#!/usr/bin/env python3
"""oracle_release_runtime_w430 - CORRECTNESS RELEASE: three precision repairs measured on the served model.

Served TriviaQA after w426 (2026-09-06 21:07): 14 right, 11 wrong. The wrong column had three
sources, each repaired here under the strictness law:

    timeline for a who/where question   "Who was the first US-born winner of golf's British Open?" was
                                        answered with a timeline of the wrong subject (a band named WINNER).
                                        A timeline is never the answer to who or where: when the strict route
                                        has no full-coverage sentence, the honest reply is a receipt.
    weak bridge                         "River Phoenix died during the making of which movie?" bridged from a
                                        first-hop sentence that covered a quarter of the question to a page
                                        about a state. The first hop must cover at least half of the question.
    word problems without math words    "How many license plates can be formed..." was answered "-9" by the
                                        document runtime. The word-problem law now also reads counting
                                        vocabulary (how many, different, combinations, arrangements, each,
                                        equal to, per, total) with at least two numbers.

Methods _c430_. Parent: the serving tip, named.
"""

from __future__ import annotations

import re
import time

from oracle_release_runtime_w264 import OracleReleaseRuntimeW264 as _Base
import oracle_release_runtime_w420 as _w420

YEAR = re.compile(r"\b(1[0-9]{3}|20[0-9]{2})\b")
TIMELINE_REPLY = re.compile(r"^(?:\[ev:[a-z_]+\]\s*)?\d{3,4}:\s")
COUNT_WORDS = ('how many', 'different', 'combinations', 'arrangements', 'each', 'equal to', 'per ', 'total', 'in how many ways', 'at least', 'at most', 'exactly')


class OracleReleaseRuntimeW430(_Base):
    """Timelines never answer who/where; bridges need a first hop that covers half the question; counting problems are word problems."""

    def _c430_word_problem(self, s):
        low = s.lower()
        nums = len(re.findall(r"\b\d+\b", s))
        hits = sum(1 for w in COUNT_WORDS if w in low)
        return len(s.split()) >= 10 and nums >= 2 and hits >= 2

    def _c426_bridge(self, q, res, t0):
        """The parent's bridge with a first-hop floor of one half (measured: a quarter admitted wrong pages)."""
        kind, noun = self._f420_type(q)
        cap = self._f420_spans(q, lower=False)
        if not cap:
            return None
        qterms = _w420._qterms(q)
        years = YEAR.findall(q)
        qlow = q.lower()
        hints = [t for t in re.findall(r"[a-z]+", qlow) if t in ('film', 'movie', 'song', 'album', 'band', 'novel', 'book', 'series', 'show', 'game', 'company', 'city', 'river', 'play', 'musician', 'actor', 'actress', 'singer', 'politician', 'footballer', 'author', 'writer')]
        best = None
        for span in cap[:4]:
            if time.time() - t0 > _w420.BUDGET_S:
                break
            first_hops = list(self._f420_pages(span)) + [(pid, rows, src) for pid, rows, src, nt in self._c426_pages_like(span, hints)[:2]]
            for pid, rows, src in first_hops:
                span_toks = _w420._toks(span)
                constraints = [t for t in qterms if t not in span_toks and t not in years and t != noun]
                for i, (cid, s) in enumerate(rows[:40]):
                    cov = self._f420_coverage(s, constraints, years)
                    if cov is None or cov < 0.5:
                        continue
                    covered = {c for c in constraints if c in _w420._toks(s)}
                    remaining = [c for c in constraints if c not in covered]
                    for m in _w420.SPAN.finditer(s):
                        bname = (m.group(1) or m.group(2) or m.group(3) or '').strip(' ,.?')
                        if len(bname) < 3 or bname.lower() in qlow or bname.lower() in _w420.QSTOP or bname.lower() == span.lower():
                            continue
                        bpid, brows, bsrc = self._c426_first_sentence(bname)
                        if not brows:
                            continue
                        title_ok = _w420._norm_title(self._f420_title(bsrc, bpid)) == _w420._norm_title(bname)
                        if not title_ok:
                            continue
                        b = self._c426_best_on_page(brows, kind, noun, q, remaining, [], bname, title_ok, floor=1.0)
                        if b and (not best or b[0] > best[0]):
                            best = (b[0], b[1], b[2], bname, bpid, bsrc, cid, s, span)
                if best and best[0] >= 1.5:
                    break
            if best and best[0] >= 1.5:
                break
        if not best:
            return None
        sc, cid2, s2, bname, bpid, bsrc, cid1, s1, span = best
        text = '%s [%s] Reached through %s: %s [%s]' % (s2, cid2, bname, s1, cid1)
        return self._c426_answer(res, text, [(cid2, s2), (cid1, s1)], {'via': 'bridge', 'first': span, 'bridge': bname, 'pages': [bpid], 'score': round(sc, 2), 'type': kind, 'first_hop_floor': 0.5}, t0)

    def chat(self, text: str, session_id: str = 'default') -> dict:
        res = super().chat(text, session_id)
        try:
            s = ' '.join(str(text).strip().split())
            if str(session_id).startswith('loop-delib-') or not isinstance(res, dict) or res.get('status') != 'answered':
                return res
            path = str(res.get('path', ''))
            body = str(res.get('response', ''))
            kind, noun = self._f420_type(s)
            t0 = time.time()
            if kind in ('who', 'where') and path.startswith(('arb:timeline', 'capability:timeline')) and TIMELINE_REPLY.match(body):
                out = self._f420_try(s, res, t0)
                if out:
                    return out
                cap = self._f420_spans(s, lower=False)
                try:
                    self._receive(s, session_id, res)
                except Exception:
                    pass
                rep = dict(res)
                rep.update({'status': 'withheld', 'path': 'factoid:withheld|vessel:receipt',
                            'response': 'I have no admitted record that answers %s about "%s", so I will not guess. A timeline of the topic is not that answer.' % ('who' if kind == 'who' else 'where', cap[0] if cap else s[:40]),
                            'references': [], 'provenance': dict(res.get('provenance') or {}, kind='factoid', factoid={'via': 'withheld', 'reason': 'timeline_for_%s' % kind}, parent_path=path)})
                return rep
            if path.startswith(('arb:', 'document_runtime', 'definitional', 'capability:')) and self._c430_word_problem(s) and '\\' not in s:
                try:
                    self._receive(s[:400], session_id, res)
                except Exception:
                    pass
                rep = dict(res)
                rep.update({'status': 'withheld', 'path': 'operator:unparsed|vessel:receipt',
                            'response': 'That is a counting problem. My exact operators read typeset and plain arithmetic, and none of them read this one whole, so I will not guess at it.',
                            'references': [], 'provenance': dict(res.get('provenance') or {}, kind='operator_unparsed', word_problem=True, parent_path=path)})
                return rep
        except Exception:
            return res
        return res
