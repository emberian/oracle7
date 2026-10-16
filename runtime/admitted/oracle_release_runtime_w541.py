#!/usr/bin/env python3
"""oracle_release_runtime_w541 - CORRECTNESS RELEASE: the wrong answers and false yeses found by the composition test C1
(research record E-20261016-0006, 2026-10-16) become declines. Narrowing only: every change below withholds an answer the
chain gave; none adds one.

The quantity routes (a specialist called by the core, the v3 network, the weight fold) answered questions whose working
they had not done. Each answered quantity turn is now read again by network_v4's question reader (specialists/_gate/
network_v4.py: typed givens, the goal's dimension, the place named) and withheld when:
1. THE GIVENS ARE NOT PHYSICAL: "An iron block has a volume of -50 cubic centimetres. What does it weigh?" was answered
   3.861 N, and "A 2 kg rock is carried to the planet Zorbon" got Earth's gravity. A negative magnitude, a rate of zero or
   less, or a body with no record (network_v4's validity verdict) withholds the answer.
2. HALF AN ANSWER: "A bucket holds 12 litres of water. What does that water weigh on Mars?" was answered "about 12 kg" by
   the densities specialist - the first step, given as the result. An answer whose quantity is not of the kind asked for
   (a mass for a weight, a mass of fuel for a mass of CO2 is still a mass, so only the DIMENSION is checked) is withheld.
3. THE WRONG PLACE'S GRAVITY: "A 70 kg climber gains 300 metres of height on Mars" was answered with 9.80665 m/s2. When the
   question names a body other than Earth, an answer worked with standard Earth gravity is withheld.
4. TWO CHECKED PATHS DISAGREE: when network_v4 works the same question to a value of the same kind that differs by more
   than 2%, the chain's answer is withheld (the network's planner already declines on its own disagreeing paths).
Turns on other routes, conversation acts, deliberate verdicts and declines are untouched. A network_v4 failure never costs
the chain's reply."""
from __future__ import annotations

import importlib.util
import re
import sys
import threading

from oracle_release_runtime_w415 import OracleReleaseRuntimeW415 as _Base

SPEC_ROOT = __import__("os").environ.get("ORACLE7_ROOT", "/opt/oracle-clm") + "/specialists"
GATE = SPEC_ROOT + "/_gate"
NET4_CODE = GATE + "/network_v4.py"
NET_STANDING = GATE + "/standing_net_v6.txt"
QTY_ROUTES = ("specialist_call>", "network3>", "weight:")
EARTH_G = re.compile(r"9\.8066|9\.81\b|standard Earth gravity|Earth's gravity", re.I)
_S: dict = {}
_LOCK = threading.Lock()


def _c541_net():
    with _LOCK:
        if "net" not in _S:
            if GATE not in sys.path:
                sys.path.insert(0, GATE)
            spec = importlib.util.spec_from_file_location("o7_network_v4_w541", NET4_CODE)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            _S["mod"] = mod
            _S["net"] = mod.Network(open(NET_STANDING, encoding="utf-8").read().split(), SPEC_ROOT, GATE)
        return _S["mod"], _S["net"]


def _c541_qty(mod, text):
    """the reply's stated result -> (SI value, dimension), read before any bracketed working"""
    head = re.split(r"\s\(|\[", str(text or ""), 1)[0]
    for m in mod.V2.RX_QTY.finditer(head):
        u = mod.V2.unit_lookup(m.group(2))
        if u:
            try:
                return mod.V2.fnum(m.group(1)) * u[0], u[1]
            except (TypeError, ValueError):
                continue
    return None


def _c541_why(q, out):
    """-> (code, response) when the chain's quantity answer must be withheld, else None"""
    if out.get("status") != "answered" or not str(out.get("path", "")).startswith(QTY_ROUTES):
        return None
    mod, net = _c541_net()
    text = mod.normalise(q)
    resp = str(out.get("response", ""))
    n4 = net.solve(text)
    if n4.get("check") == "validity":
        return "Q1_not_physical", "I can't work that out: %s." % n4.get("reason")
    givens, flags = mod.read_givens_v4(text)
    goal = mod.read_goal_v4(text, flags.get("counts", []))
    got = _c541_qty(mod, resp)
    if goal and goal[0] == "dim" and got and got[1] != goal[1]:
        return "Q2_half_answer", "I worked out only part of that, not the %s you asked for, so I won't give it as the answer." % goal[2]
    body = mod.body_of(text)
    if body and body != "Earth" and EARTH_G.search(resp):
        return "Q3_wrong_gravity", "That answer used Earth's gravity, and you asked about %s, so I won't give it." % body
    if n4.get("status") == "answered" and got:
        mine = _c541_qty(mod, n4.get("response", ""))
        if mine and mine[1] == got[1] and abs(mine[0] - got[0]) > 0.02 * max(abs(mine[0]), abs(got[0]), 1e-12):
            return "Q4_paths_disagree", "Two checked ways of working this out give different answers, so I won't guess."
    return None


class OracleReleaseRuntimeW541(_Base):
    def chat(self, text: str, session_id: str = "default") -> dict:
        out = super().chat(text, session_id=session_id)
        if not isinstance(out, dict):
            return out
        try:
            why = _c541_why(str(text or ""), out)
        except Exception:  # noqa: BLE001 - a network_v4 failure never costs the chain's reply
            why = None
        if why:
            new = dict(out)
            new.update({"status": "withheld", "path": "precision_guard:%s>%s" % (why[0], out.get("path")), "references": [],
                        "response": why[1]})
            return new
        return out
