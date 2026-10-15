#!/usr/bin/env python3
"""oracle_release_runtime_w536 - CORRECTNESS RELEASE: a specialist's receipt names BOTH ends of the fact it read, so the
conversation can point at the answer. Found on the live demo (2026-10-13, head w534): "Who directed Kagemusha?" -> "Akira
Kurosawa. From the Wikidata relation store: Kagemusha (Q854990) - movie director (P57) - Akira Kurosawa." - a forward read
names the subject's id but not the value's, so the conversation engine (chat_context_v2) took the only id it could see - the
film - as the answer, and the next turn "When was he born?" had no person to point to.
RULE: when an answered reply carries a forward receipt whose value has no id, the value's id is read from the relation store
itself - the object of (subject, property) whose label is exactly the value shown - and written into the receipt
("Akira Kurosawa (Q8006)"); the conversation state is then updated from the completed reply. Nothing is linked by
popularity and nothing is guessed: if the store holds no object of that subject and property with exactly that label, the
reply is left as it was. Single-turn answers are unchanged except for the added id.
FAMILY PRECEDENCE (the lesson of path memory's credit data, as a fixed rule): on 4,804 graded DEV questions (TriviaQA
train, Mintaka train, specialist dev exams; never a sealed or reported item), when a relation reader recognises the question,
another route answered it, and the relation family ALSO answered: both right 140, the other route wrong and the family right
34, both wrong 5, the other route right and the family wrong 0 (the "where was X born" route deliberation:where alone: 28
wrong, 8 right). So on a question a relation reader recognises, an answer from any other route is replaced by the relation
family's answer when the family answers (not a decline). When the family does not answer and path memory
(/opt/oracle-clm/specialists/_gate/path_memory_v1.json) says the answering route's verified precision for this shape is
below 0.5 over >= 4 graded answers (same dev data: such answers were 14 wrong, 5 right), the answer is withheld with that
reason. Otherwise it stands.
The fold imports no runtime other than its parent; the conversation engine is updated through its own public update()."""
from __future__ import annotations

import re

import importlib.util
import threading

from oracle_release_runtime_w534 import OracleReleaseRuntimeW534 as _Base

try:
    import chat_context_v2 as _CC
    import relation_spec_v1 as _RV
except Exception:  # noqa: BLE001 - without the store the fold is exactly its parent
    _CC = _RV = None

try:
    import path_memory_v1 as _PM
except Exception:  # noqa: BLE001
    _PM = None
SPEC_ROOT = __import__("os").environ.get("ORACLE7_ROOT", "/opt/oracle-clm") + "/specialists"
FAMILY_CODE = SPEC_ROOT + "/_gate/combo_runtime_v1.py"
STANDING = SPEC_ROOT + "/_gate/standing_new_v5.txt"
RELATION_ROUTES = ("organ:relation", "specialist:rel", "exact_router", "guard", "none")
_S: dict = {}
_LOCK = threading.Lock()


def _family():
    with _LOCK:
        if "fam" not in _S:
            spec = importlib.util.spec_from_file_location("o7_combo_runtime_v1_w536", FAMILY_CODE)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            ids = open(STANDING, encoding="utf-8").read().split()
            _S["fam"] = mod.Family(["%s/%s/manifest.json" % (SPEC_ROOT, i) for i in ids], ["%s/%s" % (SPEC_ROOT, i) for i in ids])
        return _S["fam"]


FWD = re.compile(r"From the Wikidata relation store: (.+?) \(Q(\d+)\) - ([^()]*?) \(P(\d+)\) - ([^()\[\]]+?)\.(\s*(?:\[|$))")


def value_qid(subject_qid, prop, label):
    rs = _RV._rs()
    rows = rs.db.execute("SELECT o FROM fact WHERE s=? AND p=?", (subject_qid, prop)).fetchall()
    want = label.strip().lower()
    hits = [o for (o,) in rows if o and (rs.label(o) or "").strip().lower() == want]
    return hits[0] if len(hits) == 1 else None


def complete_receipt(response):
    m = FWD.search(response or "")
    if not m:
        return None
    try:
        q = value_qid(int(m.group(2)), int(m.group(4)), m.group(5))
    except Exception:  # noqa: BLE001
        return None
    if not q:
        return None
    return response[:m.start(5)] + "%s (Q%d)" % (m.group(5), q) + response[m.end(5):]


class OracleReleaseRuntimeW536(_Base):
    def chat(self, text: str, session_id: str = "default") -> dict:
        out = super().chat(text, session_id=session_id)
        if _RV is None or not isinstance(out, dict) or out.get("status") != "answered":
            return out
        q = ((out.get("provenance") or {}).get("chat_resolved") or {}).get("read_as") or str(text or "")
        # FAMILY PRECEDENCE on questions a relation reader recognises
        if _PM is not None:
            try:
                route = _PM.route_of(out.get("path"))
                if not route.startswith(RELATION_ROUTES) and _PM.relation_key(q) != "none":
                    f = _family().reply(q, "prec:%s" % session_id)
                    fp = (f or {}).get("provenance") or {}
                    p0 = None
                    try:
                        p0 = _PM.PathMemory.load(SPEC_ROOT + "/_gate/path_memory_v1.json").precision(_PM.shape(q), route, min_n=4) \
                            if "pm" not in _S else _S["pm"].precision(_PM.shape(q), route, min_n=4)
                    except Exception:  # noqa: BLE001
                        p0 = None
                    if not (f and f.get("status") == "answered" and not fp.get("declined")) and p0 and p0[0] < 0.5:
                        # LOW-CREDIT ROUTE, no family answer: on the same dev data this route was wrong 14 times and right 5
                        out = dict(out)
                        out.update({"status": "withheld", "path": "family_precedence:low_credit|" + str(out.get("path")),
                                    "response": "The route that answered this kind of question has been wrong too often when checked, "
                                                "and my relation records can't confirm it, so I won't give that answer.",
                                    "references": [], "provenance": {"kind": "family_precedence", "withheld_route": route,
                                                                     "route_precision": round(p0[0], 3), "n": p0[1],
                                                                     "withheld_response": str(out.get("response", ""))[:300]}})
                        return out
                    if f and f.get("status") == "answered" and not fp.get("declined") and not fp.get("per_part"):
                        out = dict(out)
                        out.update({"status": "answered", "path": "family_precedence>specialist_call>" + str(f.get("path")),
                                    "response": "%s [%s]" % (f["response"], fp.get("specialist")), "references": [],
                                    "provenance": {"kind": "family_precedence", "replaced_route": route,
                                                   "replaced_response": str(out.get("response", ""))[:300],
                                                   "specialist": fp.get("specialist"), "chat_resolved": (out.get("provenance") or {}).get("chat_resolved")}})
                        if _CC is not None:
                            _CC.update(session_id, q, out)
            except Exception:  # noqa: BLE001
                pass
        done = complete_receipt(str(out.get("response", "")))
        if not done:
            return out
        new = dict(out)
        new["response"] = done
        if _CC is not None:
            try:
                _CC.update(session_id, q, new)
            except Exception:  # noqa: BLE001
                pass
        return new
