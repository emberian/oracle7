#!/usr/bin/env python3
"""oracle_release_runtime_w554 - CAPABILITY RELEASE (3.2, with 3.3's work): THE STAR SPECIALISTS, THEN OWNER-FIRST.

w552 and w553 in one fold (submitted together to save a gate cycle; their code is unchanged and runs in the same order, so
the turn behaves exactly as the w551 -> w552 -> w553 chain whose regression, route and false-yes checks were run):
  1. STAR SPECIALISTS (w552): when the parent turn did not answer, the four star specialists admitted on 2026-10-18
     (#214 stars, #215 habzone, #216 exoorbits, #217 transits; standing_stars_v1.txt) are asked through the release's own
     combiner; a reply is kept only when exactly one answered it ("rule": "only") and did not decline.
  2. OWNER-FIRST (w553): when the turn is still not answered, the whole standing family plus the admitted specialists no list
     carried (standing_owner_v1.txt: #18 orbits) is asked; an answer is kept only when one specialist gave it, it is not the
     specialist the parent already stopped, EVERY number the question gives moves it (counterfactual dependence - the test
     that refuses the astronomy reader's "29.8 km/s" for a satellite 400 km above Earth), and, if a number was asked, it gives
     one that is not merely one of the question's own.
Found by the research record (re-examination E-20261018-0043, together vs alone E-20261018-0033: answers lost when the
wrong specialist takes a question; #18 orbits admitted but in no standing list). Deliberate declines of a question that is
itself the problem (private, impossible, future, fictional, a false premise, an unknown place or body, half an answer) stand.
The fold imports no runtime other than its parent and changes no module state of any other fold."""
from __future__ import annotations

import importlib.util
import re
import threading

from oracle_release_runtime_w551 import OracleReleaseRuntimeW551 as _Base

SPEC_ROOT = __import__("os").environ.get("ORACLE7_ROOT", "/opt/oracle-clm") + "/specialists"
GATE = SPEC_ROOT + "/_gate"
FAMILY_CODE = GATE + "/combo_runtime_v1.py"
STAR_STANDING = GATE + "/standing_stars_v1.txt"
LISTS = ["standing_v2", "standing_new_v1", "standing_new_v2", "standing_new_v3", "standing_new_v4", "standing_new_v5", "standing_stars_v1",
         "standing_owner_v1"]
STARS_STAND = ("private", "impossible", "future", "fiction", "premise", "unknown_place", "other_body", "half_answer")
OWNER_STANDS = STARS_STAND + ("identity", "self", "act:")
SPEC_IN_PATH = re.compile(r"\bspecialist:([a-z0-9][a-z0-9-]*)")
NUM = re.compile(r"-?\d[\d,]*(?:\.\d+)?")
NUMQ = re.compile(r"^\s*(how many|how much|how long|how far|how fast|how old|convert|calculate|compute|what is the)\b|\bin [a-z]+\s*\?\s*$", re.I)
_S: dict = {}
_LOCK = threading.Lock()


def _load(key, lists):
    with _LOCK:
        if key not in _S:
            spec = importlib.util.spec_from_file_location("o7_combo_runtime_v1_w554_" + key, FAMILY_CODE)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            ids = []
            for f in lists:
                for s in open("%s/%s.txt" % (GATE, f), encoding="utf-8").read().split():
                    ids += [m for m in s.split("+") if m not in ids]
            _S[key] = (mod.Family(["%s/%s/manifest.json" % (SPEC_ROOT, i) for i in ids], ["%s/%s" % (SPEC_ROOT, i) for i in ids]), mod)
        return _S[key]


def _nums(s):
    out = []
    for m in NUM.finditer(str(s or "")):
        try:
            out.append(float(m.group(0).replace(",", "")))
        except ValueError:
            pass
    return out


class OracleReleaseRuntimeW554(_Base):
    def _stars(self, text, session_id, r):
        """w552, unchanged"""
        low = str(r.get("path", "")).lower()
        if any(k in low for k in STARS_STAND):
            return r
        try:
            f = _load("stars", ["standing_stars_v1"])[0].reply(text, "w552" + str(session_id)[:30])
        except Exception:  # noqa: BLE001 - a specialist failure never breaks the turn; the parent's reply stands
            return r
        if not f or f.get("status") != "answered":
            return r
        prov = f.get("provenance") or {}
        if (prov.get("trace") or {}).get("rule") != "only" or prov.get("declined"):
            return r
        out = dict(r)
        out.update(status="answered", response=str(f.get("response", "")) + " [%s]" % prov.get("specialist", ""),
                   path="specialist_call>" + str(f.get("path", "")), references=f.get("references", []))
        out.pop("why", None)
        return out

    def _owner(self, text, session_id, r):
        """w553, unchanged"""
        path = str(r.get("path", ""))
        if any(k in path.lower() for k in OWNER_STANDS):
            return r
        consulted = set(SPEC_IN_PATH.findall(path))
        try:
            fam, mod = _load("owner", LISTS)
            with _LOCK:
                chosen, trace = fam._one(text, "w553" + str(session_id)[:30])
                if chosen is None or chosen.get("declined") or chosen.get("status") != "answered":
                    return r
                sid = chosen.get("id") or getattr(chosen.get("_organ"), "id", None)
                if not sid or sid in consulted:
                    return r
                givens = mod._givens(text)
                if givens and fam._dependence(chosen, text, givens) < len(givens):
                    return r
        except Exception:  # noqa: BLE001 - a specialist failure never breaks the turn; the parent's reply stands
            return r
        resp = str(chosen.get("response", ""))
        if NUMQ.search(text):
            given = _nums(text)
            if not [v for v in _nums(resp) if not any(abs(v - g) <= 1e-9 * max(1.0, abs(g)) for g in given)]:
                return r
        out = dict(r)
        out.update(status="answered", response=resp + " [%s]" % sid, references=chosen.get("references", []),
                   path="owner_first>specialist_call>specialist:%s>%s" % (sid, chosen.get("kind", "")))
        out.pop("why", None)
        return out

    def chat(self, text: str, session_id: str = "default") -> dict:
        r = super().chat(text, session_id)
        if not isinstance(r, dict) or r.get("status") == "answered":
            return r
        r = self._stars(text, session_id, r)
        if r.get("status") == "answered":
            return r
        return self._owner(text, session_id, r)
