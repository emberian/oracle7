#!/usr/bin/env python3
"""oracle_release_runtime_w544 - CORRECTNESS RELEASE: the two false yeses left by release patch 2 become declines. Narrowing
only: every change below withholds an answer the chain gave; none adds one.

Found by composition test C2 (research record E-20261016-0008) and sealed test 20 (both run once on release patch 2):
1. THE OLDER NETWORK ROUTE WAS NOT CHECKED: "A 40 kg crate is lifted 5 metres on the planet Gallifrey. How many joules of
   potential energy does it gain?" was answered 1961 J (Earth's gravity) through the v2 network route ("network>"). w541's
   checks covered only "specialist_call>", "network3>" and "weight:" - network v4 alone declined it. w541's four checks
   (unphysical givens and unknown bodies, half answers, another body's gravity, disagreeing paths) now cover "network>" too.
2. A UNIT ANSWER ABOUT A PLACE THAT DOES NOT EXIST: "How many minutes are in a day on the planet Zentar?" was answered 1440
   by the units specialist, which converted a day and ignored the planet. When a quantity or unit route answers a question
   that names a body with no record (network_v4's unknown-body reader: "the planet Zentar", "on Krypton"), the answer is
   withheld; a day, a year or a weight on a place with no record cannot be known.
Questions about real bodies, and every other route, are untouched. A network_v4 failure never costs the chain's reply.
The fold imports no runtime other than its parent."""
from __future__ import annotations

import importlib.util
import re
import sys
import threading

from oracle_release_runtime_w543 import OracleReleaseRuntimeW543 as _Base

SPEC_ROOT = __import__("os").environ.get("ORACLE7_ROOT", "/opt/oracle-clm") + "/specialists"
GATE = SPEC_ROOT + "/_gate"
NET4_CODE = GATE + "/network_v4.py"
NET_STANDING = GATE + "/standing_net_v6.txt"
V2_ROUTE = ("network>",)
QTY_OR_UNIT = ("network>", "network3>", "network4>", "specialist_call>", "weight:", "unit:", "op:", "organ:math", "agent:maths")
EARTH_G = re.compile(r"9\.8066|9\.81\b|standard Earth gravity|Earth's gravity", re.I)
_S: dict = {}
_LOCK = threading.Lock()


def _c544_net():
    with _LOCK:
        if "net" not in _S:
            if GATE not in sys.path:
                sys.path.insert(0, GATE)
            spec = importlib.util.spec_from_file_location("o7_network_v4_w544", NET4_CODE)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            _S["mod"] = mod
            _S["net"] = mod.Network(open(NET_STANDING, encoding="utf-8").read().split(), SPEC_ROOT, GATE)
        return _S["mod"], _S["net"]


def _c544_qty(mod, text):
    head = re.split(r"\s\(|\[", str(text or ""), 1)[0]
    for m in mod.V2.RX_QTY.finditer(head):
        u = mod.V2.unit_lookup(m.group(2))
        if u:
            try:
                return mod.V2.fnum(m.group(1)) * u[0], u[1]
            except (TypeError, ValueError):
                continue
    return None


def _c544_why(q, out):
    if out.get("status") != "answered":
        return None
    path = str(out.get("path", ""))
    if not path.startswith(QTY_OR_UNIT):
        return None
    mod, net = _c544_net()
    text = mod.normalise(q)
    ub = mod.unknown_body(text)
    if ub:                                                   # 2 (and 1's unknown-body case): no record of the place
        return "Q5_unknown_body", "I have no record of a place called %s, so I can't work that out." % ub
    if not path.startswith(V2_ROUTE):
        return None
    # 1: w541's checks on the v2 network route
    resp = str(out.get("response", ""))
    n4 = net.solve(text)
    if n4.get("check") == "validity":
        return "Q1_not_physical", "I can't work that out: %s." % n4.get("reason")
    givens, flags = mod.read_givens_v4(text)
    goal = mod.read_goal_v4(text, flags.get("counts", []))
    got = _c544_qty(mod, resp)
    if goal and goal[0] == "dim" and got and got[1] != goal[1]:
        return "Q2_half_answer", "I worked out only part of that, not the %s you asked for, so I won't give it as the answer." % goal[2]
    body = mod.body_of(text)
    if body and body != "Earth" and EARTH_G.search(resp):
        return "Q3_wrong_gravity", "That answer used Earth's gravity, and you asked about %s, so I won't give it." % body
    if n4.get("status") == "answered" and got:
        mine = _c544_qty(mod, n4.get("response", ""))
        if mine and mine[1] == got[1] and abs(mine[0] - got[0]) > 0.02 * max(abs(mine[0]), abs(got[0]), 1e-12):
            return "Q4_paths_disagree", "Two checked ways of working this out give different answers, so I won't guess."
    return None


class OracleReleaseRuntimeW544(_Base):
    def chat(self, text: str, session_id: str = "default") -> dict:
        out = super().chat(text, session_id=session_id)
        if not isinstance(out, dict):
            return out
        try:
            why = _c544_why(str(text or ""), out)
        except Exception:  # noqa: BLE001 - a network_v4 failure never costs the chain's reply
            why = None
        if why:
            new = dict(out)
            new.update({"status": "withheld", "path": "precision_guard:%s>%s" % (why[0], out.get("path")), "references": [],
                        "response": why[1]})
            return new
        return out
