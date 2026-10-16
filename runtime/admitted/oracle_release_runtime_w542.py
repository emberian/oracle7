#!/usr/bin/env python3
"""oracle_release_runtime_w542 - CAPABILITY RELEASE: SPECIALIST NETWORK v4 (specialists/_gate/network_v4.py) answers the
multi-step quantity questions the chain declines. Ben 2026-10-16: "its about combining the internal reasoning not the
language" - one specialist's checked result is the next one's typed input; no step is passed along as words.

What v4 adds to v3 (it loads PRIVATE copies of network_v2/v3, so the w525 network is untouched):
  - the PLACE as a typed quantity: a question about the Moon, Mars or another named body asks the bodies specialist for
    that body's surface gravity (the weight of 1 kg there) and puts it in the pool; Earth is standard gravity; a body with
    no record is a validity decline, never Earth's gravity;
  - units v3 could not read (cm3 / cc, kN), a temperature CHANGE ("heated by 40 C"), RATES ("7 litres per 100 km", "12 pages
    in 3 minutes") and counted things ("how many cookies");
  - a solid object's own volume -> its mass through the densities specialist; derivations from three givens by core math;
  - validity first: negative magnitudes, zero or negative rates and unknown bodies decline before any search.
Development (all on sets seen before this fold): composition C1 (spent sealed set, now development) 31/32 right, 0 wrong,
1 declined (v3: 10 right, 4 wrong); net_dev_v1 47/47, net_dev_v2 60/60, net_dev_v3 11/11 - identical to v3 on all three.
A new sealed composition set (C2) is written after this fold is frozen and run once.

When it runs: only on turns the chain did not answer for lack of a reading - the w525 condition (withheld or a
clarification that is not a deliberate verdict), or w541's half-answer / wrong-gravity / disagreement withholds, which
are the turns v4 was built to work properly. Never on w541's validity withholds or any other check's decline
(precision_guard, same-name, weight, private question), never on conversation acts, and its answer must itself be
checked: v4 answers only when every complete plan at the shallowest depth agrees. Its reply names the path it took."""
from __future__ import annotations

import importlib.util
import re
import sys
import threading

from oracle_release_runtime_w541 import OracleReleaseRuntimeW541 as _Base

SPEC_ROOT = __import__("os").environ.get("ORACLE7_ROOT", "/opt/oracle-clm") + "/specialists"
GATE = SPEC_ROOT + "/_gate"
NET4_CODE = GATE + "/network_v4.py"
NET_STANDING = GATE + "/standing_net_v6.txt"
_S: dict = {}
_LOCK = threading.Lock()


def _c542_net():
    with _LOCK:
        if "net" not in _S:
            if GATE not in sys.path:
                sys.path.insert(0, GATE)
            spec = importlib.util.spec_from_file_location("o7_network_v4_w542", NET4_CODE)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            _S["mod"] = mod
            _S["net"] = mod.Network(open(NET_STANDING, encoding="utf-8").read().split(), SPEC_ROOT, GATE)
        return _S["net"]


DELIBERATE = ("does_not_follow", "out_of_fragment", "validity")
REDO = ("precision_guard:Q2_half_answer>", "precision_guard:Q3_wrong_gravity>", "precision_guard:Q4_paths_disagree>")
CHECKS = ("precision_guard", "same_name_guard", "weight:", "chat:unresolved", "act:", "organ:converse", "safety", "refuse")
CLARIFY = ("act:clarify_specific", "act:clarify|")
PRIVATE = re.compile(r"\b(my|our|mine)\b", re.I)


def _c542_eligible(q, out):
    st, path = str(out.get("status", "")), str(out.get("path", ""))
    if path.startswith(REDO):
        return True
    if st not in ("withheld", "clarification") or path.endswith(DELIBERATE):
        return False
    # a clarification asked about a pronoun the same turn already names ("A gold coin is 2 cm across... What does it weigh")
    # or about a turn it could not parse: the network answers only from a checked path over the turn's own givens
    if path.startswith(CHECKS) and not path.startswith(CLARIFY):
        return False
    return not PRIVATE.search(q) and bool(re.search(r"\d", q))


def _c542_asked_unit(q, out, n):
    """v3 answered in another unit than the one asked ("in kilonewtons" -> "15400 N") and v4 reaches the same value"""
    if not str(out.get("path", "")).startswith("network3>") or n.get("status") != "answered":
        return False
    if not re.search(r"\bin\s+[^\s?]+\s*\??\s*$", q.strip()):
        return False
    V2 = _S["mod"].V2

    def first(s):
        for m in V2.RX_QTY.finditer(str(s or "").split("(path:")[0]):
            u = V2.unit_lookup(m.group(2))
            if u:
                return V2.fnum(m.group(1)), m.group(2), u
        return None
    a, b = first(out.get("response")), first(n.get("response"))
    if not a or not b or a[1].lower() == b[1].lower() or a[2][1] != b[2][1]:
        return False
    si_a, si_b = a[0] * a[2][0], b[0] * b[2][0]
    return abs(si_a - si_b) <= 0.02 * max(abs(si_a), abs(si_b), 1e-12)     # the same quantity, stated in another unit


class OracleReleaseRuntimeW542(_Base):
    def chat(self, text: str, session_id: str = "default") -> dict:
        out = super().chat(text, session_id=session_id)
        if not isinstance(out, dict):
            return out
        q = str(text or "")
        try:
            if _c542_eligible(q, out):
                n = _c542_net().solve(q)
            elif out.get("status") == "answered" and str(out.get("path", "")).startswith("network3>"):
                n = _c542_net().solve(q)
                if not _c542_asked_unit(q, out, n):
                    return out
            else:
                return out
            if n.get("status") != "answered":
                return out
            hops = [str(t.get("node")) for t in n.get("trace") or []]
            new = dict(out)
            new.update({"status": "answered", "path": "network4>" + " ".join(hops), "response": n["response"], "references": [],
                        "provenance": {"kind": "specialist_network_v4", "path_bytes": n.get("path_bytes"), "trace": n.get("trace"),
                                       "givens": n.get("givens"), "goal": n.get("goal"), "core_status": out.get("status"),
                                       "core_path": out.get("path")}})
            return new
        except Exception:  # noqa: BLE001 - a network failure never costs the chain's own reply
            return out
