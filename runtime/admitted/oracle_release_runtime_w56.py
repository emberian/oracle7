#!/usr/bin/env python3
"""oracle_release_runtime_w56 - CORRECTNESS RELEASE: a deduction fold that lets go.

Found by testing the live endpoint rather than the panel, which is the only place
it could have been found. Every panel item states its premises and asks its
question in one surface, so the fold was never observed holding premises across a
CHANGE OF SUBJECT. A real visitor does that constantly.

The defect: once any premise was on the table, the deduction route claimed the
rest of the conversation. Ask it a syllogism and then "What is a volcano?" and it
answered "that does not follow from what I was given", because a stored universal
plus a question-shaped surface was enough for it to act. "Write a python function
that reverses a string" was quietly filed as a premise. From the outside this is
indistinguishable from the machine breaking, and it is very close to the misfire
a user reported on the live site.

The cause is a missing relevance condition. A deduction engine is only entitled to
speak about the premises on the table, and nothing in the fold said so.

The rule this adds, in three parts:

    a surface that states new premises is always the fold's business
    "what follows" is always the fold's business
    otherwise the fold may act only on a yes/no question whose content words
        actually appear in the stored premises

A question that fails all three is not merely declined, it is handled as though
the fold were not there: the premise store is set aside for the duration of the
turn, so the rest of the chain answers exactly as it did before the fold existed,
and the premises are restored afterwards for when the subject comes back.

Definitional questions ("what is a server") are excluded even when they overlap
the premises, because "what is X" is a question about the world and the corpus
route owns it. Deduction answers yes-or-no and what-follows, nothing else.

Hand-authored 2026-08-28. Judged by the gate.
"""

from __future__ import annotations

import re

from oracle_release_runtime_w55 import OracleReleaseRuntimeW55
from oracle_release_runtime_w54 import _ASK_FOLLOW, _HAS_PREMISE, _QUES, _SPLIT

# only these openings are deduction questions. "what is X" is the corpus route's.
_YESNO = re.compile(
    r'^(?:is|are|was|were|does|do|did|can|could|would|will|has|have|must)\b', re.I)
_STOP = {
    'a', 'an', 'the', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'am',
    'all', 'every', 'each', 'no', 'not', 'if', 'then', 'or', 'and', 'but',
    'either', 'neither', 'does', 'do', 'did', 'can', 'could', 'would', 'will',
    'what', 'which', 'who', 'whom', 'when', 'where', 'why', 'how', 'follows',
    'of', 'to', 'in', 'on', 'at', 'by', 'for', 'from', 'with', 'as', 'that',
    'this', 'these', 'those', 'it', 'its', 'there', 'here', 'so', 'therefore',
    'have', 'has', 'had', 'some', 'any', 'me', 'you', 'we', 'they', 'i',
}
_WORD = re.compile(r'[a-z0-9]+')


def _content(text):
    return {w for w in _WORD.findall(str(text).lower())
            if w not in _STOP and len(w) > 1}


class OracleReleaseRuntimeW56(OracleReleaseRuntimeW55):
    """Deduction, restricted to the premises it actually holds."""

    @staticmethod
    def _premise_terms(st):
        terms = set()
        for key in ('all', 'no', 'have', 'cond', 'or', 'inst'):
            for pair in st.get(key, ()):
                for half in pair:
                    terms |= _content(half)
        for f in list(st.get('fact', ())) + list(st.get('nfact', ())):
            terms |= _content(f)
        return terms

    def _deduction_relevant(self, surface, st):
        """May the deduction route act on this turn at all?"""
        if _HAS_PREMISE.search(surface):
            return True                       # new premises are always its business
        if _ASK_FOLLOW.search(surface):
            return True
        if not any(st.get(k) for k in ('all', 'no', 'cond', 'or', 'inst', 'have')):
            return True                       # nothing held, the parent passes through
        clauses = [c.strip(' ,') for c in _SPLIT.split(surface) if c and c.strip(' ,')]
        questions = [c for c in clauses if _QUES.match(c)]
        if not questions:
            return False                      # a statement on a new subject is not a premise
        q = questions[-1]
        if not _YESNO.match(q):
            return False                      # "what is X" belongs to the corpus route
        return bool(_content(q) & self._premise_terms(st))

    def chat(self, text: str, session_id: str = 'default') -> dict:
        s = ' '.join(str(text).strip().split())
        st = self._store(session_id)
        if self._deduction_relevant(s, st):
            return super().chat(s, session_id)

        # Not this fold's turn. Set the premises aside so the rest of the chain
        # answers as if the fold were not installed, then put them back: the
        # subject may return, and a visitor should not have to restate premises
        # because they asked something else in between.
        saved = {k: list(v) for k, v in st.items()}
        for v in st.values():
            v.clear()
        try:
            return super().chat(s, session_id)
        finally:
            for k, v in saved.items():
                st[k].clear()
                st[k].extend(v)
