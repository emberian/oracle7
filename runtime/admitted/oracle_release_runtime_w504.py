#!/usr/bin/env python3
"""oracle_release_runtime_w504 - CAPABILITY RELEASE: the core CALLS its specialists for knowledge it lacks.

Ben 2026-09-29: "we need a way ... for the core to call specialists for knowledge it lacks". Until now a specialist sat
IN FRONT of the core (spec_runtime / combo_runtime): the core itself never reached one. This fold keeps the core first
and unchanged, and only where the core would decline for want of knowledge - status withheld or clarification - it
calls the whole standing family (99 specialists, /opt/oracle-clm/specialists, combo_runtime_v1.Family: per-organ
isolation, counterfactual arbitration, multi-question turns answered part by part) and answers with the specialist's
reply, labelled with the specialist that gave it.
Never overridden: the core's deliberate verdicts (paths ending does_not_follow / out_of_fragment), any turn the core
answered, and any family reply that is a disagreement between two specialists (the core's own decline stands). A
specialist's own checked decline ("impossible") replaces the core's generic one but stays a decline (status withheld).
Family measured before this fold (box four, dev + core panel only): 99 organs in one process reproduce each organ's
own-process behaviour; 40 of the 3107 core items are taken by some specialist, none by two.
Parent: w503. Methods _c504_."""

from __future__ import annotations

import importlib.util
import threading

from oracle_release_runtime_w366 import OracleReleaseRuntimeW366 as _Base

SPEC_ROOT = __import__("os").environ.get("ORACLE7_ROOT", "/opt/oracle-clm") + "/specialists"
FAMILY_CODE = SPEC_ROOT + "/_gate/combo_runtime_v1.py"
STANDING = SPEC_ROOT + "/_gate/standing_v1.txt"
DELIBERATE = ("does_not_follow", "out_of_fragment")
_FAM: dict = {}
_LOCK = threading.Lock()


def _c504_family():
    with _LOCK:
        if "f" not in _FAM:
            spec = importlib.util.spec_from_file_location("o7_combo_runtime_v1", FAMILY_CODE)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            ids = open(STANDING, encoding="utf-8").read().split()
            _FAM["f"] = mod.Family(["%s/%s/manifest.json" % (SPEC_ROOT, i) for i in ids], ["%s/%s" % (SPEC_ROOT, i) for i in ids])
        return _FAM["f"]


def _c504_lacks(out: dict) -> bool:
    st, path = str(out.get("status", "")), str(out.get("path", ""))
    return st in ("withheld", "clarification") and not path.endswith(DELIBERATE)


class OracleReleaseRuntimeW504(_Base):

    def chat(self, text: str, session_id: str = "default") -> dict:
        out = super().chat(text, session_id=session_id)
        if not isinstance(out, dict) or not _c504_lacks(out):
            return out
        try:
            r = _c504_family().reply(text, "core:%s" % session_id)
        except Exception:  # noqa: BLE001 - a family failure never costs the core's own reply
            return out
        if not r or r.get("status") == "disagree":
            return out
        prov = r.get("provenance") or {}
        if prov.get("per_part"):
            if not any(p.get("specialist") and not p.get("declined") for p in (prov.get("parts") or [])):
                return out
            status, response = "answered", r["response"]
        else:
            status = "withheld" if prov.get("declined") else "answered"
            response = "%s [%s]" % (r["response"], prov.get("specialist"))
        new = dict(out)
        new.update({"status": status, "path": "specialist_call>" + str(r.get("path")), "response": response, "references": [],
                    "provenance": {"kind": "core_called_specialist", "core_status": out.get("status"), "core_path": out.get("path"),
                                   "specialist": prov.get("specialist"), "parts": prov.get("parts"), "trace": prov.get("trace")}})
        return new
