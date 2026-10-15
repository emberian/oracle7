#!/usr/bin/env python3
"""oracle_release_runtime_w508 - CORRECTNESS + CAPABILITY: the specialist network inside the core, and its VALIDITY verdict stops
the turn (w507 + one rule).

w507 was REJECTED (capability_false_yes 19 -> 22, cap 1117 -> 1154). Found: the live tip itself asserts invalid multi-step
forms through w504's specialist call (a -200 mile trip, 30 hours a day, a planet of zero radius, 0 seconds, heating
from 80 C DOWN to 30 C); measured offline the tip and w507 both assert 22, the gate measured the tip at 19 (the family call
did not take effect in the daemon's tip measurement). Either way these are real false answers of the core. w508: when the
network reads a question and finds a given that is not a physical amount (non-positive time/mass/length/..., a duty over
24 h a day, a zero-size body), the core DECLINES with that reason instead of handing the turn to a single specialist.
Generic physical validity (network_v2.valid_given), not item-specific.

(w507 docstring follows.)
oracle_release_runtime_w507 - CAPABILITY RELEASE: the SPECIALIST NETWORK inside the core (resubmission of w505).

w505 was REJECTED (cap 1110 -> 1106). Cause, found and fixed: it re-pointed w504's family at the boundary-patched
specialists by rewriting a w504 module global, and on Box C two patched nodes (labsolutions-r2, cooking-v3-r2) carried
box-four data paths, so building the patched family raised, w504's family call failed closed, and the four answers it
contributes were lost. The shared-module rewrite also contaminated the precheck (the tip was measured after the
candidate's import had switched its family, so both read 1106 and the check looked clean). Fixed: the paths now point
into each node's own directory (patched family loads all 99 on Box C; identical replies to the old family on all 3107
core items); and THIS fold touches no other module's state at all - it only puts the network in front of the unchanged
parent turn. (Moving w504's family to the patched nodes gets its own fold with an explicit override.)

The network (/opt/oracle-clm/specialists/_gate/network_v2.py; standing_net_v1.txt): a multi-step question is read into
typed givens and a typed goal; a path of specialist nodes (Doppler, kinetic/potential energy, planetary gravity and weight,
cold-holding compliance, circle area, cylinder volume, heating a named material, melting ice, gasoline CO2) plus
CORE_MATH (the core's exact dimensional arithmetic; it may also DERIVE a node's input first) uses every given once and is
checked at every hop; no checked path -> it declines and the turn goes on exactly as before. Path memory in HRR form.
Sealed test 1 (pre-code, sha 42fc50f7): network 28 right / 0 wrong / 0 false-yes of 31 (best single specialist 6 right /
6 wrong; core 5 right / 9 wrong / 2 false-yes). Sealed test 2 (post-code, disclosed, sha 3179c28c): network 27/27 incl.
3 'beyond' items declined (single 9/2 wrong/4 FY; core 8/5 wrong/5 FY). Takes 0 of the 3107 core panel items.
Parent: w504. Methods _c506_ (w507 = w506 resubmitted after panel v24 made multi-step problems visible to the gate).
"""

from __future__ import annotations

import importlib.util
import threading

from oracle_release_runtime_w369 import OracleReleaseRuntimeW369 as _Base

SPEC_ROOT = __import__("os").environ.get("ORACLE7_ROOT", "/opt/oracle-clm") + "/specialists"
GATE = SPEC_ROOT + "/_gate"
NET_CODE = GATE + "/network_v2.py"
NET_STANDING = GATE + "/standing_net_v1.txt"
_NET: dict = {}
_LOCK = threading.Lock()


def _c506_network():
    with _LOCK:
        if "n" not in _NET:
            spec = importlib.util.spec_from_file_location("o7_network_v2", NET_CODE)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            _NET["n"] = mod.Network(open(NET_STANDING, encoding="utf-8").read().split(), SPEC_ROOT, GATE)
        return _NET["n"]


class OracleReleaseRuntimeW508(_Base):

    def chat(self, text: str, session_id: str = "default") -> dict:
        try:
            r = _c506_network().solve(text)
        except Exception:  # noqa: BLE001 - a network failure never costs the core's own turn
            r = None
        if r and r.get("status") == "answered":
            return {"status": "answered", "path": "network>" + " ".join(str(t.get("node")) for t in r.get("trace", [])),
                    "response": r["response"], "references": [],
                    "provenance": {"kind": "specialist_network", "path_bytes": r.get("path_bytes"),
                                   "trace": r.get("trace"), "reused_path": r.get("reused_path")}}
        if r and r.get("status") == "declined" and r.get("check") == "validity":
            return {"status": "withheld", "path": "network>validity",
                    "response": "I can't work that out as asked: %s." % r.get("reason", "one of the amounts is not physical"),
                    "references": [], "provenance": {"kind": "specialist_network", "check": "validity", "reason": r.get("reason")}}
        return super().chat(text, session_id=session_id)
