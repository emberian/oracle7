#!/usr/bin/env python3
"""oracle_release_runtime_w525 - CAPABILITY RELEASE: the specialists admitted 2026-10-08 join the core, and SPECIALIST FUSION
(network_v3: one specialist's verified result feeds the next) answers what the v2 network could not.
Ben 2026-10-08: "we want the specialist fusion working and the 250 specialists shipped".

NEW FAMILY (pinned: /opt/oracle-clm/specialists/_gate/standing_new_v1.txt, never edited after this fold is measured):
  #101 densities (51/51 held-out vs head 3), #103 fluids (34/34 vs 2), #104 decay (34/42 vs 2), #105 springs (42/42 vs 2),
  (densities and fluids as their r2: silent when the material is a capitalised NAME - "the mass of Mercury" is the planet;
  byte-identical on all 102 / 68 panel inputs, so each inherits its admission),
  #106 fuels (42/42 vs 2) - each admitted by spec_gate_v3 (domain gain, no confident wrong over cap, no core item worse).
  Called exactly as w504 calls the standing family (combo_runtime_v1.Family: isolation, arbitration), only on turns the whole
  chain declined; a disagreement leaves the decline standing.
NARROWING PATCHES (each narrowing-only and byte-identical to the admitted version on every one of its panel inputs, so it
  inherits that admission). When the chain's answer came from the old specialist and its patch is SILENT on the turn, the
  turn counts as declined here and the new family / fusion read it (w504's family is not touched - this fold reads output):
    ocean -> ocean-r2 (46 inputs, 0 differ): pressure turns naming ANOTHER fluid got seawater's density ("5 m below the
      surface of mercury" -> 1025 kg/m3); fluids #103 reads them.
    astronomy-v3 -> astronomy-v3-r3 (276 inputs, 0 differ; carries r2's boundary narrowing): "the mass of 2 litres of
      mercury" got the PLANET's mass; densities #101 reads it.
FUSION (/opt/oracle-clm/specialists/_gate/network_v3.py, standing_net_v6.txt): network_v2's planner drew every operation's
  inputs from the question's givens; v3 plans over a POOL of typed quantities - givens and every verified intermediate - so
  an operation can consume another specialist's checked result (geometry -> densities -> thermo: "a tank 1 m across and 1 m
  tall full of water, kWh to heat it 20 -> 60 C" = 36.53 kWh). At the shallowest depth where any plan completes, every
  complete plan must agree (two checked paths that disagree -> decline). Quantities are read by ROLE (an amount must be
  attached to its material: "79 kg block of steel", never "a 35-kg dolphin ... the water"); goals added for pressure, force
  and mass are met only through a specialist operation, never by core math alone. Development: net_dev_v2 60/60 (= v2),
  OpenStax physics development 564 identical to v2 (2 right, 0 wrong), fusion development net_dev_v3 11/11.
Never overridden: any turn the chain answered (except the ocean case above), deliberate verdicts, validity verdicts.
The fold never imports a runtime other than its parent; it touches no other module's state."""
from __future__ import annotations

import importlib.util
import json
import re
import threading

from oracle_release_runtime_w524 import OracleReleaseRuntimeW524 as _Base

SPEC_ROOT = __import__("os").environ.get("ORACLE7_ROOT", "/opt/oracle-clm") + "/specialists"
GATE = SPEC_ROOT + "/_gate"
FAMILY_CODE = GATE + "/combo_runtime_v1.py"
NEW_STANDING = GATE + "/standing_new_v1.txt"
NET_CODE = GATE + "/network_v3.py"
NET_STANDING = GATE + "/standing_net_v6.txt"
NARROWED = {"ocean": "ocean-r2", "astronomy-v3": "astronomy-v3-r3"}
DELIBERATE = ("does_not_follow", "out_of_fragment", "validity")
_S: dict = {}
_LOCK = threading.Lock()


def _c525_load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _c525_family():
    with _LOCK:
        if "fam" not in _S:
            mod = _c525_load("o7_combo_runtime_v1_w525", FAMILY_CODE)
            ids = open(NEW_STANDING, encoding="utf-8").read().split()
            _S["fam"] = mod.Family(["%s/%s/manifest.json" % (SPEC_ROOT, i) for i in ids], ["%s/%s" % (SPEC_ROOT, i) for i in ids])
            _S["organ_cls"] = mod._Organ
        return _S["fam"]


def _c525_network():
    with _LOCK:
        if "net" not in _S:
            import sys
            if GATE not in sys.path:
                sys.path.insert(0, GATE)
            mod = _c525_load("o7_network_v3_w525", NET_CODE)
            _S["net"] = mod.Network(open(NET_STANDING, encoding="utf-8").read().split(), SPEC_ROOT, GATE)
        return _S["net"]


def _c525_narrowed_silent(path, text):
    """the chain's answer came from an old specialist whose narrowing patch is silent on this turn"""
    m = re.match(r"specialist_call>specialist:([\w.\-]+)>", str(path))
    if not m or m.group(1) not in NARROWED:
        return False
    _c525_family()
    patch = NARROWED[m.group(1)]
    with _LOCK:
        if patch not in _S:
            d = "%s/%s" % (SPEC_ROOT, patch)
            _S[patch] = _S["organ_cls"](d + "/manifest.json", d)
    return _S[patch].reply(text, "w525-narrowed") is None


def _c525_lacks(out):
    st, path = str(out.get("status", "")), str(out.get("path", ""))
    return st in ("withheld", "clarification") and not path.endswith(DELIBERATE)


class OracleReleaseRuntimeW525(_Base):
    def chat(self, text: str, session_id: str = "default") -> dict:
        out = super().chat(text, session_id=session_id)
        if not isinstance(out, dict):
            return out
        try:
            narrowed_case = _c525_narrowed_silent(out.get("path", ""), text)
            if not narrowed_case and not _c525_lacks(out):
                return out
            r = _c525_family().reply(text, "core:%s" % session_id)
            if r and r.get("status") != "disagree":
                prov = r.get("provenance") or {}
                if not prov.get("per_part") or any(p.get("specialist") and not p.get("declined") for p in (prov.get("parts") or [])):
                    status = "answered" if prov.get("per_part") or not prov.get("declined") else "withheld"
                    response = r["response"] if prov.get("per_part") else "%s [%s]" % (r["response"], prov.get("specialist"))
                    new = dict(out)
                    new.update({"status": status, "path": "specialist_call>" + str(r.get("path")), "response": response, "references": [],
                                "provenance": {"kind": "core_called_specialist", "family": "new_v1", "core_status": out.get("status"),
                                               "core_path": out.get("path"), "specialist": prov.get("specialist"), "parts": prov.get("parts")}})
                    return new
            n = _c525_network().solve(text)
            if n.get("status") == "answered":
                new = dict(out)
                new.update({"status": "answered", "path": "network3>" + " ".join(str(t.get("node")) for t in n.get("trace", [])),
                            "response": n.get("response"), "references": [],
                            "provenance": {"kind": "specialist_network_v3", "path_bytes": n.get("path_bytes"), "trace": n.get("trace"),
                                           "core_status": out.get("status"), "core_path": out.get("path")}})
                return new
            if narrowed_case:
                new = dict(out)
                new.update({"status": "withheld", "path": "specialist_call>narrowed>silent",
                            "response": "I can't verify an answer to that exact question, so I won't guess.", "references": [],
                            "provenance": {"kind": "narrowed_specialist", "withheld_path": out.get("path"),
                                           "withheld_response": str(out.get("response", ""))[:400]}})
                return new
        except Exception:  # noqa: BLE001 - a family or network failure never costs the chain's own reply
            return out
        return out
