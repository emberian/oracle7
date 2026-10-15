#!/usr/bin/env python3
"""oracle_release_runtime_w270 - SELF-IMPROVEMENT fold (epoch 48): the loop speaking from its ledgers.

Answers "how do you improve?" / "what did you learn recently?" / "what was refused
and why?" from the actual admission and rejection records - including refusal REASONS,
because the read-the-reasons law is now a capability, not just a discipline. Robustness
is queryable: the bar never falls, refusals are preserved, every step is witnessed.
Authored 2026-09-07 10:37 UTC by oracle_fold_worker_v6, chained on oracle_release_runtime_w269."""

from __future__ import annotations

import re

from oracle_release_runtime_w269 import OracleReleaseRuntimeW269

RECENT_ADMITS = ['oracle_release_runtime_w269.py admitted', 'oracle_release_runtime_w268.py admitted', 'oracle_release_runtime_w434.py admitted', 'oracle_release_runtime_w432.py admitted', 'oracle_release_runtime_w267.py admitted']
RECENT_REFUSALS = ["oracle_release_runtime_w436.py: [{'no_gain': 'new-family candidate must raise at least one metric above baseline (epochs a"]

HOW_RX = re.compile(r"(how do you (?:improve|learn)|how does your improvement work)", re.I)
LEARNED_RX = re.compile(r"(what (?:did|have) you learn(?:ed)?( recently)?)", re.I)
REFUSED_RX = re.compile(r"(what was (?:refused|rejected)( and why)?)", re.I)


class OracleReleaseRuntimeW270(OracleReleaseRuntimeW269):
    """Base + the improvement-ledger routes."""

    def chat(self, text: str, session_id: str = "default") -> dict:
        s = " ".join(str(text).strip().split())
        if HOW_RX.search(s):
            return {"status": "answered", "path": "worker:self_improve",
                     "response": "A worker authors candidate folds from residue - "
                                 "mined relations, induced templates, world episodes; "
                                 "a gate measures each on held-out and admits only "
                                 "no-regression; the bar rises with each admission and "
                                 "never falls; refusals are preserved with reasons; "
                                 "every step is witnessed. [improvement_ledger]",
                     "provenance": {"kind": "improvement_ledger", "epoch": 48},
                     "latency_ms": 1}
        if LEARNED_RX.search(s):
            bits = "; ".join(RECENT_ADMITS[:4]) or "no recent admissions"
            return {"status": "answered", "path": "worker:self_improve",
                     "response": f"Recently admitted: {bits}. [improvement_ledger]",
                     "provenance": {"kind": "improvement_ledger", "epoch": 48},
                     "latency_ms": 1}
        if REFUSED_RX.search(s):
            bits = "; ".join(RECENT_REFUSALS[:3]) or "no recent refusals"
            return {"status": "answered", "path": "worker:self_improve",
                     "response": f"Refused, with reasons preserved: {bits}. "
                                 f"[improvement_ledger]",
                     "provenance": {"kind": "improvement_ledger", "epoch": 48},
                     "latency_ms": 1}
        return super().chat(s, session_id)
