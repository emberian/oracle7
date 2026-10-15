#!/usr/bin/env python3
"""oracle_release_runtime_w244 - DEEP REACH: the English Wikipedia by-slot store answers
only where the runtime has just declined.

The m13e8 stores (6.34M articles, 19.9M claims, 13 GB each) were measured on
2026-09-05 as the tip's primary store and as a transparent fallback behind the
primary reader. Both made things worse: as primary, answered 400 -> 396,
capability 213 -> 203 and 17 s -> 270 s per measurement; as a transparent
fallback, page_id resolved titles the rest of the runtime could not read, and
eight relation-panel items lost their walk. The small curated store must stay
the runtime's world.

So the deep store is a separate, explicit route that fires only on a decline:
when the parent answers a definitional form ("what is X", "who was X", "tell me
about X", "define X") with a clarification or a vessel receipt, and the deep
store holds a page for X, the reply is that page's first sentences with their
own claim ids (enwiki_..., simplewiki_...), tagged [ev:direct] and marked as
coming from the deep record. Nothing the parent already answers is touched; a
title the deep store lacks stays a received shape. The store is named by
ORACLE_DEEP_BUILD; without it the runtime is exactly its parent.
Methods _s244_. Parent: the serving tip, named.
"""

from __future__ import annotations

import os
import re
from pathlib import Path

from oracle_release_runtime_w242 import OracleReleaseRuntimeW242 as _Base

WHAT = re.compile(r"^(?:what|who)\s+(?:is|are|was|were)\s+(?:a\s+|an\s+|the\s+)?(?P<x>[A-Za-z][\w \-'.]{1,70}?)\s*[?.!]*$", re.I)
TELL = re.compile(r"^(?:tell me about|define|describe|explain)\s+(?:a\s+|an\s+|the\s+)?(?P<x>[A-Za-z][\w \-'.]{1,70}?)\s*[?.!]*$", re.I)
DECLINE_STATUS = ('clarification', 'withheld', 'declined', 'empty')


class OracleReleaseRuntimeW244(_Base):
    """Deep reach on decline: the big store speaks only where the small one is silent."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._s244_deep = None
        deep_path = os.environ.get('ORACLE_DEEP_BUILD')
        if deep_path and Path(deep_path).exists():
            try:
                from stage5m13e7_benchfold_induction_v1 import DBpediaQuery
                self._s244_deep = DBpediaQuery(Path(deep_path))
            except Exception:
                self._s244_deep = None

    def _s244_declined(self, res: dict) -> bool:
        if not isinstance(res, dict) or res.get('status') == 'answered':
            return False
        return 'vessel:receipt' in str(res.get('path', '')) or str(res.get('status', '')) in DECLINE_STATUS

    def _s244_lookup(self, x: str):
        deep = self._s244_deep
        if deep is None:
            return None, []
        pid = None
        for cand in (x, x.title(), x.lower(), x.capitalize()):
            try:
                pid = deep.page_id(cand)
            except Exception:
                pid = None
            if pid:
                break
        if not pid:
            return None, []
        try:
            rows = [(cid, ' '.join(str(f).split())) for cid, f in deep.page_sentences(pid)]
        except Exception:
            rows = []
        rows = [(cid, f) for cid, f in rows if len(f.split()) >= 4 and f[-1] in '.!?'][:3]
        return pid, rows

    def chat(self, text: str, session_id: str = 'default') -> dict:
        res = super().chat(text, session_id)
        try:
            if self._s244_deep is None or not self._s244_declined(res):
                return res
            s = ' '.join(str(text).split())
            m = WHAT.match(s) or TELL.match(s)
            if not m:
                return res
            x = m.group('x').strip().rstrip('?.!')
            pid, rows = self._s244_lookup(x)
            if not rows:
                return res
            body = ' '.join('%s [%s]' % (f, cid) for cid, f in rows[:2])
            out = dict(res)
            out.update({
                'status': 'answered', 'path': 'deep_reach:definitional',
                'response': '[ev:direct] %s (From the deep record: English Wikipedia by slot.)' % body,
                'references': [{'id': cid, 'text': f, 'page_id': pid} for cid, f in rows[:2]],
                'provenance': dict(res.get('provenance') or {}, kind='deep_reach', topic=x, page_id=pid, store='ORACLE_DEEP_BUILD',
                                   declined_as=str(res.get('path', ''))),
            })
            return out
        except Exception:
            return res
