#!/usr/bin/env python3
"""oracle_release_runtime_w400 - DELIBERATION RECOVERIES: the burst behind a declined follow-up.

The fresh six-conversation test of 2026-09-06 found the first turn right every time and
the follow-through failing on typed forms the runtime does not hold. An answer costs
25 ms, so a declined turn can afford a burst of self-questions before it gives up. This
fold adds the recoveries the record already supports, each warranted by the same
sentences and citations as every other route, and each provenance-tagged as a
deliberation:

    made_of        "What is it made of?" -> the topic's own page sentences that carry a
                   composition marker (ingredients, made of, consists of ...), primary
                   store first, then the deep store
    where          "Where is it eaten / found / used?" -> the page sentence carrying the
                   verb, or a place marker
    genus_or       "Is that a dumpling or a bread?" -> the lead sentence decides
    session        "Summarize what you told me." -> the claims this session actually told,
                   from the selection state (w191), numbered and cited
    causal_yes_no  "Does that mean weight causes gravity?" -> the TYPED edge table: yes
                   with the attesting claim, no with the reverse claim, or 'not attested
                   in either direction' (open-world law: not attested is not false)
    verify         "Correct me if I am wrong: <claim>" -> the page sentence that agrees,
                   or the nearest one when it does not, never a bare yes

Referents (it, that, this) resolve to the session's current topic, which this fold
tracks from every turn's provenance. A recovery fires only when the parent declined;
answered turns are untouched. Nothing is asserted without a cited sentence, and the
absence of a relation is reported as absence. Methods _d400_. Parent: the serving tip, named.
"""

from __future__ import annotations

import importlib
import os
import re
import sqlite3
import time
from pathlib import Path

from oracle_release_runtime_w253 import OracleReleaseRuntimeW253 as _Base

_w181 = importlib.import_module('oracle_release_runtime_w181')
_strip_prefix, CITE_RX = _w181._strip_prefix, _w181.CITE_RX
_an = importlib.import_module('oracle_release_runtime_an')
_content_terms = _an.content_terms

REF = r"(?:it|that|this|they|them|those|these)"
MADE = re.compile(r"^what (?:is|are) (?:" + REF + r"|(?:a |an |the )?(?P<x>[\w \-']{2,50}?)) made (?:of|from|out of)\??$", re.I)
INGR = re.compile(r"^what (?:is|are) the (?:ingredients|parts|components|materials) (?:of|in) (?:" + REF + r"|(?:a |an |the )?(?P<x>[\w \-']{2,50}?))\??$", re.I)
WHERE = re.compile(r"^where (?:is|are|was|were|do|does|did|can) (?:" + REF + r"|(?:a |an |the )?(?P<x>[\w \-']{2,40}?))\s+(?P<v>[a-z]+)\??$", re.I)
GENUS_OR = re.compile(r"^is (?:" + REF + r"|(?:a |an |the )?(?P<x>[\w \-']{2,40}?)) (?:a |an )?(?P<a>[\w\-']{2,30}) or (?:a |an )?(?P<b>[\w\-']{2,30})\??$", re.I)
SUMMARY = re.compile(r"^(?:summari[sz]e|recap|sum up|repeat)\s+(?:what you(?:'ve| have)? (?:told|said|taught)(?: to)? me|what we(?:'ve| have)? (?:said|discussed|covered|talked about)|this conversation|our conversation|so far|everything so far)\.?$", re.I)
CAUSAL_YN = re.compile(r"^(?:does that mean (?:that )?|so |is it true that |does |do |can |could )?(?P<x>[\w \-']{2,40}?)\s+causes?\s+(?P<y>[\w \-']{2,40}?)\s*(?:then)?\??$", re.I)
CORRECT = re.compile(r"^(?:correct me if i(?:'m| am) wrong[:,]?|is it (?:right|true|correct|accurate) that|am i right that|am i correct that|is it the case that)\s+(?P<claim>.{8,220}?)[.?]*$", re.I)
WHAT_IS = re.compile(r"^(?:what|who) (?:is|are|was|were) (?:a |an |the )?(?P<x>[\w][\w \-'.]{1,60}?)\s*[?.!]*$", re.I)
MADE_MARK = re.compile(r"\b(ingredients?|made (?:of|from|out of|with)|consists? of|composed of|comprises?|made up of|contains?|containing|includes?|built (?:of|from)|formed (?:of|from))\b", re.I)
PLACE_MARK = re.compile(r"\b(in|across|throughout|native to|found in|common in|popular in|eaten in|used in|cuisines?|countr(?:y|ies)|regions?)\b", re.I)


class OracleReleaseRuntimeW400(_Base):
    """Deliberation recoveries behind declined follow-ups."""

    _d400_topic = None   # session -> current topic
    _d400_said = None    # session -> [(claim_id, sentence)]

    # ---------------------------------------------------------------- session memory
    def _d400_mem(self):
        if self._d400_topic is None:
            self._d400_topic, self._d400_said = {}, {}
        return self._d400_topic, self._d400_said

    def _d400_note(self, session_id, text, res):
        topics, said = self._d400_mem()
        prov = res.get('provenance') or {} if isinstance(res, dict) else {}
        t = prov.get('topic')
        if not t:
            m = WHAT_IS.match(' '.join(str(text).split()))
            if m and res.get('status') == 'answered':
                t = m.group('x').strip().rstrip('?.!')
        if t:
            topics[session_id] = str(t).strip().lower()
        if isinstance(res, dict) and res.get('status') == 'answered':
            body = _strip_prefix(str(res.get('response', '')))
            lst = said.setdefault(session_id, [])
            for sent, cid in re.findall(r"([^\[\]]{12,240}?)\s*\[([a-z0-9_]+:?[a-z0-9_.\-]*)\]", body, re.I):
                s = re.sub(r"^\s*(?:\d+\.\s*)?", '', ' '.join(sent.split()))
                if cid not in {c for _, c in lst} and len(s.split()) >= 4:
                    lst.append((cid, s.strip()))
            if len(lst) > 40:
                del lst[:-40]

    # ---------------------------------------------------------------- page access, primary then deep
    def _d400_page(self, x):
        pid = None
        try:
            pid = self.bench_query.page_id(x) or self.bench_query.page_id(x.title()) or self.bench_query.page_id(x.lower())
            if pid:
                rows = [(cid, ' '.join(str(f).split())) for cid, f in self.bench_query.page_sentences(pid)]
                if rows:
                    return pid, rows, 'primary'
        except Exception:
            pass
        try:
            pid2, rows = self._s244_lookup(x)
            if pid2 and rows:
                deep = self._s244_deep
                rows = [(cid, ' '.join(str(f).split())) for cid, f in deep.page_sentences(pid2)]
                return pid2, rows, 'deep'
        except Exception:
            pass
        return None, [], None

    @staticmethod
    def _d400_answer(res, path, body, refs, turns, t0):
        out = dict(res)
        out.update({'status': 'answered', 'path': path, 'response': '[ev:direct] ' + body,
                    'references': [{'id': cid, 'text': s} for cid, s in refs],
                    'provenance': dict(res.get('provenance') or {}, kind='deliberation', deliberation={'turns': turns, 'ms': int((time.time() - t0) * 1000)},
                                       declined_as=str(res.get('path', '')))})
        return out

    # ---------------------------------------------------------------- recoveries
    def _d400_made_of(self, x, res, t0):
        pid, rows, src = self._d400_page(x)
        hits = [(cid, s) for cid, s in rows if MADE_MARK.search(s)][:2]
        if not hits:
            return None
        body = ' '.join('%s [%s]' % (s, cid) for cid, s in hits)
        return self._d400_answer(res, 'deliberation:made_of', body, hits, 1 + len(rows) // 8, t0)

    def _d400_where(self, x, verb, res, t0):
        pid, rows, src = self._d400_page(x)
        stem = verb.lower().rstrip('s')[:5]
        hits = [(cid, s) for cid, s in rows if stem in s.lower() and PLACE_MARK.search(s)] or [(cid, s) for cid, s in rows if PLACE_MARK.search(s)]
        if not hits:
            return None
        cid, s = hits[0]
        return self._d400_answer(res, 'deliberation:where', '%s [%s]' % (s, cid), [(cid, s)], 1 + len(rows) // 8, t0)

    def _d400_genus_or(self, x, a, b, res, t0):
        pid, rows, src = self._d400_page(x)
        if not rows:
            return None
        cid, lead = rows[0]
        low = lead.lower()
        pick = a if a.lower() in low else (b if b.lower() in low else None)
        if not pick:
            return None
        return self._d400_answer(res, 'deliberation:genus', '%s [%s] So the record has it as a %s.' % (lead, cid, pick), [(cid, lead)], 2, t0)

    def _d400_session_summary(self, session_id, res, t0):
        _, said = self._d400_mem()
        lst = said.get(session_id) or []
        try:
            told = self._s187_state(session_id).get('told') or set()
        except Exception:
            told = set()
        items = [(cid, s) for cid, s in lst if not told or cid in told] or lst
        if not items:
            body = 'I have told you nothing with a citation in this session yet, so there is nothing to summarize.'
            out = dict(res)
            out.update({'status': 'answered', 'path': 'deliberation:session_summary', 'response': body, 'references': [],
                        'provenance': dict(res.get('provenance') or {}, kind='deliberation', told=0)})
            return out
        items = items[-6:]
        body = 'So far in this session I told you: ' + ' '.join('%d. %s [%s]' % (i + 1, s, cid) for i, (cid, s) in enumerate(items))
        return self._d400_answer(res, 'deliberation:session_summary', body, items, len(items), t0)

    def _d400_edges(self):
        deep = os.environ.get('ORACLE_DEEP_BUILD')
        p = Path(deep).parent / 'edges.sqlite' if deep else None
        return p if p and p.exists() else None

    def _d400_causal(self, x, y, res, t0):
        """Does X cause Y? Typed edges only: caused_by on Y's page pointing at X, or causes on X's page pointing at Y."""
        edges = self._d400_edges()
        deep = getattr(self, '_s244_deep', None)
        if not edges or deep is None:
            return None
        px = deep.page_id(x) or deep.page_id(x.title())
        py = deep.page_id(y) or deep.page_id(y.title())
        if not px or not py:
            return None
        con = sqlite3.connect('file:%s?mode=ro' % edges, uri=True)
        cols = [r[1] for r in con.execute('pragma table_info(edge)')]
        if 'rel' not in cols:
            con.close()
            return None
        fwd = con.execute("select claim_id from edge where ((src=? and dst=? and rel='caused_by') or (src=? and dst=? and rel='causes')) limit 1", (py, px, px, py)).fetchone()
        rev = con.execute("select claim_id from edge where ((src=? and dst=? and rel='caused_by') or (src=? and dst=? and rel='causes')) limit 1", (px, py, py, px)).fetchone()
        con.close()

        def sent(cid):
            try:
                row = deep.connection.execute('select fact from source_rows where claim_id=? limit 1', (cid,)).fetchone()
                return ' '.join(str(row[0]).split()) if row else ''
            except Exception:
                return ''
        if fwd:
            s = sent(fwd[0])
            return self._d400_answer(res, 'deliberation:causal_yes', 'Yes, the record attests it: %s [%s]' % (s, fwd[0]), [(fwd[0], s)], 3, t0)
        if rev:
            s = sent(rev[0])
            return self._d400_answer(res, 'deliberation:causal_no', 'No. The record attests the reverse: %s [%s]' % (s, rev[0]), [(rev[0], s)], 3, t0)
        out = dict(res)
        out.update({'status': 'withheld', 'path': 'deliberation:causal_unattested',
                    'response': 'The record does not attest a causal relation between %s and %s in either direction; not attested is not the same as false.' % (x, y),
                    'provenance': dict(res.get('provenance') or {}, kind='deliberation', checked=['caused_by', 'causes'], pages=[px, py])})
        return out

    def _d400_verify(self, claim, session_id, res, t0):
        topics, _ = self._d400_mem()
        subj = None
        m = re.match(r"^(?:the |a |an )?(?P<s>[\w \-']{2,40}?)\s+(?:is|are|was|were|has|have|causes?|means?)\b", claim, re.I)
        if m:
            subj = m.group('s').strip()
        cands = [c for c in (subj, topics.get(session_id)) if c]
        want = set(_content_terms(claim))
        best, best_ov = None, 0.0
        for c in cands:
            pid, rows, src = self._d400_page(c)
            for cid, s in rows[:24]:
                have = set(_content_terms(s))
                ov = len(want & have) / max(1, len(want))
                if ov > best_ov:
                    best, best_ov = (cid, s), ov
        if not best:
            return None
        cid, s = best
        if best_ov >= 0.6:
            body = 'That agrees with the record: %s [%s]' % (s, cid)
            return self._d400_answer(res, 'deliberation:verify_agrees', body, [(cid, s)], 2, t0)
        if best_ov >= 0.3:
            body = 'The record does not attest that as stated. The nearest it says: %s [%s]' % (s, cid)
            return self._d400_answer(res, 'deliberation:verify_nearest', body, [(cid, s)], 2, t0)
        return None

    # ---------------------------------------------------------------- the turn
    def chat(self, text: str, session_id: str = 'default') -> dict:
        res = super().chat(text, session_id)
        s = ' '.join(str(text).strip().split())
        try:
            self._d400_note(session_id, s, res)
            topics, _ = self._d400_mem()
            topic = topics.get(session_id)
            # a causal yes-or-no that the parent "answered" with a page summary is not answered: the typed
            # edge table decides when it can; when it cannot, the parent's answer stands (nothing is lost)
            mc = CAUSAL_YN.match(s)
            if mc and isinstance(res, dict) and res.get('status') == 'answered' and 'summarize' in str(res.get('path', '')):
                x = mc.group('x').strip().lower()
                y = mc.group('y').strip().lower()
                x = topic if x in ('it', 'that', 'this') and topic else x
                y = topic if y in ('it', 'that', 'this') and topic else y
                out = self._d400_causal(x, y, res, time.time())
                if out and out.get('status') == 'answered':
                    return out
                return res
            if not self._s244_declined(res) or str(session_id).startswith('loop-delib-'):
                return res
            t0 = time.time()

            def pick(g):
                return (g or '').strip().rstrip('?.!') or topic

            m = SUMMARY.match(s)
            if m:
                return self._d400_session_summary(session_id, res, t0)
            m = MADE.match(s) or INGR.match(s)
            if m:
                x = pick(m.group('x'))
                out = self._d400_made_of(x, res, t0) if x else None
                if out:
                    return out
            m = GENUS_OR.match(s)
            if m:
                x = pick(m.group('x'))
                out = self._d400_genus_or(x, m.group('a'), m.group('b'), res, t0) if x else None
                if out:
                    return out
            m = WHERE.match(s)
            if m:
                x = pick(m.group('x'))
                out = self._d400_where(x, m.group('v'), res, t0) if x else None
                if out:
                    return out
            m = CORRECT.match(s)
            if m:
                out = self._d400_verify(m.group('claim'), session_id, res, t0)
                if out:
                    return out
            m = CAUSAL_YN.match(s)
            if m:
                x = m.group('x').strip().lower()
                y = m.group('y').strip().lower()
                if x in ('it', 'that', 'this') and topic:
                    x = topic
                if y in ('it', 'that', 'this') and topic:
                    y = topic
                out = self._d400_causal(x, y, res, t0)
                if out:
                    return out
        except Exception:
            return res
        return res
