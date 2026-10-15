#!/usr/bin/env python3
"""oracle_release_runtime_w432 - READING: yes/no over a given passage, and multiple choice by attestation.

Two benchmark rows stood at zero because the model never saw the task as the benchmark states it:
BoolQ gives a passage with its question, and MMLU-Pro gives ten options. Both are answerable under
the strictness law without any new knowledge:

    passage yes/no   "Passage: ... Question: is X Y?" -> the passage sentence that covers the question's
                     constraint terms in full is the evidence; its polarity (a negation next to the
                     constraint) decides No, otherwise Yes; the sentence is quoted as the warrant. No
                     covering sentence -> receipt.
    options          "... Options: (A) ... (J) ..." -> each option is scored by attestation: a store
                     sentence on a page of the question's proper-noun spans, or the option's own page,
                     that covers the option's content terms together with the question's constraints.
                     The answer is the single option whose attestation is full and unique; two attested
                     options, or none, -> receipt. The attesting sentence is cited.

Methods _r432_. Parent: the serving tip, named.
"""

from __future__ import annotations

import re
import time

from oracle_release_runtime_w267 import OracleReleaseRuntimeW267 as _Base
import oracle_release_runtime_w420 as _w420

PASSAGE = re.compile(r"^Passage:\s*(.+?)\s*\n\s*Question:\s*(.+?)\s*$", re.S)
OPTIONS = re.compile(r"^(.*?)\n\s*Options:\s*\n(.+)$", re.S)
OPTION_LINE = re.compile(r"^\(([A-J])\)\s*(.+?)\s*$")
NEGATION = re.compile(r"\b(?:not|no|never|neither|nor|cannot|can't|isn't|aren't|wasn't|weren't|doesn't|don't|didn't|without|unable|illegal|false)\b", re.I)
YESNO_HEAD = re.compile(r"^(?:is|are|was|were|does|do|did|can|could|has|have|had|will|would|should)\b", re.I)


def _split_sentences(text):
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", ' '.join(str(text).split())) if len(s.strip()) > 12]


class OracleReleaseRuntimeW432(_Base):
    """Passage yes/no and attested multiple choice."""

    # ---- passage yes/no ---------------------------------------------------------------------------------
    def _r432_passage(self, s, res, t0):
        m = PASSAGE.match(s)
        if not m:
            return None
        passage, q = m.group(1), m.group(2)
        if not YESNO_HEAD.match(q):
            return None
        terms = [t for t in _w420._qterms(q) if len(t) > 2]
        if len(terms) < 2:
            return None
        best = None
        for sent in _split_sentences(passage):
            toks = _w420._toks(sent)
            cov = sum(1 for t in terms if t in toks) / len(terms)
            if not best or cov > best[0]:
                best = (cov, sent)
        if not best or best[0] < 0.99:
            return None
        cov, sent = best
        # polarity: a negation in the covering sentence within the clause that carries the constraints
        neg = bool(NEGATION.search(sent))
        verdict = 'No' if neg else 'Yes'
        out = dict(res)
        out.update({'status': 'answered', 'path': 'reading:passage_yesno', 'response': '%s. The passage states it: "%s"' % (verdict, sent[:300]),
                    'references': [{'id': 'passage', 'text': sent[:300]}],
                    'provenance': dict(res.get('provenance') or {}, kind='reading', reading={'via': 'passage_yesno', 'coverage': round(cov, 2), 'negation': neg, 'terms': terms[:8]},
                                       verified_warrant={'kind': 'passage_quote', 'steps': [{'sentence': sent[:200]}]}, ms=int((time.time() - t0) * 1000), parent_path=str(res.get('path', '')))})
        return out

    # ---- multiple choice by attestation ------------------------------------------------------------------
    def _r432_options(self, s, res, t0):
        m = OPTIONS.match(s)
        if not m:
            return None
        q, block = m.group(1).strip(), m.group(2)
        opts = []
        for line in block.splitlines():
            mm = OPTION_LINE.match(line.strip())
            if mm:
                opts.append((mm.group(1), mm.group(2)))
        if len(opts) < 2:
            return None
        cap = self._f420_spans(q, lower=False)
        qterms = _w420._qterms(q)
        pages = []
        for span in cap[:3]:
            pages += self._f420_pages(span)
        attested = []
        for letter, text in opts:
            if time.time() - t0 > _w420.BUDGET_S * 2:
                break
            oterms = [t for t in _w420._qterms(text) if len(t) > 2 and t not in ('true', 'false', 'none', 'above', 'all', 'only')]
            if not oterms:
                continue
            # the option's own page, when it names a thing, joins the question's pages
            opages = list(pages)
            for span in self._f420_spans(text, lower=False)[:1]:
                opages += self._f420_pages(span)
            found = None
            for pid, rows, src in opages:
                for cid, sent in rows[:60]:
                    toks = _w420._toks(sent)
                    ocov = sum(1 for t in oterms if t in toks) / len(oterms)
                    qcov = sum(1 for t in qterms if t in toks) / max(1, len(qterms))
                    if ocov >= 0.99 and qcov >= 0.34:
                        found = (cid, sent, round(qcov, 2))
                        break
                if found:
                    break
            if found:
                attested.append((letter, text, found))
        if len(attested) != 1:
            return None
        letter, text, (cid, sent, qcov) = attested[0]
        out = dict(res)
        out.update({'status': 'answered', 'path': 'reading:option_attested', 'response': 'Option (%s) %s. The record attests it: %s [%s]' % (letter, text, sent[:260], cid),
                    'references': [{'id': cid, 'text': sent[:300]}],
                    'provenance': dict(res.get('provenance') or {}, kind='reading', reading={'via': 'option_attested', 'option': letter, 'question_coverage': qcov, 'options': len(opts)},
                                       ms=int((time.time() - t0) * 1000), parent_path=str(res.get('path', '')))})
        return out

    def chat(self, text: str, session_id: str = 'default') -> dict:
        res = super().chat(text, session_id)
        try:
            s = str(text).strip()
            if str(session_id).startswith('loop-delib-'):
                return res
            if not (s.startswith('Passage:') or '\nOptions:' in s):
                return res
            t0 = time.time()
            out = self._r432_passage(s, res, t0) if s.startswith('Passage:') else self._r432_options(s, res, t0)
            if out:
                return out
            # the task was stated and no evidence covered it: a receipt, never the parent's guess about a fragment
            if isinstance(res, dict) and res.get('status') == 'answered':
                rep = dict(res)
                rep.update({'status': 'withheld', 'path': 'reading:withheld|vessel:receipt',
                            'response': 'I read the passage and the question but found no sentence that covers the question in full, so I will not guess.' if s.startswith('Passage:')
                            else 'I read the options but no single option is attested in the record with the question, so I will not guess.',
                            'references': [], 'provenance': dict(res.get('provenance') or {}, kind='reading', reading={'via': 'withheld'}, parent_path=str(res.get('path', '')))})
                return rep
        except Exception:
            return res
        return res
