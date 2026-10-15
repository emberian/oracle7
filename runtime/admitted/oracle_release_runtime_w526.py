#!/usr/bin/env python3
"""oracle_release_runtime_w526 - CAPABILITY RELEASE: the RELATION SPECIALISTS admitted 2026-10-09 join the core.
Ben 2026-10-08: "the 250 specialists shipped". Each relation specialist reads one Wikidata domain (films, novels, countries,
bridges, painters, footballers, ...) with HAND-WRITTEN readers - whole-question phrasings with an entity slot, every one
measured on 140k natural TRAIN questions first (phrasings below 90% answering precision dropped) - plus that domain's
mined patterns; values are read exactly from the Wikidata relation store (v2, CC0) and every answer carries its receipt
(subject Q-id, property, value). A question it recognises but cannot read reliably is declined in-domain, never guessed.
Each was admitted by spec_gate_v4 (spec_gate_v3.1 criteria; head core results cached per tip, validated identical):
domain gain over the head, no confident wrong answers over the cap, no core item worse.
PINNED family: /opt/oracle-clm/specialists/_gate/standing_new_v2.txt (never edited after this fold is measured), called
exactly as w504 / w525 call theirs - only on turns the whole chain declined; a disagreement leaves the decline standing.
The fold never imports a runtime other than its parent; it touches no other module's state."""
from __future__ import annotations

import importlib.util
import threading

from oracle_release_runtime_w525 import OracleReleaseRuntimeW525 as _Base

SPEC_ROOT = __import__("os").environ.get("ORACLE7_ROOT", "/opt/oracle-clm") + "/specialists"
GATE = SPEC_ROOT + "/_gate"
FAMILY_CODE = GATE + "/combo_runtime_v1.py"
NEW_STANDING = GATE + "/standing_new_v2.txt"
DELIBERATE = ("does_not_follow", "out_of_fragment", "validity")
_S: dict = {}
_LOCK = threading.Lock()


def _c526_family():
    with _LOCK:
        if "fam" not in _S:
            spec = importlib.util.spec_from_file_location("o7_combo_runtime_v1_w526", FAMILY_CODE)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            ids = open(NEW_STANDING, encoding="utf-8").read().split()
            _S["fam"] = mod.Family(["%s/%s/manifest.json" % (SPEC_ROOT, i) for i in ids], ["%s/%s" % (SPEC_ROOT, i) for i in ids])
        return _S["fam"]


def _c526_lacks(out):
    st, path = str(out.get("status", "")), str(out.get("path", ""))
    return st in ("withheld", "clarification") and not path.endswith(DELIBERATE)


class OracleReleaseRuntimeW526(_Base):
    def chat(self, text: str, session_id: str = "default") -> dict:
        out = super().chat(text, session_id=session_id)
        if not isinstance(out, dict) or not _c526_lacks(out):
            return out
        try:
            r = _c526_family().reply(text, "core:%s" % session_id)
        except Exception:  # noqa: BLE001 - a family failure never costs the chain's own reply
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
                    "provenance": {"kind": "core_called_specialist", "family": "new_v2", "core_status": out.get("status"),
                                   "core_path": out.get("path"), "specialist": prov.get("specialist"), "parts": prov.get("parts")}})
        return new
