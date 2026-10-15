#!/usr/bin/env python3
"""oracle_release_runtime_w191 - selection (O2): never say the same thing twice.

The gate now measures repeat_rate: over cited follow-up turns in a session, the
fraction whose cited claims were ALL already cited earlier. At the tip it is
0.52: the head repeats itself more than half the time when asked to go on.
This fold keeps, per session, the claim ids it has already released, and when a
route's answer would repeat only what was said, it replaces the answer with
the next claims from the same admitted page that were not yet told, ordered by
how many new content terms each brings. Nothing is composed: every sentence is
an admitted claim with its id, from the page the route itself chose. If the
page has nothing new, the answer says so, cited to the page, instead of
repeating. Methods are prefixed _s187_. Parent: the serving tip, named.
"""

from __future__ import annotations

import importlib
import re

from oracle_release_runtime_w184 import OracleReleaseRuntimeW184 as _Base

_an = importlib.import_module('oracle_release_runtime_an')
_content_terms, CITE_RX = _an.content_terms, _an.CITE

ACCORDING = re.compile(r"According to ([^,\[]{1,80}),", re.I)
PAGE_TAG = re.compile(r"The page for ([^:\[]{1,80}) records", re.I)
REPEATABLE = ('summar', 'anchored', 'continue', 'list_n', 'what_causes', 'how_does', 'resolve:topic', 'explain', 'timeline')


class OracleReleaseRuntimeW191(_Base):
    """Selection: replace a repeated answer with untold claims from the same page."""

    def _s187_state(self, session_id: str) -> dict:
        store = getattr(self, '_s187_store', None)
        if store is None:
            store = self._s187_store = {}
        st = store.get(session_id)
        if st is None:
            st = store[session_id] = {'told': set(), 'terms': set(), 'cited_turns': 0}
        return st

    def _s187_page_of(self, result: dict):
        prov = result.get('provenance') or {}
        for key in ('page', 'page_id'):
            v = prov.get(key)
            if isinstance(v, str) and v:
                try:
                    pid = self.bench_query.page_id(v)
                except Exception:
                    pid = None
                if pid:
                    return pid, v
                if re.match(r'^(sw|ox|fb|en)\d+$', v):
                    return v, v
        resp = str(result.get('response', ''))
        m = ACCORDING.search(resp) or PAGE_TAG.search(resp)
        if m:
            title = m.group(1).strip()
            try:
                pid = self.bench_query.page_id(title)
            except Exception:
                pid = None
            if pid:
                return pid, title
        return None, None

    def _s187_novel_claims(self, st: dict, page: str, n: int = 3):
        try:
            rows = self.bench_query.page_sentences(page)
        except Exception:
            rows = []
        scored = []
        for i, (cid, fact) in enumerate(rows):
            if cid in st['told']:
                continue
            terms = set(_content_terms(fact))
            scored.append((len(terms - st['terms']), -i, cid, fact))
        scored.sort(key=lambda x: (-x[0], -x[1]))
        return [(cid, fact) for _, _, cid, fact in scored[:n]]

    def chat(self, text: str, session_id: str = 'default') -> dict:
        s = ' '.join(str(text).strip().split())
        result = super().chat(s, session_id)
        st = self._s187_state(session_id)
        resp = str(result.get('response', ''))
        cited = set(CITE_RX.findall(resp))
        path = str(result.get('path', ''))
        if (result.get('status') == 'answered' and cited and st['cited_turns'] > 0
                and cited <= st['told'] and any(k in path for k in REPEATABLE)):
            page, title = self._s187_page_of(result)
            if page:
                picks = self._s187_novel_claims(st, page, 3)
                if picks:
                    body = 'Beyond what I already told you on %s: ' % (title or page) + ' '.join(
                        '%s [%s]' % (fact, cid) for cid, fact in picks)
                    result = dict(result)
                    result['response'] = body
                    result['path'] = path + '|select:novel'
                    prov = dict(result.get('provenance') or {})
                    prov['selection'] = {'page': page, 'replaced_repeats': sorted(cited)[:6], 'chosen': [cid for cid, _ in picks]}
                    result['provenance'] = prov
                    cited = set(CITE_RX.findall(body))
                else:
                    body = ('I have already given you everything the record holds on %s [page:%s]; ask about something '
                            'beside it and I will follow.' % (title or page, page))
                    result = dict(result)
                    result['response'] = body
                    result['path'] = path + '|select:exhausted'
                    cited = set()
                try:
                    q = self._paths.get(session_id)
                    if q and len(q) and q[-1].get('in_surface', '')[:60] == s[:60]:
                        rec = q[-1]
                        rec['operator'] = result['path']
                        self._recite(rec, s, str(result['response']))
                except Exception:
                    pass
        if result.get('status') == 'answered' and cited:
            st['cited_turns'] += 1
            st['told'] |= cited
        st['terms'] |= set(_content_terms(str(result.get('response', ''))))
        return result
