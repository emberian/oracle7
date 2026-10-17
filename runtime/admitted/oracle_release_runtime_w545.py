#!/usr/bin/env python3
"""oracle_release_runtime_w545 - CAPABILITY RELEASE: SPECIALIST NETWORK v5 (specialists/_gate/network_v5.py) answers the
multi-step quantity questions the chain still declines after w542. v5 = v4 + the shapes v4 could not read, found by
composition test C2 (E-20261016-0008):
  - a box "5 cm by 4 cm by 3 cm" and a cube "5 cm on each side" become one volume, derived by core arithmetic and recorded
    as a hop in the path; a derived volume of a solid becomes its mass through the densities specialist;
  - "500 cubic centimetres of ice" ties the volume to its material; "the water in the pond" means the vessel is full;
  - "in a day" with no number is one day; "already at 0 C" is the object's state, not a quantity to use.
v5 loads a PRIVATE copy of v4 (released v4 untouched). Development (sets seen before this fold): C1 32/32, C2 32/32 (both
spent; v4: 31 and 27), 0 wrong; net_dev_v1 47/47, net_dev_v2 60/60, net_dev_v3 11/11 - identical to v4. A new sealed
composition test (C3) is written after this fold is frozen and run once.
When it runs: only on turns still not answered for lack of a reading after w542 (the w542 condition, the same check codes),
and, as w542 does for v3, to restate a v2/v3 network answer in the unit the question asked for when v5 reaches the same
value ("in kilonewtons" answered "55460 N" by the v3 network, C2). Never on a validity or other check's decline.
The fold imports no runtime other than its parent."""
from __future__ import annotations

import importlib.util
import re
import sys
import threading

from oracle_release_runtime_w544 import OracleReleaseRuntimeW544 as _Base

SPEC_ROOT = __import__("os").environ.get("ORACLE7_ROOT", "/opt/oracle-clm") + "/specialists"
GATE = SPEC_ROOT + "/_gate"
NET5_CODE = GATE + "/network_v5.py"
NET_STANDING = GATE + "/standing_net_v6.txt"
_S: dict = {}
_LOCK = threading.Lock()


def _c545_net():
    with _LOCK:
        if "net" not in _S:
            if GATE not in sys.path:
                sys.path.insert(0, GATE)
            spec = importlib.util.spec_from_file_location("o7_network_v5_w545", NET5_CODE)
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


def _c545_eligible(q, out):
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


def _c545_asked_unit(q, out, n):
    """v3 answered in another unit than the one asked ("in kilonewtons" -> "15400 N") and v4 reaches the same value"""
    if not str(out.get("path", "")).startswith(("network3>", "network>")) or n.get("status") != "answered":
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


class OracleReleaseRuntimeW545(_Base):
    def chat(self, text: str, session_id: str = "default") -> dict:
        out = super().chat(text, session_id=session_id)
        if not isinstance(out, dict):
            return out
        q = str(text or "")
        try:
            if _c545_eligible(q, out):
                n = _c545_net().solve(q)
            elif out.get("status") == "answered" and str(out.get("path", "")).startswith(("network3>", "network>")):
                n = _c545_net().solve(q)
                if not _c545_asked_unit(q, out, n):
                    return out
            else:
                return out
            if n.get("status") != "answered":
                return out
            hops = [str(t.get("node")) for t in n.get("trace") or []]
            new = dict(out)
            new.update({"status": "answered", "path": "network5>" + " ".join(hops), "response": n["response"], "references": [],
                        "provenance": {"kind": "specialist_network_v5", "path_bytes": n.get("path_bytes"), "trace": n.get("trace"),
                                       "givens": n.get("givens"), "goal": n.get("goal"), "core_status": out.get("status"),
                                       "core_path": out.get("path")}})
            return new
        except Exception:  # noqa: BLE001 - a network failure never costs the chain's own reply
            return out
