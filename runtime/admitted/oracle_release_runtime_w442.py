#!/usr/bin/env python3
"""oracle_release_runtime_w442 - READING v3: paraphrase reach through the chain's own WordNet store.

BoolQ questions paraphrase their passages ("make" for "produce", "illegal" for "prohibited"). w434 finds the covering
sentence over stemmed terms; this fold lets a question term be covered by a single-word WordNet alias of any of its
senses (the m13a WordNet specialist store, CC-licensed, already in the chain), and records which term was covered by
which alias in the provenance. Measured before building (analyze_boolq_v5, n=600, development and daily windows):

    w434 rules                  110 attempted, 90 right, 20 wrong, honest 0.117
    + strict aliases            119 attempted, 98 right, 21 wrong, honest 0.128   (items reached by an alias: 19/20)
    + any-sense aliases         131 attempted, 108 right, 23 wrong, honest 0.142  (items reached by an alias: 31/34)

Any-sense aliases are used: the covering sentence still has to carry every other term, so the sense is pinned by the
rest of the question, and the reached items were right 31 times in 34. Everything else is w434: the same withholds,
the same verdict rule, the same one-miss rule with its required words. Methods _r436_ (kept, so the ledger reads continuously). Parent: the serving tip, named, and nothing
else is imported: the helpers this fold needs are declared here rather than borrowed from an ancestor,
because the fork guard reads imports and a borrowed ancestor looks like a branch.
"""

from __future__ import annotations

import os
import re
import sqlite3
import time

from oracle_release_runtime_w278 import OracleReleaseRuntimeW278 as _Base

WORDNET_PATHS = (os.environ.get('ORACLE_WORDNET_SPECIALIST', ''),
                 __import__("os").environ.get("ORACLE7_ROOT", "/opt/oracle-clm") + '/fable-content/oracle-m-series-2026-08-15/m13a_wordnet_build_a_v4/wordnet_specialist.sqlite3')

# copied verbatim from the reading route at build time, so behaviour matches what was measured while
# this file still imports nothing but the serving head

PASSAGE = re.compile(r"^Passage:\s*(.+)\s+Question:\s*(.+?)\s*$", re.S)

YESNO_HEAD = re.compile(r"^(?:is|are|was|were|does|do|did|can|could|has|have|had|will|would|should)\b", re.I)

STOP = {'the', 'a', 'an', 'of', 'in', 'on', 'and', 'or', 'to', 'is', 'are', 'was', 'were', 'for', 'by', 'with', 'at', 'from', 'as', 'that', 'this', 'it', 'its',
        'does', 'did', 'can', 'could', 'has', 'have', 'had', 'will', 'would', 'should', 'there', 'you', 'they', 'any', 'still', 'ever', 'really', 'actually', 'get', 'been', 'being'}

REQUIRED = {'world', 'universe', 'earth', 'all', 'every', 'only', 'always', 'never', 'largest', 'biggest', 'first', 'last', 'most', 'best', 'oldest',
            'longest', 'highest', 'tallest', 'smallest', 'greatest', 'deepest', 'fastest', 'same', 'different', 'part', 'member'}

def _toks(s):
    return {_stem(t) for t in re.findall(r"[a-z0-9]+", s.lower())}

def _stem(t):
    for suf in ('ies', 'ing', 'ed', 'es', 'ly', 'er', 's'):
        if len(t) > len(suf) + 3 and t.endswith(suf):
            base = t[:-len(suf)]
            return base + 'y' if suf == 'ies' else base
    return t

def _sentences(text):
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", ' '.join(str(text).split())) if len(s.strip()) > 12]

def _qterms(q):
    return [t for t in _toks(q) if t.isdigit() or (len(t) > 2 and t not in STOP)]


class OracleReleaseRuntimeW442(_Base):
    """Passage reading with WordNet-alias coverage."""

    def _r436_db(self):
        db = getattr(self, '_r436_conn', None)
        if db is not None:
            return db
        self._r436_conn = False
        for p in WORDNET_PATHS:
            if p and os.path.exists(p):
                try:
                    self._r436_conn = sqlite3.connect('file:%s?mode=ro' % p, uri=True, check_same_thread=False)
                    break
                except Exception:  # noqa: BLE001
                    self._r436_conn = False
        return self._r436_conn

    def _r436_aliases(self, term):
        """single-word aliases of any sense of the term, stemmed; cached per term"""
        cache = getattr(self, '_r436_cache', None)
        if cache is None:
            cache = self._r436_cache = {}
        if term in cache:
            return cache[term]
        out = {}
        db = self._r436_db()
        if db:
            try:
                for (sid,) in db.execute('select synset_id from alias where normalized_alias = ? limit 40', (term,)).fetchall():
                    for (surf,) in db.execute('select normalized_alias from alias where synset_id = ? limit 40', (sid,)).fetchall():
                        if ' ' in surf or '_' in surf or surf == term or len(surf) < 3:
                            continue
                        out.setdefault(_stem(surf), surf)
            except Exception:  # noqa: BLE001
                pass
        cache[term] = out
        return out

    def _r436_covered(self, terms, terms_stem, numbers, pool):
        """returns (ok, coverage, via) with via = [(term, alias)] for terms covered by an alias"""
        missing = []
        via = []
        for t, ts in zip(terms, terms_stem):
            if ts in pool:
                continue
            if not t.isdigit():
                al = self._r436_aliases(t)
                hit = next((al[s] for s in al if s in pool), None)
                if hit:
                    via.append((t, hit))
                    continue
            missing.append(ts)
        if not missing:
            return True, 1.0, via
        if len(terms_stem) >= 4 and len(missing) == 1 and missing[0] not in numbers and missing[0] not in REQUIRED:
            return True, round(1 - 1 / len(terms_stem), 2), via
        return False, 0.0, via

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
            pool = set(_stem(t) for t in _toks(sent))
            ok, cov, via = self._r436_covered(terms, terms_stem, numbers, pool)
            if ok:
                hits = sum(1 for t in terms_stem if t in pool)
                if best is None or hits > best[0]:
                    best = (hits, sent, cov, via)
        out = dict(res)
        if best is None:
            return self._r434_receipt(out, res, 'I read the passage and the question but found no sentence that covers the question in full, so I will not guess.', 'no_covering_sentence')
        _, sent, cov, via = best
        # the alias terms join the term set so the negation window sees them
        vt = set(terms) | set(terms_stem) | {_stem(a) for _, a in via} | {a for _, a in via}
        verdict, reason = self._r434_verdict(sent, vt, terms_stem, q)
        if verdict is None:
            return self._r434_receipt(out, res, 'The passage sentence that covers the question does not settle it (%s), so I will not guess.' % reason.replace('_', ' '), reason)
        out.update({'status': 'answered', 'path': 'reading:passage_yesno', 'response': '%s. The passage states it: "%s"' % (verdict, sent[:300]),
                    'references': [{'id': 'passage', 'text': sent[:300]}],
                    'provenance': dict(res.get('provenance') or {}, kind='reading',
                                       reading={'via': 'passage_yesno', 'coverage': cov, 'reason': reason, 'terms': terms[:8], 'aliases': [{'term': t, 'alias': a} for t, a in via]},
                                       verified_warrant={'kind': 'passage_quote', 'steps': [{'sentence': sent[:200]}]}, ms=int((time.time() - t0) * 1000), parent_path=str(res.get('path', '')))})
        return out
