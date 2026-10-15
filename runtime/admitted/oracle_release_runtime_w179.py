#!/usr/bin/env python3
"""oracle_release_runtime_w179 - reach: two routes that were declining or
substituting although the record held the page (charter fable_reach F2, F5).

F5  ADMITTED PAGE OUTRANKS THE GLOSS. "what is truth" was answered by the
    dictionary route ("Truth is defined as a fact that has been verified [W1]")
    while a thirty-two-sentence admitted page opened with a genus-form lead.
    The arbiter redispatches only when the gloss route FAILS, so a gloss that
    answers pre-empts depth. Here: when the base answered from the gloss route
    (or substituted) and the question is definitional, the definitional route
    is tried on the canonical surface "What is <term>?"; if it answers from an
    admitted page, that answer is released and the path says why.

F2  RELATION QUESTIONS. "what is the relation between X and Y" and "how does X
    relate to Y" fell to clarify. They are compare questions in another
    surface; they are redispatched to the compare capability's canonical
    surface and labeled relation->compare. No new knowledge is claimed; the
    compare route's own citations carry the answer, or it declines.

Both keep every law: cite or decline, one page per title, no writes to the
record. Parent: the serving tip, named.
"""

from __future__ import annotations

import importlib
import re

from oracle_release_runtime_w175 import OracleReleaseRuntimeW175 as _Base

_an_mod = importlib.import_module('oracle_release_runtime_an')
_content_terms = _an_mod.content_terms
CITE_RX = _an_mod.CITE

DEF_Q = re.compile(r"^what\s+(?:is|are)\s+(?:an?\s+|the\s+)?(?P<term>[\w][\w \-']{1,60}?)\s*\??$", re.I)
REL_Q = re.compile(
    r"^(?:what\s+is\s+the\s+relation(?:ship)?\s+between\s+(?P<a>[\w][\w \-']{1,50}?)\s+and\s+(?P<b>[\w][\w \-']{1,50}?)"
    r"|how\s+(?:does|do|is|are)\s+(?P<c>[\w][\w \-']{1,50}?)\s+relat(?:e|ed)\s+to\s+(?P<d>[\w][\w \-']{1,50}?)"
    r"|how\s+(?:does|do)\s+(?P<e>[\w][\w \-']{1,50}?)\s+connect\s+(?:to|with)\s+(?P<f>[\w][\w \-']{1,50}?))\s*\??$", re.I)
GLOSS_PATHS = ('document_runtime',)


class OracleReleaseRuntimeW179(_Base):
    """Reach: admitted page over gloss (F5); relation questions to compare (F2).

    Also a correction to w175 found the same day: the gate's measurement sessions
    (ids starting with 'loop-') were writing into the LIVE vessel store every cycle,
    inflating held-out shapes. Measurement sessions now use an in-memory store, so
    within-session reception still works for them and the live register holds only
    what people and the stimuli organ asked."""

    _MEASURE_PREFIX = ('loop-',)

    def _measuring(self) -> bool:
        return bool(getattr(self, '_vessel_mem_mode', False))

    def _vessels_load(self) -> dict:
        if self._measuring():
            mem = getattr(self, '_vessel_mem', None)
            if mem is None:
                mem = self._vessel_mem = {'next': 1, 'by_key': {}}
            return mem
        return super()._vessels_load()

    def _vessels_save(self, store: dict) -> None:
        if self._measuring():
            self._vessel_mem = store
            return
        super()._vessels_save(store)

    def _event(self, kind: str, **kw) -> None:  # type: ignore[override]
        if self._measuring():
            return
        _Base._event(kind, **kw)

    @staticmethod
    def _an_terms(s: str):
        return _content_terms(s)

    def _rel_pair(self, s: str):
        m = REL_Q.match(s)
        if not m:
            return None
        g = m.groupdict()
        for x, y in (('a', 'b'), ('c', 'd'), ('e', 'f')):
            if g.get(x) and g.get(y):
                return g[x].strip(), g[y].strip()
        return None

    def chat(self, text: str, session_id: str = 'default') -> dict:
        # measurement sessions (the gate's) never touch the live vessel store
        self._vessel_mem_mode = str(session_id).startswith(self._MEASURE_PREFIX)
        s = ' '.join(str(text).strip().split())
        pair = self._rel_pair(s)
        if pair:
            a, b = pair
            canon = 'Compare %s and %s.' % (a, b)
            result = super().chat(canon, session_id)
            # a redispatch must EARN its place: only a cited compare answer replaces the base's
            # own behaviour on the original surface; a withheld or uncited compare falls through
            if result.get('status') == 'answered' and len(CITE_RX.findall(str(result.get('response', '')))) > 0:
                result = dict(result)
                result['path'] = 'relation->' + str(result.get('path', ''))
                prov = dict(result.get('provenance') or {})
                prov['relation_surface'] = s[:120]
                result['provenance'] = prov
                # the witness must record the turn the PERSON made, not the canonical surface:
                # original surface, a typed reading, and the terms carried from the prior turn
                try:
                    q = self._paths.get(session_id)
                    if q and len(q):
                        rec = q[-1]
                        rec['in_surface'] = s[:120]
                        rec['in_form'] = list(rec.get('in_form') or []) + ['relation_question']
                        rec['operator'] = result['path']
                        in_terms = set(self._an_terms(s))
                        prior = q[-2] if len(q) > 1 else None
                        if prior:
                            prior_terms = set(prior.get('in_terms') or []) | set(prior.get('out_terms') or [])
                            carried = sorted(in_terms & prior_terms)
                            if carried:
                                rec['carried_from_prior'] = sorted(set(rec.get('carried_from_prior') or []) | set(carried))
                                rec['continuity'] = True
                        rec['in_terms'] = sorted(in_terms)
                        self._recite(rec, s, str(result.get('response', '')))
                except Exception:
                    pass
                return result
            # compare could not carry it: fall through to the base on the original surface
        result = super().chat(s, session_id)
        path = str(result.get('path', ''))
        m = DEF_Q.match(s)
        if m and result.get('status') == 'answered' and (
                any(p in path for p in GLOSS_PATHS) or 'substitution_disclosed' in path):
            term = m.group('term').strip()
            try:
                alt = self._definitional_turn('What is %s?' % term)
            except Exception:
                alt = None
            if not alt or alt.get('status') != 'answered':
                try:
                    alt = self._definitional_turn('What is a %s?' % term)
                except Exception:
                    alt = None
            if alt and alt.get('status') == 'answered' and str(alt.get('response', '')).strip():
                alt = dict(alt)
                alt['path'] = str(alt.get('path', 'definitional_encyclopedic')) + '|over_gloss'
                prov = dict(alt.get('provenance') or {})
                prov['displaced'] = {'path': path, 'response': str(result.get('response', ''))[:140]}
                alt['provenance'] = prov
                alt['latency_ms'] = result.get('latency_ms')
                # keep the witness honest: the base recorded the gloss turn; amend its operator and text
                try:
                    q = self._paths.get(session_id)
                    if q and len(q) and q[-1].get('in_surface', '')[:60] == s[:60]:
                        rec = q[-1]
                        rec['operator'] = alt['path']
                        self._recite(rec, s, str(alt['response']))
                except Exception:
                    pass
                return alt
        return result
