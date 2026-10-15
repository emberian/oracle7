#!/usr/bin/env python3
"""oracle_release_runtime_w532 - CORRECTNESS RELEASE: three answer guards from SEALED TEST 12 (run once 2026-10-13, RC13
head w406). The sealed bar "false yes <= 2" FAILED with 5 in both variants. Each guard is a general rule over a class of
reply, not over the sealed items (which are spent and never asked again):

  G1 SIGN KEPT - a domain specialist (specialist_call path) answered a question that gives a NEGATIVE quantity with a reply
     that contains no negative number: the sign was dropped (densities: "-5 litres of water" -> 5 kg; springs: "k = -200 N/m"
     -> 20 N). A specialist must not silently change an input. Temperatures (degrees, C, F, K) are exempt (a negative
     temperature is an ordinary input that can give a positive result).
  G2 PRIVATE STATE - an encyclopedia route (factoid:*) answered a question about the asker's own private state ("What is my
     bank account balance?" -> a sentence defining "bank"; "What number am I thinking of?" -> a sentence about number
     lines). Only the asker knows that; no page can answer it.
  G3 DATE PREMISE - "Who painted / wrote / composed / sculpted / built / designed / founded / invented / discovered X in
     YEAR?" where X links to an item whose recorded dates (inception, publication, first performance, discovery, start,
     point in time, opening) are all far from YEAR ("Who painted the Mona Lisa in 1950?" -> Leonardo da Vinci, a false
     premise answered). Tolerance: works may be dated up to 5 years before their recorded date and 2 after.
Each guard WITHHOLDS (status withheld, reason stated); none produces a new answer. The fold never imports a runtime other
than its parent; it touches no other module's state."""
from __future__ import annotations

import re

from oracle_release_runtime_w406 import OracleReleaseRuntimeW406 as _Base

try:
    import entity_linker_v2 as _EL
    import relation_spec_v1 as _RV
except Exception:  # noqa: BLE001 - without the store G3 is off; G1/G2 need nothing
    _EL = _RV = None

NEG = re.compile(r"(?:^|(?<=[\s(=:,]))[-−]\s?(\d+(?:\.\d+)?)(?![\d.])(?!\s*(?:°|degrees?\b|deg\b|[CFK]\b|celsius|fahrenheit|kelvin))", re.I)
NEG_IN_REPLY = re.compile(r"[-−]\s?\d")
PRIVATE = re.compile(r"\b(?:what(?:'s| is| are| was)|how (?:much|many)\b.*?\b(?:is|are|do|did|have)|when (?:is|was)|where (?:is|are))\s+"
                     r"(?:in\s+)?(?:the\s+\w+(?:\s+\w+)?\s+of\s+)?my\b|\bwhat (?:number|word|colou?r|card|letter|animal|thing) am i thinking\b|\bwhat am i thinking\b|"
                     r"\bwhat (?:did|do) i (?:have|eat|say|do)\b", re.I)
PREMISE = re.compile(r"^\s*(?:who|which \w+)\s+(painted|wrote|composed|sculpted|built|designed|founded|invented|discovered)\s+"
                     r"(?:the\s+)?(.+?)\s+in\s+(\d{3,4})\s*\??\s*$", re.I)
DATE_PROPS = (571, 577, 1191, 575, 580, 585, 1619)
WITHHELD = "I can't verify an answer to that exact question, so I won't guess."


def _withhold(out, rule, reason):
    new = dict(out)
    path = str(out.get("path", ""))
    new.update({"status": "withheld", "path": "precision_guard:%s|%s" % (rule, path), "response": reason, "references": [],
                "provenance": {"kind": "precision_guard", "rule": rule, "withheld_path": path,
                               "withheld_response": str(out.get("response", ""))[:400]}})
    return new


def sign_dropped(q, reply):
    return bool(NEG.search(q)) and not NEG_IN_REPLY.search(reply)


def private_state(q):
    return bool(PRIVATE.search(q))


def premise_years(q):
    """(item label, asked year, recorded years) when the asked year contradicts every recorded date, else None."""
    m = PREMISE.match(q)
    if not m or _EL is None:
        return None
    verb, x, year = m.group(1), m.group(2).strip(), int(m.group(3))
    try:
        spans = _EL.link(q, k=3)
    except Exception:  # noqa: BLE001
        return None
    cands = [c for s, cs in spans if s.lower().lstrip("the ").strip() == x.lower().lstrip("the ").strip() for c in cs[:1]]
    if not cands:
        return None
    qid, _, label = cands[0]
    years = set()
    for p in DATE_PROPS:
        for v in _RV.values(qid, p):
            y = re.match(r"^[+]?(-?\d{1,4})-", str(v))
            if y:
                years.add(int(y.group(1)))
    if not years:
        return None
    if min(years) - 5 <= year <= max(years) + 2:
        return None
    return label, year, sorted(years)


class OracleReleaseRuntimeW532(_Base):
    def chat(self, text: str, session_id: str = "default") -> dict:
        out = super().chat(text, session_id=session_id)
        if not isinstance(out, dict) or str(out.get("status", "")) != "answered":
            return out
        q, path, reply = str(text or ""), str(out.get("path", "")), str(out.get("response", ""))
        if path.startswith("specialist_call>") and sign_dropped(q, reply):
            return _withhold(out, "G1_sign_kept", "The question gives a negative quantity and my calculation did not keep the "
                                                  "sign, so I won't give that answer.")
        if path.startswith("factoid:") and private_state(q):
            return _withhold(out, "G2_private_state", "That depends on something only you know; my records can't tell me.")
        try:
            pm = premise_years(q)
        except Exception:  # noqa: BLE001
            pm = None
        if pm:
            label, year, years = pm
            shown = ", ".join(str(y) for y in years[:3])
            return _withhold(out, "G3_date_premise", "My records date %s to %s, not %d, so I can't answer as the question puts it."
                             % (label, shown, year))
        return out
