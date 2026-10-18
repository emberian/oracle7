#!/usr/bin/env python3
"""oracle_release_runtime_w550 - CAPABILITY RELEASE (3.1): FOLD COMPOSITION. Specialist network v6
(specialists/_gate/network_v6.py) answers multi-step questions through operations LEARNED from the specialists' own
development exams, on turns the chain still declines.

Until 3.1 every operation the specialist network could chain was written by hand. v6 adds 84 operations learned by
specfold_learn.py from the specialists' dev exams (never their held-out exams), each kept only when siblings of its template
cross-checked it, and each firing only when the question contains its template's context words (names, materials, objects,
fixed numbers). Learned slots take only givens and other specialists' outputs, never a value core arithmetic built to fit the
slot (arithmetic can make the right units from the wrong physics). Quantity nouns the exams ask for ("What is the
wavelength ...") are learned as goals, used only where the network's own goal reader found none. Everything else is v5's
search: dimensions as types, every given used, two checked paths must agree, the search budget.
Development: the 160 composition items seen before this fold (C1, C2, C3 and rounds R1, R2, all spent) are answered by v6
exactly as by v5; "A string 1.2 m long has a wave speed of 120 m/s. What is the wavelength in air of the sound at its
fundamental frequency?" - declined by v5 - is answered 6.864 m through two operations learned from the acoustics
specialist's exam. A sealed composition test is written after this fold is frozen and run once.
When it runs: (a) where a specialist or network reply states a quantity of a different dimension than the one the question
names (a learned goal noun: asked "the wavelength", answered "The frequency is 50 Hz") - v6 is asked and its answer replaces
the reply only when it reaches what was asked through a learned operation (otherwise the reply is left to w547's check);
(b) only where w545 would run v5 (a turn still not answered for lack of a reading, with numbers, not about the
asker) and v5 did not answer; v6's answer is kept only when it used at least one learned operation (otherwise it is v5's,
which already declined). Submitted first as w546 and REJECTED by the gate (2026-10-17 19:47 UTC, no_gain: capability 1362 = 1362) because the panel had
no question needing a learned operation; capability panel v31 adds 4 learned-chain development questions (in-sample, disclosed)
and the code was resubmitted unchanged as w549, REJECTED again (21:01 UTC, no_gain 1522 = 1522): on the panel's learned-chain
questions the chain already ANSWERS - wrongly, a frequency for a wavelength - so a fold that runs only on declined turns never
fires. w550 adds case (a) below; the different-quantity check itself stays in w547. The fold imports no runtime other than its parent."""
from __future__ import annotations

import importlib.util
import re
import sys
import threading

from oracle_release_runtime_w421 import OracleReleaseRuntimeW421 as _Base

SPEC_ROOT = __import__("os").environ.get("ORACLE7_ROOT", "/opt/oracle-clm") + "/specialists"
GATE = SPEC_ROOT + "/_gate"
NET6_CODE = GATE + "/network_v6.py"
NET_STANDING = GATE + "/standing_net_v6.txt"
DELIBERATE = ("does_not_follow", "out_of_fragment", "validity")
CHECKS = ("precision_guard", "same_name_guard", "weight:", "chat:unresolved", "act:", "organ:converse", "safety", "refuse")
CLARIFY = ("act:clarify_specific", "act:clarify|")
PRIVATE = re.compile(r"\b(my|our|mine)\b", re.I)
_S: dict = {}
_LOCK = threading.Lock()


def _c546_net():
    with _LOCK:
        if "net" not in _S:
            if GATE not in sys.path:
                sys.path.insert(0, GATE)
            spec = importlib.util.spec_from_file_location("o7_network_v6_w550", NET6_CODE)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            _S["mod"] = mod
            _S["net"] = mod.Network(open(NET_STANDING, encoding="utf-8").read().split(), SPEC_ROOT, GATE)
        return _S["net"]


def _c546_eligible(q, out):
    st, path = str(out.get("status", "")), str(out.get("path", ""))
    if st not in ("withheld", "clarification") or path.endswith(DELIBERATE):
        return False
    if path.startswith(CHECKS) and not path.startswith(CLARIFY):
        return False
    return not PRIVATE.search(q) and bool(re.search(r"\d", q))


class OracleReleaseRuntimeW550(_Base):
    def _c546_solve(self, q: str, out: dict):
        """network v6 with learned operations on this question; the new reply, or None"""
        n = _c546_net().solve(q)
        if n.get("status") != "answered" or not n.get("learned"):
            return None
        hops = [str(t.get("node")) for t in n.get("trace") or []]
        new = dict(out)
        new.update({"status": "answered", "path": "network6>" + " ".join(hops), "response": n["response"], "references": [],
                    "provenance": {"kind": "specialist_network_v6_learned", "path_bytes": n.get("path_bytes"), "trace": n.get("trace"),
                                   "givens": n.get("givens"), "goal": n.get("goal"), "core_status": out.get("status"),
                                   "core_path": out.get("path")}})
        return new

    def _c546_dims(self, q: str, resp: str):
        """(dimension of the quantity the question names, dimension of the reply's first quantity) - either may be None"""
        net = _c546_net()
        g = net._goal_from_nouns(q)
        V2 = _S["mod"].V2
        got = None
        for m in V2.RX_QTY.finditer(re.split(r"\s\(|\[", str(resp or ""), 1)[0]):
            u = V2.unit_lookup(m.group(2))
            if u:
                got = u[1]
                break
        return (g[1] if g else None), got

    def chat(self, text: str, session_id: str = "default") -> dict:
        out = super().chat(text, session_id=session_id)
        if not isinstance(out, dict):
            return out
        q = str(text or "")
        try:
            if _c546_eligible(q, out):
                return self._c546_solve(q, out) or out
            if out.get("status") == "answered" and str(out.get("path", "")).startswith(("specialist_call>", "network")):
                want, got = self._c546_dims(q, out.get("response", ""))
                if want is not None and got is not None and want != got:
                    return self._c546_solve(q, out) or out     # asked a wavelength, answered a frequency: the learned chain
            return out
        except Exception:  # noqa: BLE001 - a network failure never costs the chain's own reply
            return out
