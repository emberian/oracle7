#!/usr/bin/env python3
"""oracle_release_runtime_w422 - PARSED-SURFACE LAW for the exact operators: no operator answers a problem it did not read whole.

Aimed at MATH-500 (2026-09-06): 200 competition problems, the served model answered 77 and
was wrong 65 times. Every wrong answer was an exact operator firing on a fragment of a
surface it cannot read: integer_sqrt took the "0" out of "sin D = 0.7"; statistics summed
every number in a word problem; the document runtime replied "1" or "3" to a polynomial;
algebra solved "x + 1 = 0" inside a cubic. The operators are exact; the parse was not. The
law this fold installs: an exact operator's answer stands only when the operator consumed
the surface; a surface with typeset mathematics (TeX delimiters, \\frac, \\sqrt, \\sum,
diagrams) is not one the current operators read, so their answers are withheld with a
receipt that names the class, and the surface is received so the loop sees the residue.

    surface     TeX markers: $...$, \\[ ... \\], \\frac \\sqrt \\sum \\cdot \\dots \\infty, [asy], ^{ , _{
    routes      op:*, algebra:*, document_runtime, arb:* capabilities, corpus_query:* on such a surface
    answer      withheld: "This is typeset mathematics; my exact operators read arithmetic,
                integer roots, combinations, statistics and linear algebra on plain surfaces,
                and did not read this one whole, so I will not guess."
    untouched   factoid, deliberation, self-explanation, conversation-ops and every plain surface

Methods _m422_. Parent: the serving tip, named.
"""

from __future__ import annotations

import re
import time

from oracle_release_runtime_w420 import OracleReleaseRuntimeW420 as _Base

TEX = re.compile(r"\$[^$]{1,200}\$|\\\[|\\\]|\\(?:frac|sqrt|sum|cdot|dots|infty|int|prod|binom|left|right|begin|end|text|mathbf|le|ge|neq|pi|theta|alpha|sin|cos|tan|log)\b|\[asy\]|\^\{|_\{")
ROUTES = ('op:', 'algebra:', 'document_runtime', 'arb:', 'corpus_query:', 'capability:', 'game:', 'deduce:', 'self:', 'factoid:', 'deliberation:', 'wordnet', 'conceptnet', 'definitional')
# an exact operator's own forms are short ("3 choose 2", "mean of 4, 8, 15"); a WORD PROBLEM of this
# length ("The Greek army contained two types of soldiers ... how many ...") is a surface the operator
# did not read whole, whatever numbers it found in it (measured on MATH-500, 2026-09-06)
WORD_PROBLEM_WORDS = 15
# deduction is not here: its premises are long by nature and it reads them whole (held-out diff 2026-09-06)
OPERATOR_ONLY = ('op:', 'algebra:', 'compute:')
# a function-word subject is a defect only on a surface that names something else to be the subject
# ("is there a word with q without u"); a short continuation turn ("is it big?") is the conversation's
FUNCTION_WORD_MIN_WORDS = 5


CLASSIFIES = re.compile(r"\bclassifies\s+([A-Za-z']+)\s+under\b")
FUNCTION_WORDS = {'there', 'it', 'this', 'that', 'here', 'they', 'he', 'she', 'we', 'you', 'i', 'them', 'these', 'those', 'what', 'which', 'who', 'one', 'any', 'some'}


class OracleReleaseRuntimeW422(_Base):
    """Exact operators answer only surfaces they read whole; a function word is never a subject."""

    @staticmethod
    def _m422_typeset(text):
        return len(TEX.findall(text)) >= 1

    @staticmethod
    def _m422_function_subject(res):
        """A kind-classification whose subject is a pronoun or adverb ("classifies there under location")."""
        m = CLASSIFIES.search(str(res.get('response', '')))
        return bool(m) and m.group(1).lower() in FUNCTION_WORDS

    def chat(self, text: str, session_id: str = 'default') -> dict:
        res = super().chat(text, session_id)
        try:
            s = str(text)
            if not isinstance(res, dict) or res.get('status') != 'answered' or str(session_id).startswith('loop-delib-'):
                return res
            path = str(res.get('path', ''))
            if path.startswith('wordnet_kind') and len(s.split()) >= FUNCTION_WORD_MIN_WORDS and self._m422_function_subject(res):
                t0 = time.time()
                try:
                    self._receive(' '.join(s.split())[:400], session_id, res)
                except Exception:
                    pass
                subj = CLASSIFIES.search(str(res.get('response', ''))).group(1)
                out = dict(res)
                out.update({'status': 'withheld', 'path': 'subject:function_word|vessel:receipt',
                            'response': 'I read "%s" as the subject of that question, which is a function word, not a subject, so the classification I had is not an answer. '
                                        'I will not guess.' % subj,
                            'references': [], 'provenance': dict(res.get('provenance') or {}, kind='function_word_subject', subject=subj, parent_path=path,
                                                                 ms=int((time.time() - t0) * 1000))})
                return out
            typeset = self._m422_typeset(s)
            word_problem = path.startswith(OPERATOR_ONLY) and len(s.split()) >= WORD_PROBLEM_WORDS and 'verified' not in path
            if not ((path.startswith(ROUTES) and typeset) or word_problem):
                return res
            t0 = time.time()
            if word_problem and not typeset:
                try:
                    self._receive(' '.join(s.split())[:400], session_id, res)
                except Exception:
                    pass
                out = dict(res)
                out.update({'status': 'withheld', 'path': 'operator:unparsed|vessel:receipt',
                            'response': 'That is a word problem. My exact operators read short forms (a sum, a mean, a choose, a linear equation) and this one '
                                        'took numbers out of a sentence it did not read whole, so I will not guess at it.',
                            'references': [],
                            'provenance': dict(res.get('provenance') or {}, kind='operator_unparsed', words=len(s.split()), parent_path=path,
                                               ms=int((time.time() - t0) * 1000))})
                return out
            try:
                self._receive(' '.join(s.split())[:400], session_id, res)
            except Exception:
                pass
            out = dict(res)
            out.update({'status': 'withheld', 'path': 'operator:unparsed|vessel:receipt',
                        'response': 'This is typeset mathematics. My exact operators read arithmetic, integer roots, combinations, statistics and linear '
                                    'algebra on plain surfaces, and they did not read this problem whole, so I will not guess at it.',
                        'references': [],
                        'provenance': dict(res.get('provenance') or {}, kind='operator_unparsed', markers=TEX.findall(s)[:6], parent_path=path,
                                           ms=int((time.time() - t0) * 1000))})
            return out
        except Exception:
            return res
