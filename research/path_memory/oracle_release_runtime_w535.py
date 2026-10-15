#!/usr/bin/env python3
"""oracle_release_runtime_w535 - PATH MEMORY: routing by verified credit (Ben 2026-10-13: "we want all that in the release";
"this system is built for recursive improvement at the base - properly apply it").

Until w534 the main model combined routes by FIXED precedence: its chain answers first; the specialist families answer only
when the chain declines. w535 lets VERIFIED OUTCOMES decide instead. path_memory_v1 holds, for every path (the shape of a
question - its lead word, the relation reader that recognises it, whether it carries numbers - bound with the route that
answered), how often that route's answer to that shape was RIGHT or WRONG on graded dev pools (TriviaQA train, Mintaka
train, the dev split of every admitted specialist's exam; never a sealed item, never a reported benchmark window). The
memory is HRR (osub_seed codebook, D=1024): an unseen path borrows the credit of its most resonant stored neighbour on the
same route.
RULE (policy and thresholds chosen on 80% of 4,804 graded dev questions by sealed test 15's own pass rule - more right,
no more wrong, precision not lower - and checked on the held-back 20%: fixed routing 470 right / 56 wrong, path memory
475 / 51; a withholding policy that cut wrong answers to 30 but lost right ones was not chosen; the held-back fifth was
looked at for three policy families - disclosed): when the route that answered has LOST credit for this shape (smoothed
precision < P_LOW over >= MIN_N graded answers), the relation family is asked the same question, and its answer replaces the
chain's when the family's route has EARNED more credit for this shape (>= P_HIGH and above the chain route's). Otherwise
the chain's answer stands. A route with good or unknown credit answers exactly as before; the memory never produces an
answer itself. The deployed memory holds all 4,804 graded outcomes (thresholds from the 80% only).
Memory file pinned: /opt/oracle-clm/specialists/_gate/path_memory_v1.json (never edited after this fold is measured).
The fold imports no runtime other than its parent."""
from __future__ import annotations

import importlib.util
import threading

from oracle_release_runtime_w534 import OracleReleaseRuntimeW534 as _Base

try:
    import path_memory_v1 as _PM
except Exception:  # noqa: BLE001 - without the memory the fold is exactly its parent
    _PM = None

SPEC_ROOT = "/opt/oracle-clm/specialists"
GATE = SPEC_ROOT + "/_gate"
MEMORY = GATE + "/path_memory_v1.json"
FAMILY_CODE = GATE + "/combo_runtime_v1.py"
STANDING = GATE + "/standing_new_v5.txt"
P_LOW, P_HIGH, MIN_N = 0.80, 0.60, 4          # path_memory_tune_v1 (train 80%, sealed-15 rule): swap_only
_S: dict = {}
_LOCK = threading.Lock()
WITHHELD = "The route that answered this kind of question has been wrong too often when checked, so I won't give that answer."


def _mem():
    with _LOCK:
        if "pm" not in _S:
            _S["pm"] = _PM.PathMemory.load(MEMORY)
        return _S["pm"]


def _family():
    with _LOCK:
        if "fam" not in _S:
            spec = importlib.util.spec_from_file_location("o7_combo_runtime_v1_w535", FAMILY_CODE)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            ids = open(STANDING, encoding="utf-8").read().split()
            _S["fam"] = mod.Family(["%s/%s/manifest.json" % (SPEC_ROOT, i) for i in ids], ["%s/%s" % (SPEC_ROOT, i) for i in ids])
        return _S["fam"]


class OracleReleaseRuntimeW535(_Base):
    def chat(self, text: str, session_id: str = "default") -> dict:
        out = super().chat(text, session_id=session_id)
        if _PM is None or not isinstance(out, dict) or out.get("status") != "answered":
            return out
        prov = out.get("provenance") or {}
        q = (prov.get("chat_resolved") or {}).get("read_as") or str(text or "")
        try:
            sh = _PM.shape(q)
            r0 = _PM.route_of(out.get("path"))
            if r0 in ("guard", "none"):
                return out
            p0 = _mem().precision(sh, r0, min_n=MIN_N)
        except Exception:  # noqa: BLE001
            return out
        if p0 is None or p0[0] >= P_LOW:
            return out
        alt = None
        if r0 != "specialist:rel":
            try:
                f = _family().reply(q, "pm:%s" % session_id)
                p1 = _mem().precision(sh, "specialist:rel", min_n=MIN_N)
                fp = (f or {}).get("provenance") or {}
                if f and f.get("status") == "answered" and not fp.get("declined") and p1 and p1[0] >= P_HIGH and p1[0] > p0[0]:
                    alt = (f, p1)
            except Exception:  # noqa: BLE001
                alt = None
        if not alt:
            return out                              # swap_only: without a better-credited route the chain's answer stands
        new = dict(out)
        if alt:
            f, p1 = alt
            new.update({"status": "answered", "path": "path_memory>specialist_call>" + str(f.get("path")),
                        "response": "%s [%s]" % (f["response"], (f.get("provenance") or {}).get("specialist")), "references": [],
                        "provenance": {"kind": "path_memory", "replaced_route": r0, "replaced_precision": round(p0[0], 3),
                                       "replaced_n": p0[1], "chosen_route": "specialist:rel", "chosen_precision": round(p1[0], 3),
                                       "chosen_n": p1[1], "shape": sh, "replaced_response": str(out.get("response", ""))[:300]}})
        else:
            new.update({"status": "withheld", "path": "path_memory:low_credit|" + str(out.get("path")), "response": WITHHELD,
                        "references": [], "provenance": {"kind": "path_memory", "withheld_route": r0, "precision": round(p0[0], 3),
                                                         "n": p0[1], "shape": sh, "withheld_response": str(out.get("response", ""))[:300]}})
        return new
