#!/usr/bin/env python3
"""oracle_release_runtime_w524 - CAPABILITY RELEASE: the EXACT relation router answers on the turns the core declines.
Ben 2026-10-08: the release must do what the October films show (their knowledge answers came from this router).

ROUTER (wander-train/exact_router_v1.py): no similarity, no learned weights. A question is answered only when an ADMITTED
pattern names the relation it asks and every linked candidate entity agrees on ONE stored value.
  Patterns (router_mine_v4, 2026-10-06): (asked noun or wh-word, one content word) -> Wikidata property, mined over 124,000
  TriviaQA TRAIN questions on the relation store v2; admitted when the answer through that property is right >= 90% of the
  time on BOTH md5 halves with >= 8 firings in each: 35 patterns, 17 properties (relstore/router_patterns_v4.json).
  Linking (wander-train/entity_linker_v2.py): every English label and alias of the 10.36M Wikidata items with an English
  Wikipedia article (relstore/names_v1.sqlite3, CC0), sitelink count as popularity, case agreement, titles, no numbers.
  Store: relstore/relations_v2.sqlite3 (Wikidata, CC0): relation store v1 + 27.7M facts over 2,456 more properties.
  Refused: yes/no questions, a hidden hop (an unnamed intermediate), a quoted title that is not the linked span, a past-time
  qualifier on a relation that changes over time, blank-node values, patterns that disagree on the property, an answer that
  restates the question.
  Untouched measurements (each read only after its counts): TriviaQA validation 12000-14999 with store v2 + patterns v4:
  20 right / 0 wrong; patterns v3 on store v1: train 80k 30/2 (both alias format), 82k 33/1, validation 0 30/3, 3000 12/2,
  6000 29/3, 9000 31/0.
Never overridden: any turn the core answered, a clarification, the core's deliberate verdicts (does_not_follow,
out_of_fragment, network validity). Only a QUESTION turn (w521's question test) reaches the router. The reply carries its
receipt: subject Q-id, property, value - every answer can be checked against Wikidata by hand.
The fold never imports a runtime other than its parent; w521's question test is reached through sys.modules."""
import sys

from oracle_release_runtime_w393 import OracleReleaseRuntimeW393 as _Base

try:
    import exact_router_v1 as _XR
except Exception:  # noqa: BLE001 - without the router the fold is exactly its parent
    _XR = None

DELIBERATE = ("does_not_follow", "out_of_fragment", "validity")
PROP_LABELS = __import__("os").environ.get("ORACLE7_ROOT", "/opt/oracle-clm") + "/relstore/prop_labels.tsv"
_PL = {}


def _prop_label(p):
    if not _PL:
        try:
            with open(PROP_LABELS, encoding="utf-8") as f:
                for line in f:
                    a, _, b = line.rstrip("\n").partition("\t")
                    if a.startswith("<http://www.wikidata.org/entity/P") and b.endswith('"@en'):
                        _PL[int(a[len("<http://www.wikidata.org/entity/P"):-1])] = b[1:-4]
        except Exception:  # noqa: BLE001
            _PL[-1] = ""
    return _PL.get(p) or "P%d" % p


def _question(q):
    w521 = sys.modules.get("oracle_release_runtime_w521")
    if w521 is not None and hasattr(w521, "question"):
        return w521.question(q)
    return str(q or "").strip().endswith("?")


class OracleReleaseRuntimeW524(_Base):
    def chat(self, text: str, session_id: str = "default") -> dict:
        out = super().chat(text, session_id=session_id)
        if _XR is None or not isinstance(out, dict) or out.get("status") != "withheld":
            return out
        try:
            if any(str(out.get("path", "")).endswith(d) for d in DELIBERATE) or not _question(text):
                return out
            a = _XR.answer(str(text))
            if not a:
                return out
            subj = _XR._load()[1].label(a["subject_qid"]) or "Q%d" % a["subject_qid"]
            plab = _prop_label(a["property"])
            body = "%s. From the Wikidata relation store: %s (Q%d) - %s (P%d) - %s." % (
                a["answer"], subj, a["subject_qid"], plab, a["property"], a["answer"])
            new = dict(out)
            new.update({"status": "answered", "response": "[ev:direct] " + body,
                        "path": "exact_router>LINK>ROUTE:%s>RELATE:P%d>AGREE>READ" % (a["pattern"], a["property"]),
                        "references": ["wd:Q%d" % a["subject_qid"], "wd:P%d" % a["property"]],
                        "provenance": {"kind": "exact_router", "subject_qid": "Q%d" % a["subject_qid"],
                                       "property": "P%d" % a["property"], "pattern": a["pattern"],
                                       "declined_path": out.get("path")}})
            return new
        except Exception:  # noqa: BLE001 - a router failure never costs the core's own reply
            return out
