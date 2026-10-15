#!/usr/bin/env python3
"""oracle_release_runtime_w426 - COMPOSE: answers reached by inference over two attested sentences, and from the derived store.

Ben (2026-09-06): the corpus expands through inference, not more information. Measured the
same day on HotpotQA (offset 0): the stores hold the answer to 97 of 200 questions on one of
the two supporting pages, while the served model answered 5. The missing capability is
composition: reach a second page through a sentence on the first, and read the fact there.
Under the closure and composition laws every answer here is a proof over attested claims,
cited in full, and the rule has a verifier where one exists (dates compare exactly).

    bridge      "What position was held by the woman who portrayed Corliss Archer in Kiss and Tell?"
                first hop: a page named in the question; a sentence there covering part of
                the question names a proper noun not in the question (the bridge); second
                hop: the bridge's own page, read by the strict route with the REMAINING
                constraints and the answer type; both sentences cited
    comparison  "Who was born earlier, A or B?" / "Which was founded first, A or B?"
                both pages' first sentences carry a date; the earlier is named; both cited
    both        "Are A and B both X?" -> yes only when both definitions carry X; else the
                honest answer is what each definition says, or a receipt
    derived     "How old was X when he died?" -> the derived store (m13e10, rule age_at_death)
                holds "X died aged N" with its premise claim; answered citing both

Fires only when the parent declined or withheld. Methods _c426_. Parent: the serving tip.
"""

from __future__ import annotations

import os
import re
import sqlite3
import time
from pathlib import Path

from oracle_release_runtime_w259 import OracleReleaseRuntimeW259 as _Base
import oracle_release_runtime_w420 as _w420

CMP_EARLIER = re.compile(r"^(?:who|which|what)\b.*\b(?:born|founded|established|formed|created|released|published|built|opened|started|began)\s+(?:earlier|first|later|last)\b.*?\b([A-Z][^,?]+?)\s+or\s+([A-Z][^,?]+?)\??$", re.I)
CMP_FIRST = re.compile(r"^(?:which|who)\b.*?\b(?:first|earlier|later|last|older|younger|newer)\b.*?[:,]?\s*([A-Z][^,?]+?)\s+or\s+([A-Z][^,?]+?)\??$", re.I)
BOTH = re.compile(r"^(?:are|were)\s+(.+?)\s+and\s+(.+?)\s+both\s+(.+?)\??$", re.I)
YEAR = re.compile(r"\b(1[0-9]{3}|20[0-9]{2})\b")
LATER_WORDS = ('later', 'last', 'younger', 'newer')
DERIVED_Q = re.compile(r"\bhow old\b.*\b(?:die|died|death)\b|\bhow long\b.*\b(?:last|lasted|exist|existed|run|ran)\b|\bage\b.*\b(?:die|died|death)\b", re.I)
DERIVED = Path(__import__("os").environ.get("ORACLE7_ROOT", "/opt/oracle-clm") + '/fable-content/oracle-m-series-2026-08-15/m13e10_derived_build_a_v1/derived.sqlite3')


class OracleReleaseRuntimeW426(_Base):
    """Composition over attested claims; derived facts with their premises."""

    # ---- derived store ------------------------------------------------------------------------
    def _c426_derived(self):
        if '_c426_dstore' not in self.__dict__:
            p = Path(os.environ.get('ORACLE_DERIVED_BUILD', str(DERIVED)))
            self.__dict__['_c426_dstore'] = sqlite3.connect('file:%s?mode=ro' % p, uri=True) if p.exists() else None
        return self.__dict__['_c426_dstore']

    def _c426_derived_rows(self, subject, rule=None):
        db = self._c426_derived()
        if db is None:
            return []
        try:
            q = 'SELECT derived_id, fact, rule, premise_claim_id, premise FROM derived WHERE lower(subject) = lower(?)' + (' AND rule = ?' if rule else '')
            return db.execute(q, (subject, rule) if rule else (subject,)).fetchall()[:8]
        except Exception:
            return []

    # ---- helpers --------------------------------------------------------------------------------
    def _c426_pages_like(self, name, hints=()):
        """Pages whose title begins with the span, for titles the question does not spell out in full:
        'the film Kiss and Tell' -> 'Kiss and Tell (1945 film)'. A hint word from the question (film, song,
        album, band, novel...) that appears in the title's suffix picks among several; else the shortest."""
        norm = _w420._norm_title(name)
        if len(norm) < 4:
            return []
        found = []
        for store, q in (('primary', self.bench_query), ('deep', getattr(self, '_s244_deep', None))):
            if q is None:
                continue
            try:
                rows = q.connection.execute('SELECT normalized_title, page_id FROM title_alias WHERE normalized_title LIKE ? LIMIT 24', (norm + ' %',)).fetchall()
            except Exception:
                rows = []
            for nt, pid in rows:
                suffix = nt[len(norm):].strip()
                score = 0
                for h in hints:
                    if h and h in suffix.split():
                        score += 2
                found.append((-score, len(suffix), store, pid, nt))
        found.sort()
        out = []
        for _, _, store, pid, nt in found[:4]:
            q = self.bench_query if store == 'primary' else getattr(self, '_s244_deep', None)
            try:
                rows = [(cid, ' '.join(str(f).split())) for cid, f in q.page_sentences(pid)]
            except Exception:
                rows = []
            if rows:
                out.append((pid, rows, store, nt))
        return out

    def _c426_first_sentence(self, name, hints=()):
        """The page for a name. When the question hints at a kind (film, band, song) and the exact page's
        definition does not carry it, a titled variant whose suffix does ("Freakonomics (film)") wins."""
        pages = self._f420_pages(name)
        exact = None
        for pid, rows, src in pages:
            title_ok = _w420._norm_title(self._f420_title(src, pid)) == _w420._norm_title(name)
            if rows and title_ok:
                exact = (pid, rows, src)
                break
        if exact is None and pages:
            exact = pages[0]
        if hints:
            head = ' '.join(s for _, s in (exact[1][:2] if exact else [])).lower()
            if not any(h in head for h in hints):
                for pid, rows, src, nt in self._c426_pages_like(name, hints):
                    suffix = nt[len(_w420._norm_title(name)):]
                    if any(h in suffix for h in hints):
                        return pid, rows, src
        if exact:
            return exact
        like = self._c426_pages_like(name, hints)
        if like:
            pid, rows, src, nt = like[0]
            return pid, rows, src
        return None, [], None

    @staticmethod
    def _c426_years(sentence):
        return [int(y) for y in YEAR.findall(sentence)]

    @staticmethod
    def _c426_dated_sentence(rows):
        """The sentence that dates the entity: the first of the opening five that carries a year, preferring
        one that says born / founded / established / formed / created / released / built / opened."""
        cands = [(cid, s) for cid, s in rows[:5] if YEAR.search(s)]
        for cid, s in cands:
            if re.search(r"\b(?:born|founded|established|formed|created|released|built|opened|began|started|published)\b", s, re.I):
                return cid, s
        return cands[0] if cands else (None, None)

    def _c426_best_on_page(self, rows, kind, noun, q, constraints, years, entity, title_is_entity, floor):
        """The strict route's page reader with a settable coverage floor (the second hop of a bridge is read
        with the constraints that remain after the first, and those are few)."""
        best = None
        for i, (cid, s) in enumerate(rows[:60]):
            if not self._f420_passes(kind, noun, s, q):
                continue
            cov = self._f420_coverage(s, constraints, years)
            names = self._f420_names(s, entity)
            if cov is None:
                if not (i == 0 and title_is_entity):
                    continue
                sc = 1.0
            else:
                if cov < floor or (names == 0 and not title_is_entity):
                    continue
                sc = cov + 0.25 * names + (0.1 if i == 0 else 0.0)
            if not best or sc > best[0]:
                best = (sc, cid, s, round(cov, 2) if cov is not None else None)
        return best

    @staticmethod
    def _c426_head_nouns(sentence):
        """Candidate kind words in a definition: agentive nouns (singer, guitarist, composer, actor, politician)
        in the clause after 'is/was a(n)', up to the first period or 'who'; at most three, nearest first."""
        m = re.search(r"\b(?:is|was|are|were)\s+(?:an?|the)\s+(.{3,160}?)(?:\.|\bwho\b|\bthat\b|\bbest known\b|$)", sentence)
        if not m:
            return []
        words = [w.strip('-') for w in re.findall(r"[a-z][a-z\-]{3,}", m.group(1).lower())]
        agent = [w for w in words if w.endswith(('er', 'or', 'ist', 'ian', 'ant', 'ent', 'man', 'woman', 'ee', 'eur')) and w not in _w420.QSTOP
                 and w not in ('former', 'other', 'later', 'earlier', 'better', 'member', 'american', 'german', 'italian', 'canadian', 'russian', 'australian', 'indian', 'mexican', 'brazilian')]
        seen, out = set(), []
        for w in agent:
            if w not in seen:
                seen.add(w)
                out.append(w)
        return out[:3]

    def _c426_isa(self, kind_word, what):
        """Ask the chain itself: 'Is a singer a musician?' A cited Yes is the step; anything else is no step."""
        try:
            r = super().chat('Is a %s a %s?' % (kind_word, what.rstrip('s')), session_id='loop-delib-compose-isa')
        except Exception:
            return None
        body = re.sub(r"^\[ev:[a-z_]+\]\s*", '', ' '.join(str(r.get('response', '')).split()))
        if r.get('status') == 'answered' and body.startswith('Yes'):
            refs = r.get('references') or []
            cid = refs[0].get('id') if refs and isinstance(refs[0], dict) else str(r.get('path', ''))[:40]
            return (body[:140], cid)
        return None

    def _c426_answer(self, res, text, refs, prov, t0):
        out = dict(res)
        out.update({'status': 'answered', 'path': 'compose:%s' % prov.get('via', 'bridge'), 'response': '[ev:derived] ' + text,
                    'references': [{'id': cid, 'text': s} for cid, s in refs],
                    'provenance': dict(res.get('provenance') or {}, kind='compose', compose=prov, ms=int((time.time() - t0) * 1000), parent_path=str(res.get('path', '')))})
        return out

    # ---- comparison -----------------------------------------------------------------------------
    def _c426_compare(self, q, res, t0):
        m = CMP_EARLIER.match(q) or CMP_FIRST.match(q)
        if not m:
            return None
        a, b = m.group(1).strip(' ,.?'), m.group(2).strip(' ,.?')
        later = any(w in q.lower() for w in LATER_WORDS)
        hints = [t for t in re.findall(r"[a-z]+", q.lower()) if t in ('film', 'movie', 'song', 'album', 'band', 'novel', 'book', 'magazine', 'company', 'university', 'city', 'series')]
        pa, ra, sa = self._c426_first_sentence(a, hints)
        pb, rb, sb = self._c426_first_sentence(b, hints)
        if not ra or not rb:
            return None
        ca, sa_ = self._c426_dated_sentence(ra)
        cb, sb_ = self._c426_dated_sentence(rb)
        if not sa_ or not sb_:
            return None
        fa, fb = self._c426_years(sa_)[0], self._c426_years(sb_)[0]
        if fa == fb:
            return None
        win_a = (fa > fb) if later else (fa < fb)
        win, wy, lose, ly = (a, fa, b, fb) if win_a else (b, fb, a, fa)
        text = '%s (%d) %s %s (%d), by %d years. From: %s [%s] and %s [%s]' % (
            win, wy, 'comes after' if later else 'comes before', lose, ly, abs(fa - fb), sa_, ca, sb_, cb)
        return self._c426_answer(res, text, [(ca, sa_), (cb, sb_)],
                                 {'via': 'comparison', 'a': a, 'b': b, 'years': [fa, fb], 'rule': 'later' if later else 'earlier', 'pages': [pa, pb]}, t0)

    def _c426_both(self, q, res, t0):
        m = BOTH.match(q)
        if not m:
            return None
        a, b, what = m.group(1).strip(), m.group(2).strip(), m.group(3).strip(' ?.')
        terms = [t for t in _w420._qterms(what) if t]
        if not terms:
            return None
        hints = [t for t in re.findall(r"[a-z]+", what.lower()) if t in ('film', 'films', 'movie', 'movies', 'documentaries', 'documentary', 'song', 'songs', 'album', 'albums', 'band', 'bands', 'novel', 'novels', 'book', 'books', 'magazine', 'magazines', 'company', 'companies', 'series', 'game', 'games')]
        hints = [h.rstrip('s') if h.endswith('s') and not h.endswith('ss') else h for h in hints]
        hints = ['documentary' if h == 'documentarie' else h for h in hints]
        # a documentary is a film; a band a group: the title suffix says the broader kind
        if 'documentary' in hints:
            hints += ['film']
        if 'band' in hints:
            hints += ['group', 'musician']
        pa, ra, sa = self._c426_first_sentence(a, hints)
        pb, rb, sb = self._c426_first_sentence(b, hints)
        if not ra or not rb:
            return None
        ta, tb = _w420._toks(ra[0][1]), _w420._toks(rb[0][1])
        ha, hb = all(t in ta for t in terms), all(t in tb for t in terms)
        # composition with the chain's own kind reasoner: "singer" IS-A "musician" makes a definition that
        # says singer carry "musician"; each step is the chain's cited yes, never this fold's word
        via = {}
        if not (ha and hb) and len(terms) == 1:
            kind_word = terms[0]
            for tag, held, sent in (('a', ha, ra[0][1]), ('b', hb, rb[0][1])):
                if held:
                    continue
                for cand in self._c426_head_nouns(sent):
                    ans = self._c426_isa(cand, what)
                    if ans:
                        via[tag] = (cand, ans)
                        break
            ha = ha or 'a' in via
            hb = hb or 'b' in via
        if ha and hb:
            steps = ''.join(' (%s is a %s: %s [%s])' % (v[0], what.rstrip('s'), v[1][0], v[1][1]) for v in via.values())
            text = 'Yes. Both definitions carry "%s"%s: %s [%s] and %s [%s]' % (what, steps, ra[0][1], ra[0][0], rb[0][1], rb[0][0])
        elif ha or hb:
            yes, no, ry, rn = (a, b, ra, rb) if ha else (b, a, rb, ra)
            text = 'Not both, on the record: %s is described as %s [%s], while the record for %s says: %s [%s]' % (yes, what, ry[0][0], no, rn[0][1], rn[0][0])
        else:
            return None
        return self._c426_answer(res, text, [(ra[0][0], ra[0][1]), (rb[0][0], rb[0][1])], {'via': 'both', 'a': a, 'b': b, 'what': what, 'held': [ha, hb]}, t0)

    # ---- derived facts ----------------------------------------------------------------------------
    def _c426_from_derived(self, q, res, t0):
        if not DERIVED_Q.search(q):
            return None
        rule = 'age_at_death' if re.search(r"\b(?:die|died|death|old|age)\b", q, re.I) else 'duration'
        for span in self._f420_spans(q, lower=False):
            rows = self._c426_derived_rows(span, rule)
            if rows:
                did, fact, rl, pcid, premise = rows[0]
                text = '%s Derived by %s from: %s [%s]' % (fact, rl, premise, pcid)
                return self._c426_answer(res, text, [(did, fact), (pcid, premise)], {'via': 'derived', 'rule': rl, 'subject': span, 'derived_id': did}, t0)
        return None

    # ---- bridge -------------------------------------------------------------------------------------
    def _c426_bridge(self, q, res, t0):
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
                    if cov is None or cov < 0.25:
                        continue
                    covered = {c for c in constraints if c in _w420._toks(s)}
                    remaining = [c for c in constraints if c not in covered]
                    # bridge candidates: proper nouns in this sentence that the question did not name
                    for m in _w420.SPAN.finditer(s):
                        bname = (m.group(1) or m.group(2) or m.group(3) or '').strip(' ,.?')
                        if len(bname) < 3 or bname.lower() in qlow or bname.lower() in _w420.QSTOP or bname.lower() == span.lower():
                            continue
                        bpid, brows, bsrc = self._c426_first_sentence(bname)
                        if not brows:
                            continue
                        title_ok = _w420._norm_title(self._f420_title(bsrc, bpid)) == _w420._norm_title(bname)
                        # the second hop is read under the strictness law: every remaining constraint, or nothing
                        # (a 0.5 floor measured 6 right / 10 wrong on HotpotQA; comparison and both-forms were 8 / 0)
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
        return self._c426_answer(res, text, [(cid2, s2), (cid1, s1)], {'via': 'bridge', 'first': span, 'bridge': bname, 'pages': [bpid], 'score': round(sc, 2), 'type': kind}, t0)

    def chat(self, text: str, session_id: str = 'default') -> dict:
        res = super().chat(text, session_id)
        try:
            s = ' '.join(str(text).strip().split())
            if str(session_id).startswith('loop-delib-'):
                return res
            path = str(res.get('path', ''))
            declined = self._f420_declined(res) or path.startswith(('factoid:withheld', 'subject:function_word', 'operator:unparsed'))
            typed = bool(CMP_EARLIER.match(s) or CMP_FIRST.match(s) or BOTH.match(s))
            # an exact comparison outranks a dump route (a timeline of one entity is not "who was born first")
            dumped = typed and path.startswith(_w420.DUMP_PATHS)
            if not declined and not dumped:
                return res
            if _w420.SELF_Q.search(s) or _w420._numbers(s) >= 3:
                return res
            t0 = time.time()
            # a comparison or a both-form that its own rule could not settle stays a receipt: the bridge is
            # for questions that name one thing and ask about another, never a fallback for these
            fns = (self._c426_compare, self._c426_both, self._c426_from_derived) if typed else (self._c426_from_derived, self._c426_bridge)
            for fn in fns:
                out = fn(s, res, t0)
                if out:
                    return out
                if time.time() - t0 > _w420.BUDGET_S:
                    break
        except Exception as e:  # noqa: BLE001
            try:
                out = dict(res)
                out['provenance'] = dict(res.get('provenance') or {}, compose_error=repr(e)[:160])
                return out
            except Exception:
                return res
        return res
