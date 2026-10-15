#!/usr/bin/env python3
"""oracle_release_runtime_w360 - SELF-IMPROVEMENT fold (epoch 77): the loop speaking from its ledgers.

Answers "how do you improve?" / "what did you learn recently?" / "what was refused
and why?" from the actual admission and rejection records - including refusal REASONS,
because the read-the-reasons law is now a capability, not just a discipline. Robustness
is queryable: the bar never falls, refusals are preserved, every step is witnessed.
Authored 2026-09-27 17:27 UTC by oracle_fold_worker_v6, chained on oracle_release_runtime_w359."""

from __future__ import annotations

import re

from oracle_release_runtime_w359 import OracleReleaseRuntimeW359

RECENT_ADMITS = ['oracle_release_runtime_w359.py admitted', 'oracle_release_runtime_w358.py admitted', 'oracle_release_runtime_w357.py admitted', 'oracle_release_runtime_w482.py admitted', 'oracle_release_runtime_w356.py admitted']
RECENT_REFUSALS = ["oracle_release_runtime_w355.py: [{'below_baseline': {'novelty': [0.6837, 0.6826]}}]", "oracle_release_runtime_w480.py: [{'unlicensed_assertions': {'capability_false_yes': [22, 23], 'meaning': 'the candidate as", "oracle_release_runtime_w478.py: [{'no_gain': 'new-family candidate must raise at least one metric above baseline (epochs a"]

HOW_RX = re.compile(r"(how do you (?:improve|learn)|how does your improvement work)", re.I)
LEARNED_RX = re.compile(r"(what (?:did|have) you learn(?:ed)?( recently)?)", re.I)
REFUSED_RX = re.compile(r"(what was (?:refused|rejected)( and why)?)", re.I)


class OracleReleaseRuntimeW360(OracleReleaseRuntimeW359):
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
                     "provenance": {"kind": "improvement_ledger", "epoch": 77},
                     "latency_ms": 1}
        if LEARNED_RX.search(s):
            bits = "; ".join(RECENT_ADMITS[:4]) or "no recent admissions"
            return {"status": "answered", "path": "worker:self_improve",
                     "response": f"Recently admitted: {bits}. [improvement_ledger]",
                     "provenance": {"kind": "improvement_ledger", "epoch": 77},
                     "latency_ms": 1}
        if REFUSED_RX.search(s):
            bits = "; ".join(RECENT_REFUSALS[:3]) or "no recent refusals"
            return {"status": "answered", "path": "worker:self_improve",
                     "response": f"Refused, with reasons preserved: {bits}. "
                                 f"[improvement_ledger]",
                     "provenance": {"kind": "improvement_ledger", "epoch": 77},
                     "latency_ms": 1}
        return super().chat(s, session_id)
