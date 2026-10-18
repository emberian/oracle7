#!/usr/bin/env python3
"""oracle_release_runtime_w548 - CAPABILITY RELEASE (3.1): THE SPECIALIST THAT KNOWS, AFTER A CHECK STOPPED A ROUTE THAT DID NOT.

Found by the re-examination of release patch 3 (research record E-20261017-0013): through the released model the specialists
kept 10,662 of the 12,153 held-out answers they had at admission. The largest single cause: a precision check (folds
w511/w516) correctly withholds an answer given by a route that could not have computed it - a document page answering
"Differentiate -t^5 - 2t^4 ... with respect to t" - but the turn then ends, and the specialist that can compute it is never
asked. Calculus kept 2 of its 62.

When the chain's reply is withheld by one of the checks that say THE ROUTE COULD NOT KNOW (symbolic maths answered by lookup,
a bare value with no working, a lookup answering a computation over the asker's numbers, a number asked and none given),
the whole standing family (every list the release ships) is asked, with its own arbitration (two specialists that disagree
decline). Its reply is kept only when:
  - exactly one specialist answered and did not decline;
  - if a number was asked, the reply gives one that is not merely one of the question's own;
  - the quantity the question names and the reply's quantity have the same dimension (network v6's learned goal nouns,
    the w547 rule);
  - the reply carries the specialist's name, as every specialist reply does.
Every other withheld turn, every check that says the QUESTION is the problem (impossible givens, private facts, unknown
places, half answers, other bodies) and every deliberate verdict stands as it is. The fold imports no runtime other than
its parent."""
from __future__ import annotations

import importlib.util
import re
import threading

from oracle_release_runtime_w547 import OracleReleaseRuntimeW547 as _Base

SPEC_ROOT = __import__("os").environ.get("ORACLE7_ROOT", "/opt/oracle-clm") + "/specialists"
GATE = SPEC_ROOT + "/_gate"
FAMILY_CODE = GATE + "/combo_runtime_v1.py"
STANDING = ["standing_v2", "standing_new_v1", "standing_new_v2", "standing_new_v3", "standing_new_v4", "standing_new_v5"]
ROUTE_COULD_NOT_KNOW = ("P9_math_by_lookup", "R5_bare_value", "P4_lookup_for_compute", "P2_no_number", "C1_other_derivative",
                        "M1_definitions_not_a_calculation", "A3_other_quantity", "A1_time_not_asked", "A2_property_not_asked")
NUM = re.compile(r"-?\d[\d,]*(?:\.\d+)?")
NUMQ = re.compile(r"^\s*(how many|how much|how long|how far|how fast|how old|convert|calculate|compute)\b|\bin [a-z]+\s*\?\s*$", re.I)
_S: dict = {}
_LOCK = threading.Lock()


def _c548_family():
    with _LOCK:
        if "fam" not in _S:
            spec = importlib.util.spec_from_file_location("o7_combo_runtime_v1_w548", FAMILY_CODE)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            ids = []
            for f in STANDING:
                for s in open("%s/%s.txt" % (GATE, f), encoding="utf-8").read().split():
                    ids += [m for m in s.split("+") if m not in ids]
            _S["fam"] = mod.Family(["%s/%s/manifest.json" % (SPEC_ROOT, i) for i in ids], ["%s/%s" % (SPEC_ROOT, i) for i in ids])
        return _S["fam"]


def _c548_rule(out: dict):
    path = str(out.get("path", ""))
    if out.get("status") != "withheld" or not path.startswith("precision_guard:"):
        return None
    rule = path.split(":", 1)[1].split(">")[0].split("|")[0]
    return rule if rule in ROUTE_COULD_NOT_KNOW else None


def _c548_nums(s):
    out = []
    for m in NUM.finditer(str(s or "")):
        try:
            out.append(float(m.group(0).replace(",", "")))
        except ValueError:
            pass
    return out


class OracleReleaseRuntimeW548(_Base):
    def chat(self, text: str, session_id: str = "default") -> dict:
        out = super().chat(text, session_id=session_id)
        if not isinstance(out, dict):
            return out
        q = str(text or "")
        try:
            rule = _c548_rule(out)
            if not rule:
                return out
            r = _c548_family().reply(q, "guard:%s" % session_id)
            if not r or r.get("status") == "disagree":
                return out                                   # two specialists read it differently: the check's decline stands
            prov = r.get("provenance") or {}
            if prov.get("declined") or prov.get("per_part") or not prov.get("specialist"):
                return out
            resp = str(r.get("response", ""))
            if NUMQ.search(q):
                given = _c548_nums(q)
                if not any(not any(abs(x - g) <= 1e-9 * max(abs(g), 1) for g in given) for x in _c548_nums(resp)):
                    return out                                   # a number was asked and the reply gives none of its own
            want, got = self._c546_dims(q, resp)
            if want is not None and got is not None and want != got:
                return out
            new = dict(out)
            new.update({"status": "answered", "path": "specialist_after_guard>%s>%s" % (rule, r.get("path")),
                        "response": "%s [%s]" % (resp, prov.get("specialist")), "references": [],
                        "provenance": {"kind": "specialist_after_guard", "guard": rule, "guard_path": out.get("path"),
                                       "specialist": prov.get("specialist"), "trace": prov.get("trace")}})
            return new
        except Exception:  # noqa: BLE001 - a family failure never costs the chain's own reply
            return out
