#!/usr/bin/env python3
"""CORRECTNESS RELEASE. ARTIFACT: repeat_rate (w193 replaced FIRST answers, which are never repeats, so the baseline repeat_rate 0.3942 was lowered by the defect itself; the corrected value is the honest one).
oracle_release_runtime_w195 - correction to w193's repeat check.

w193 asked "were this answer's citations already told?" AFTER w191 had recorded
them, so every wide-lead definition looked like a repeat and was replaced by
other claims from the page: "what is truth" answered with the second and third
sentences instead of the definition. The check must use the record as it stood
BEFORE the turn. This fold snapshots the told set at the start of each turn and
makes w193's check read the snapshot. Nothing else changes. Methods _r195_.
Parent: the serving tip, named.
"""

from __future__ import annotations

from oracle_release_runtime_w193 import OracleReleaseRuntimeW193 as _Base


class OracleReleaseRuntimeW195(_Base):
    """Repeat check against the record before the turn, not after."""

    def _k193_no_repeat(self, s: str, session_id: str, result: dict) -> dict:  # type: ignore[override]
        before = getattr(self, '_r195_before', None)
        if before is None:
            return result
        try:
            st = self._s187_state(session_id)
            after = st['told']
            st['told'] = set(before)          # judge against the record before this turn
            try:
                return super()._k193_no_repeat(s, session_id, result)
            finally:
                st['told'] = after | st['told']  # keep everything that was told, including the replacement
        except Exception:
            return result

    def chat(self, text: str, session_id: str = 'default') -> dict:
        try:
            self._r195_before = set(self._s187_state(session_id)['told'])
        except Exception:
            self._r195_before = set()
        return super().chat(text, session_id)
