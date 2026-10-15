#!/usr/bin/env python3
"""oracle_release_runtime_w534 - CORRECTNESS RELEASE: the guards see the FINAL answer, and the conversation sees the
specialists. From SEALED TEST 14 (run once 2026-10-13, RC13c head w533: precision 93.6% / 96.6%, format 0, but 3 false yes
in both variants - bar <= 2) and CONVERSATION TEST 2 (run once, head w533). Two structural defects, both general:

  1. ORDER. The answer guards of w532 (sign kept, private state, date premise) run inside the chain; the specialist
     families folded later (w530's, w533's) answer AFTER them, so a family answer was never checked: "Who painted The
     Starry Night in 1990?" -> Vincent van Gogh (relation family), a false premise answered. And G2 looked only at
     encyclopedia routes: "What is my social security number?" was answered by an explain-simply route. Here the three
     guards run again on the final answer, whatever route produced it, and the private-state rule covers every route
     and the private things people ask about ("my social security number", "what did I dream about"). A question
     carrying quantities to compute with ("my car does 30 mpg ...") is never treated as private.
  2. CONVERSATION. The conversation fold (w529) sits in the middle of the chain: the families folded above it received
     the turn AS TYPED ("When was he born?") instead of the question it stands for, and the conversation state was
     written before their answers existed - so after a specialist answered, the next "he" or "it" had nothing to point
     to. Here the turn is resolved FIRST (the same engine, chat_context_v2.rewrite), the whole stack is asked the
     standalone question, and the conversation state is updated from the FINAL answer (its receipt names the entity).
     A turn the engine splits into parts, or cannot resolve, goes down exactly as typed.
Every guard WITHHOLDS with its reason; nothing here invents an answer. The fold imports no runtime other than its parent;
the conversation engine is called through its own public functions (rewrite, update, split_parts)."""
from __future__ import annotations

import re

from oracle_release_runtime_w533 import OracleReleaseRuntimeW533 as _Base

try:
    import chat_context_v2 as _CC
except Exception:  # noqa: BLE001 - without the engine the conversation part is off; the guards still run
    _CC = None
try:
    import entity_linker_v2 as _EL
    import relation_spec_v1 as _RV
except Exception:  # noqa: BLE001
    _EL = _RV = None

NEG = re.compile(r"(?:^|(?<=[\s(=:,]))[-−]\s?(\d+(?:\.\d+)?)(?![\d.])(?!\s*(?:°|degrees?\b|deg\b|[CFK]\b|celsius|fahrenheit|kelvin))", re.I)
NEG_IN_REPLY = re.compile(r"[-−]\s?\d")
WH = r"(?:what|what's|whats|who|whom|where|when|which|how\s+(?:much|many|old|long))"
PRIVATE_THINGS = (r"social\s+security(?:\s+number)?|ssn|pin|password|passcode|passport(?:\s+number)?|bank(?:\s+account)?|account|"
                  r"balance|salary|income|address|phone(?:\s+number)?|e-?mail|credit\s+card|debit\s+card|card|name|age|birthday|"
                  r"home|house|flat|apartment|car|boss|sister|brother|mother|mum|mom|father|dad|wife|husband|partner|son|daughter|"
                  r"friend|neighbou?r|dog|cat|pet|dreams?|lunch|dinner|breakfast|plans?|schedule|weight|height|blood\s+type|"
                  r"code|key|lock|front\s+door|country|city|town|street|school|job|work|company|team|doctor|bill|order|parcel|flight")
PRIVATE = re.compile(r"\b%s\b[^?]*\bmy\s+(?:\w+\s+){0,2}?(?:%s)\b|\bmy\s+(?:%s)'?s?\s+(?:\w+\s+)?(?:is|are|was|were)\s*\?|"
                     r"\bwhat\s+(?:did|do|will|am|was|shall)\s+i\b(?!\s+(?:need|have\s+to|call|use)\b)|"
                     r"\bwhat\s+(?:number|word|colou?r|card|letter|animal|thing|name)\s+am\s+i\s+thinking\b"
                     % (WH, PRIVATE_THINGS, PRIVATE_THINGS), re.I)
QUANTITY = re.compile(r"\d+(?:\.\d+)?\s*(?:%|kg|g|m|km|mi|miles?|mph|mpg|lbs?|cm|mm|l|litres?|liters?|kwh|kw|w|v|a|hours?|h|minutes?|"
                      r"min|days?|weeks?|months?|°|degrees?|\$|dollars?|euros?|pounds?)\b|\$\s?\d", re.I)
PREMISE = re.compile(r"^\s*(?:who|which \w+)\s+(painted|wrote|composed|sculpted|built|designed|founded|invented|discovered)\s+"
                     r"(?:the\s+)?(.+?)\s+in\s+(\d{3,4})\s*\??\s*$", re.I)
DATE_PROPS = (571, 577, 1191, 575, 580, 585, 1619)
REASON = {"G1_sign_kept": "The question gives a negative quantity and my calculation did not keep the sign, so I won't give that answer.",
          "G2_private_state": "That depends on something only you know; my records can't tell me.",
          "G3_date_premise": "My records date %s to %s, not %d, so I can't answer as the question puts it."}


def sign_dropped(q, reply):
    return bool(NEG.search(q)) and not NEG_IN_REPLY.search(reply)


def private_state(q):
    return bool(PRIVATE.search(q)) and not QUANTITY.search(q)


def premise_years(q):
    m = PREMISE.match(q)
    if not m or _EL is None:
        return None
    x, year = m.group(2).strip(), int(m.group(3))
    try:
        spans = _EL.link(q, k=3)
    except Exception:  # noqa: BLE001
        return None
    key = lambda s: re.sub(r"^the\s+", "", s.strip(), flags=re.I).lower()
    cands = [c for s, cs in spans if key(s) == key(x) for c in cs[:1]]
    if not cands:
        return None
    qid, _, label = cands[0]
    years = set()
    for p in DATE_PROPS:
        for v in _RV.values(qid, p):
            y = re.match(r"^[+]?(-?\d{1,4})-", str(v))
            if y:
                years.add(int(y.group(1)))
    if not years or min(years) - 5 <= year <= max(years) + 2:
        return None
    return label, year, sorted(years)


def _withhold(out, rule, reason):
    new = dict(out)
    path = str(out.get("path", ""))
    new.update({"status": "withheld", "path": "precision_guard:%s|%s" % (rule, path), "response": reason, "references": [],
                "provenance": {"kind": "precision_guard", "rule": rule, "withheld_path": path,
                               "withheld_response": str(out.get("response", ""))[:400]}})
    return new


def final_guards(q, out):
    """the w532 guards, on the FINAL answer of any route"""
    if not isinstance(out, dict) or str(out.get("status", "")) != "answered":
        return out
    path, reply = str(out.get("path", "")), str(out.get("response", ""))
    if path.startswith("precision_guard:"):
        return out
    if "specialist" in path and sign_dropped(q, reply):
        return _withhold(out, "G1_sign_kept", REASON["G1_sign_kept"])
    if private_state(q):
        return _withhold(out, "G2_private_state", REASON["G2_private_state"])
    try:
        pm = premise_years(q)
    except Exception:  # noqa: BLE001
        pm = None
    if pm:
        label, year, years = pm
        return _withhold(out, "G3_date_premise", REASON["G3_date_premise"] % (label, ", ".join(str(y) for y in years[:3]), year))
    return out


class OracleReleaseRuntimeW534(_Base):
    def chat(self, text: str, session_id: str = "default") -> dict:
        q = str(text or "")
        standalone = None
        if _CC is not None:
            try:
                if not _CC.split_parts(q):                       # None = one question (a list = parts, left to w529)
                    s = _CC.rewrite(session_id, q)
                    if isinstance(s, str) and s.strip() and s.strip() != q.strip():
                        standalone = s
            except Exception:  # noqa: BLE001 - an engine failure leaves the turn exactly as typed
                standalone = None
        out = super().chat(standalone or q, session_id=session_id)
        if not isinstance(out, dict):
            return out
        out = final_guards(standalone or q, out)
        if standalone:
            out = dict(out)
            if not str(out.get("path", "")).startswith("chat:"):
                out["path"] = "chat:resolved>" + str(out.get("path"))
            prov = dict(out.get("provenance") or {})
            prov["chat_resolved"] = {"turn": q, "read_as": standalone}
            out["provenance"] = prov
        if _CC is not None:
            try:
                _CC.update(session_id, standalone or q, out)          # the state follows the FINAL answer
            except Exception:  # noqa: BLE001
                pass
        return out
