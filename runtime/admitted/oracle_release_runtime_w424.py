#!/usr/bin/env python3
"""oracle_release_runtime_w424 - CORRECTNESS RELEASE: the definition form must start with a capital.

Defect found on the served model (2026-09-06, SimpleQA against :8097 after w420 was admitted):
the factoid route's DEFINITION_FORM pattern was compiled case-insensitively, so its clause
"what is (a|an|the) <Capital>" matched "What is the name of the statue that Rosemarie
Trockel made..." and "What is the length in meters of Abdullah Bridge..." - and the route
answered with the entity's DEFINITION (first sentence of its page), which carries none of
what was asked. 22 of 26 wrong SimpleQA answers on the served model were this one defect.

This fold re-reads the question with the corrected form (the capital is a capital) and
otherwise runs the parent's factoid route unchanged: `_f420_try` is overridden to compute
`definition` strictly and then delegate the page and full-text search to the parent's own
helpers. Methods _c424_. Parent: the serving tip, named.
"""

from __future__ import annotations

import re
import time

from oracle_release_runtime_w422 import OracleReleaseRuntimeW422 as _Base
import oracle_release_runtime_w420 as _w420

DEFINITION_WORDS = re.compile(r"\b(?:profession|occupation|nationality|genre)\b", re.I)
DEFINITION_WHAT = re.compile(r"^[Ww]hat (?:is|was) (?:a |an |the )?[A-Z]")
DEFINITION_SHORT = re.compile(r"^[Ww]hat (?:is|was|are|were) (?:a |an |the )?[\w'\-]+(?:\s+[\w'\-]+){0,3}\??$")
DEFINITION_MAX_WORDS = 7
# "the GPS coordinates of Malawi", "the capital of France": an attribute OF a proper noun is not a definition
ATTRIBUTE_OF = re.compile(r"\b(?:of|in|at|from|by|for)\s+(?:the\s+)?[A-Z]")


class OracleReleaseRuntimeW424(_Base):
    """The definition form applies to 'What is <Proper Noun>', to a short 'what is a <thing>' (at most seven
    words: "what is a moynat trunk for"), and to profession/nationality questions; never to a long question
    that names an attribute of the entity ("What is the name of the statue that Rosemarie Trockel made")."""

    @staticmethod
    def _c424_definition(q):
        s = q.strip()
        if DEFINITION_WORDS.search(s) or DEFINITION_WHAT.match(s):
            return True
        return len(s.split()) <= DEFINITION_MAX_WORDS and bool(DEFINITION_SHORT.match(s)) and not ATTRIBUTE_OF.search(s)

    def _f420_try(self, q, res, t0, avoid=()):
        years = _w420.YEAR.findall(q)
        spans = self._f420_spans(q)
        if not spans:
            return None
        kind, noun = self._f420_type(q)
        qterms = _w420._qterms(q)
        definition = self._c424_definition(q)
        best = None
        for span in spans:
            if time.time() - t0 > _w420.BUDGET_S:
                break
            for pid, rows, src in self._f420_pages(span):
                title_is_entity = _w420._norm_title(self._f420_title(src, pid)) == _w420._norm_title(span)
                span_toks = _w420._toks(span)
                constraints = [t for t in qterms if t not in span_toks and t not in years and t != noun]
                b = self._f420_best_on_page(rows, kind, noun, q, constraints, years, span, title_is_entity, definition and title_is_entity, avoid=avoid)
                if b and (not best or b[0] > best[0]):
                    best = b + (span, pid, src)
            if best and best[0] >= 1.5:
                break
        if best:
            sc, cid, s, cov, span, pid, src = best
            return self._f420_answer(res, s, cid, {'entity': span, 'page': pid, 'store': src, 'score': round(sc, 2), 'coverage': cov, 'type': kind, 'via': 'page',
                                                   'definition_form': definition, 'corrected_by': 'w424'}, t0)
        if time.time() - t0 > _w420.BUDGET_S:
            return None
        deep = getattr(self, '_s244_deep', None)
        cap = self._f420_spans(q, lower=False)
        if deep is not None and cap:
            ent = cap[0]
            constraints = [t for t in qterms if t not in _w420._toks(ent) and t not in years and t != noun]
            if not constraints and not years:
                return None
            hits = self._f420_fts([ent] + constraints[:6] + years, limit=8)
            cands = []
            for cid, s in hits:
                s = ' '.join(str(s).split())
                cov = self._f420_coverage(s, constraints, years)
                subject = ent.lower() in s[:60].lower()
                if cov is not None and cov >= _w420.FULL and subject and self._f420_passes(kind, noun, s, q):
                    cands.append((cov, cid, s))
            cands.sort(reverse=True)
            if cands:
                cov, cid, s = cands[0]
                return self._f420_answer(res, s, cid, {'entity': ent, 'page': None, 'store': 'deep_fts', 'score': round(cov + 0.5, 2), 'coverage': round(cov, 2), 'type': kind,
                                                       'via': 'fts', 'corrected_by': 'w424'}, t0)
        return None
