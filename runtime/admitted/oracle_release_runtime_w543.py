#!/usr/bin/env python3
"""oracle_release_runtime_w543 - CORRECTNESS RELEASE: one name, two people - ask which, never pick one silently. Narrowing
only: the change below turns an answer into a question back; it adds no answer.

Found by the family-harm study (research record E-20261016-0007, 2026-10-16): of 16 questions a relation specialist gets
right alone and the release family gets wrong, 14 are the same name read as two different entities. "What nationality was
Richard Hart?" - the curlers reader read Richard Hart (Q457024), Canada; the actors reader read Richard Hart (Q3430847),
United States; the family's arbitration ranked the two replies and kept one. Neither is a misreading: the question names
two people, and only the asker knows which one is meant. The arbitration never compared WHICH entity each reply was about.

RULE: on a turn the chain answered with a Wikidata receipt ("From the Wikidata relation store: <name> (Q...) - ..."), the
release's relation family (the 161 readers of standing_new_v5, the same family w533 and w536 call) is asked the same
question. Each reply that answers with a receipt is reduced to the entity it read for the name in the question (the
receipt's item whose label the question contains, accents and case ignored; a receipt about an item the question does not
name is a reading of something else). When the chain's answer and the family's replies read the question's name as two or
more different entities AND give two or more different answers, the answer is replaced by a clarification that names each
reading, its record and its answer, and asks which one is meant. When the chain's answer is about an item the question
does not name ("Who was Alexander Downer's father?" -> George Downer's father) and a reader found the item it does name
with a different answer, the answer is withheld. Same entity, or the same answer from every reading: the
answer stands. The study's other two harms (an accent-spelled "Dalí" scored wrong, and an ocean pressure the scorer read
in another unit) are not errors of the reply and are untouched.
A family failure never costs the chain's reply. The fold imports no runtime other than its parent."""
from __future__ import annotations

import importlib.util
import re
import threading
import unicodedata

from oracle_release_runtime_w542 import OracleReleaseRuntimeW542 as _Base

SPEC_ROOT = __import__("os").environ.get("ORACLE7_ROOT", "/opt/oracle-clm") + "/specialists"
GATE = SPEC_ROOT + "/_gate"
FAMILY_CODE = GATE + "/combo_runtime_v1.py"
REL_STANDING = GATE + "/standing_new_v5.txt"
RECEIPT = re.compile(r"From the Wikidata relation store:\s*(.+)", re.S)
ITEM = re.compile(r"([^()\-–—:]+?)\s*\(Q(\d+)\)")
_S: dict = {}
_LOCK = threading.Lock()


def _c543_family():
    with _LOCK:
        if "fam" not in _S:
            spec = importlib.util.spec_from_file_location("o7_combo_runtime_v1_w543", FAMILY_CODE)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            ids = open(REL_STANDING, encoding="utf-8").read().split()
            _S["fam"] = mod.Family(["%s/%s/manifest.json" % (SPEC_ROOT, i) for i in ids], ["%s/%s" % (SPEC_ROOT, i) for i in ids])
        return _S["fam"]


def _fold(s):
    s = unicodedata.normalize("NFKD", str(s or ""))
    return re.sub(r"\s+", " ", "".join(c for c in s if not unicodedata.combining(c))).strip().lower()


def _c543_reading(q, response):
    """-> (qid read for the question's name, label, answer, named) from a receipt, or None. named = the question contains the
    item's label; a receipt naming no item of the question is a reading of something else."""
    resp = str(response or "")
    m = RECEIPT.search(resp)
    if not m:
        return None
    items = [(lab.strip(" .,;'\""), qid) for lab, qid in ITEM.findall(m.group(1))]
    if not items:
        return None
    fq = _fold(q)
    named = [(lab, qid) for lab, qid in items if len(lab) >= 3 and _fold(lab) in fq]
    lab, qid = (named or items)[0]
    answer = re.sub(r"\s+", " ", re.split(r"\.?\s*From the Wikidata relation store:", resp, 1)[0]).strip().rstrip(" .")
    return qid, lab, answer, bool(named)


def _c543_check(q, out, session_id):
    """-> (code, status, response) or None"""
    if out.get("status") != "answered":
        return None
    mine = _c543_reading(q, out.get("response"))
    if not mine:
        return None
    named = {}
    for r in _c543_family()._ask_all(q, "w543:%s" % session_id):
        if r.get("declined"):
            continue
        x = _c543_reading(q, r.get("response"))
        if x and x[3] and x[0] not in named:
            named[x[0]] = (x[1], x[2], r.get("id"))
    if not mine[3]:
        # the chain answered about an item the question does not name, while a reader found the one it does name
        other = [v for k, v in named.items() if _fold(v[1]) != _fold(mine[2])]
        if other:
            return ("S3_other_item", "withheld", "That answer is about %s (Q%s), not the %s you asked about, so I won't give it."
                    % (mine[1], mine[0], other[0][0]))
        return None
    named.setdefault(mine[0], (mine[1], mine[2], None))
    if len(named) < 2 or len({_fold(a) for _, a, _ in named.values()}) < 2:
        return None
    parts = []
    for qid, (lab, ans, sid) in named.items():
        where = (" in my %s records" % sid.split("rel-", 1)[-1].replace("-", " ")) if sid else ""
        parts.append("%s (Q%s)%s, for whom the answer is %s" % (lab, qid, where, ans))
    return ("S2_two_readings", "clarification",
            "My records have more than one %s: %s. Which one do you mean?" % (mine[1], "; ".join(parts)))


class OracleReleaseRuntimeW543(_Base):
    def chat(self, text: str, session_id: str = "default") -> dict:
        out = super().chat(text, session_id=session_id)
        if not isinstance(out, dict):
            return out
        try:
            why = _c543_check(str(text or ""), out, session_id)
        except Exception:  # noqa: BLE001 - a family failure never costs the chain's reply
            why = None
        if why:
            new = dict(out)
            new.update({"status": why[1], "path": "same_name_guard:%s>%s" % (why[0], out.get("path")), "references": [],
                        "response": why[2]})
            return new
        return out
