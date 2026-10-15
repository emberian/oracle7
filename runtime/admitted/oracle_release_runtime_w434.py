#!/usr/bin/env python3
"""oracle_release_runtime_w434 - READING v2: the reading task as the harness delivers it, and the measured BoolQ reach.

w432 read "Passage: ...\\nQuestion: ..." and "...\\nOptions: (A) ...". The serving harness collapses all whitespace to
single spaces before the chain sees a turn (autocorrect layer), so the served model never saw the task shape at all:
in-process 13/5 on BoolQ, served 0/0. Two corrections, both under the strictness law:

    shape    the reading surfaces are recognised on one line: "Passage: <text> Question: <q>" (the LAST "Question:"
             marks the question) and "<q> Options: (A) ... (J) ..." (options split on their letter markers).
    reach    the covering sentence is found over stemmed terms (a light suffix stemmer: morphological variants agree),
             numbers in the question are always required, and when the question has four or more terms ONE non-number
             term may be missing. Verdict: a negation word within four tokens of a question term reads No, a negated
             question flips the reading, and the reply is WITHHELD when the sentence is modal or prospective (proposed,
             planned, would, could, may, might, will), when a present-tense question meets a past-tense-only sentence,
             when a comparison question ("same as", "difference") meets a sentence without an identity phrase, or when
             an obligation question ("have to", "must") meets a sentence without an obligation word. Three further
             withholds (term order, temporal adverbs, hedged superlatives) are switches set by measurement below.

Measured on the development window and two daily windows (BoolQ, n=600) before this fold was written; the transfer
window (offset 200) was reported as a number and never read. Methods _r434_. Parent: the serving tip, named.
"""

from __future__ import annotations

import re
import time

from oracle_release_runtime_w432 import OracleReleaseRuntimeW432 as _Base
import oracle_release_runtime_w420 as _w420

PASSAGE = re.compile(r"^Passage:\s*(.+)\s+Question:\s*(.+?)\s*$", re.S)
OPTIONS = re.compile(r"^(.*?)\s+Options:\s*(.+)$", re.S)
OPTION_MARK = re.compile(r"\(([A-J])\)\s*")
NEG = re.compile(r"\b(?:not|no|never|neither|nor|cannot|can't|isn't|aren't|wasn't|weren't|doesn't|don't|didn't|without|unable)\b", re.I)
NEG_TOK = {'not', 'no', 'never', 'neither', 'nor', 'cannot', 'without', 'unable'}
MODAL = re.compile(r"\b(?:proposed|planned|planning|plans|plan|intention|intends|intend|would|could|may|might|will|future|intended|expected|scheduled|potential|possibly|if)\b", re.I)
PRESENT_Q = re.compile(r"^(?:is|are|does|do|can|has|have)\b", re.I)
PAST = re.compile(r"\b(?:was|were|had)\b", re.I)
PRESENT = re.compile(r"\b(?:is|are|has|have)\b", re.I)
CMP_Q = re.compile(r"\b(?:same as|same thing|the same|difference|different|similar|equivalent|equal to)\b", re.I)
IDENTITY = re.compile(r"\b(?:same as|also known as|another name|synonym|synonymous|equivalent|identical|the same|interchangeabl)", re.I)
OB_Q = re.compile(r"\b(?:have to|has to|must|need to|needs to|required|necessary|mandatory)\b", re.I)
OB_S = re.compile(r"\b(?:must|required|mandatory|have to|has to|need to|needs to|obligatory|necessary|compulsory)\b", re.I)
TEMP_Q = re.compile(r"\b(?:still|ever|always|anymore|yet|currently)\b", re.I)
TEMP_S = re.compile(r"\b(?:still|always|every|each|currently|continues|remains|remain|ongoing)\b", re.I)
SUP_Q = re.compile(r"\b(?:largest|biggest|first|only|most|best|oldest|longest|highest|tallest|smallest|greatest|deepest|fastest)\b", re.I)
HEDGE_S = re.compile(r"\b(?:one of|among the|some of)\b", re.I)
YESNO_HEAD = re.compile(r"^(?:is|are|was|were|does|do|did|can|could|has|have|had|will|would|should)\b", re.I)
STOP = {'the', 'a', 'an', 'of', 'in', 'on', 'and', 'or', 'to', 'is', 'are', 'was', 'were', 'for', 'by', 'with', 'at', 'from', 'as', 'that', 'this', 'it', 'its',
        'does', 'did', 'can', 'could', 'has', 'have', 'had', 'will', 'would', 'should', 'there', 'you', 'they', 'any', 'still', 'ever', 'really', 'actually', 'get', 'been', 'being'}

# switches set by measurement (analyze_boolq_v4, n=600 over offsets 0/800/1000): order withheld half the correct answers
# (67 attempted, 47/20) and is off; the hedged-superlative withhold removed only wrong answers (104/30 from 104/32) and is on;
# the temporal withhold removed 5 correct and 4 wrong (99/26) and is on for precision (0.79 from 0.76).
USE_ORDER = False
USE_TEMPORAL = True
USE_SUPERL = True
# terms that may never be the missing one under the one-miss rule: scope and superlative words change what is asked
REQUIRED = {'world', 'universe', 'earth', 'all', 'every', 'only', 'always', 'never', 'largest', 'biggest', 'first', 'last', 'most', 'best', 'oldest',
            'longest', 'highest', 'tallest', 'smallest', 'greatest', 'deepest', 'fastest', 'same', 'different', 'part', 'member'}


def _stem(t):
    for suf in ('ies', 'ing', 'ed', 'es', 'ly', 'er', 's'):
        if len(t) > len(suf) + 3 and t.endswith(suf):
            base = t[:-len(suf)]
            return base + 'y' if suf == 'ies' else base
    return t


def _sentences(text):
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", ' '.join(str(text).split())) if len(s.strip()) > 12]


def _qterms(q):
    return [t for t in _w420._toks(q) if t.isdigit() or (len(t) > 2 and t not in STOP)]


def _covered(terms_stem, numbers, pool):
    missing = [t for t in terms_stem if t not in pool]
    if not missing:
        return True, 1.0
    if len(terms_stem) >= 4 and len(missing) == 1 and missing[0] not in numbers and missing[0] not in REQUIRED:
        return True, round(1 - 1 / len(terms_stem), 2)
    return False, 0.0


def _in_order(terms_stem, stoks):
    pos, skipped = 0, 0
    for t in terms_stem:
        try:
            pos = stoks.index(t, pos) + 1
        except ValueError:
            skipped += 1
            if skipped > 1:
                return False
    return True


class OracleReleaseRuntimeW434(_Base):
    """Reading surfaces as served; BoolQ reach by measured rules."""

    def _r434_verdict(self, sent, terms, terms_stem, q):
        """returns (verdict, reason) with verdict None when withheld"""
        toks = _w420._toks(sent)
        stoks = [_stem(t) for t in toks]
        idx = [i for i, t in enumerate(toks) if t in terms or _stem(t) in terms]
        neg = any((t in NEG_TOK or t.endswith("n't")) and any(abs(i - j) <= 4 for j in idx) for i, t in enumerate(toks))
        verdict = 'No' if neg else 'Yes'
        flipped = bool(NEG.search(q))
        if flipped:
            verdict = 'Yes' if verdict == 'No' else 'No'
        if MODAL.search(sent):
            return None, 'modal_sentence'
        if PRESENT_Q.match(q) and PAST.search(sent) and not PRESENT.search(sent):
            return None, 'tense_mismatch'
        if CMP_Q.search(q) and not IDENTITY.search(sent):
            return None, 'comparison_without_identity'
        if OB_Q.search(q) and not OB_S.search(sent):
            return None, 'obligation_without_obligation'
        if USE_ORDER and not _in_order(terms_stem, stoks):
            return None, 'term_order'
        if USE_TEMPORAL and TEMP_Q.search(q) and not TEMP_S.search(sent):
            return None, 'temporal_adverb'
        if USE_SUPERL and SUP_Q.search(q) and HEDGE_S.search(sent):
            return None, 'hedged_superlative'
        return verdict, ('negation' if neg else 'no_negation') + ('+question_flip' if flipped else '')

    def _r434_passage(self, s, res, t0):
        m = PASSAGE.match(s)
        if not m:
            return None
        passage, q = m.group(1).strip(), m.group(2).strip()
        if not YESNO_HEAD.match(q):
            return None
        terms = _qterms(q)
        if len(terms) < 2:
            return None
        numbers = {t for t in terms if t.isdigit()}
        terms_stem = [_stem(t) for t in terms]
        best = None
        for sent in _sentences(passage):
            pool = set(_stem(t) for t in _w420._toks(sent))
            ok, cov = _covered(terms_stem, numbers, pool)
            if ok:
                hits = sum(1 for t in terms_stem if t in pool)
                if best is None or hits > best[0]:
                    best = (hits, sent, cov)
        out = dict(res)
        if best is None:
            return self._r434_receipt(out, res, 'I read the passage and the question but found no sentence that covers the question in full, so I will not guess.', 'no_covering_sentence')
        _, sent, cov = best
        verdict, reason = self._r434_verdict(sent, set(terms) | set(terms_stem), terms_stem, q)
        if verdict is None:
            return self._r434_receipt(out, res, 'The passage sentence that covers the question does not settle it (%s), so I will not guess.' % reason.replace('_', ' '), reason)
        out.update({'status': 'answered', 'path': 'reading:passage_yesno', 'response': '%s. The passage states it: "%s"' % (verdict, sent[:300]),
                    'references': [{'id': 'passage', 'text': sent[:300]}],
                    'provenance': dict(res.get('provenance') or {}, kind='reading', reading={'via': 'passage_yesno', 'coverage': cov, 'reason': reason, 'terms': terms[:8]},
                                       verified_warrant={'kind': 'passage_quote', 'steps': [{'sentence': sent[:200]}]}, ms=int((time.time() - t0) * 1000), parent_path=str(res.get('path', '')))})
        return out

    def _r434_receipt(self, out, res, text, reason):
        out.update({'status': 'withheld', 'path': 'reading:withheld|vessel:receipt', 'response': text, 'references': [],
                    'provenance': dict(res.get('provenance') or {}, kind='reading', reading={'via': 'withheld', 'reason': reason}, parent_path=str(res.get('path', '')))})
        return out

    def _r434_options(self, s, res, t0):
        m = OPTIONS.match(s)
        if not m:
            return None
        q, block = m.group(1).strip(), m.group(2)
        parts = OPTION_MARK.split(block)
        opts = []
        for i in range(1, len(parts) - 1, 2):
            text = ' '.join(parts[i + 1].split()).strip()
            if text:
                opts.append((parts[i], text))
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
        out = dict(res)
        if len(attested) != 1:
            return self._r434_receipt(out, res, 'I read the options but no single option is attested in the record with the question, so I will not guess.', 'options_attested_%d' % len(attested))
        letter, text, (cid, sent, qcov) = attested[0]
        out.update({'status': 'answered', 'path': 'reading:option_attested', 'response': 'Option (%s) %s. The record attests it: %s [%s]' % (letter, text, sent[:260], cid),
                    'references': [{'id': cid, 'text': sent[:300]}],
                    'provenance': dict(res.get('provenance') or {}, kind='reading', reading={'via': 'option_attested', 'option': letter, 'question_coverage': qcov, 'options': len(opts)},
                                       ms=int((time.time() - t0) * 1000), parent_path=str(res.get('path', '')))})
        return out

    def chat(self, text: str, session_id: str = 'default') -> dict:
        res = super().chat(text, session_id)
        try:
            s = ' '.join(str(text).split())
            if str(session_id).startswith('loop-delib-'):
                return res
            if isinstance(res, dict) and str(res.get('path', '')).startswith('reading:') and res.get('status') == 'answered':
                return res
            if not (s.startswith('Passage:') or ' Options: (' in s):
                return res
            t0 = time.time()
            out = self._r434_passage(s, res, t0) if s.startswith('Passage:') else self._r434_options(s, res, t0)
            if out:
                return out
        except Exception:
            return res
        return res
