#!/usr/bin/env python3
"""oracle_release_runtime_w529 - CAPABILITY RELEASE: CONVERSATION (w527 resubmitted on the v2 engine - w527 was REJECTED
2026-10-09 03:53Z, 1249 -> 1247: its multi-part splitter cut a reading passage and "Everything is fine, and how are you?";
the splitter now splits only when every part is a question the relation readers can read, and both items score as on the
head. v2 engine (wander-train/chat_context_v2.py; v1 stays FROZEN - the head reads its recognised()): the TOPIC - the named
entity a conversation is about - "the book" / "this movie" / "it" resolve to it, and a FACTUAL wh-question whose rewrite
names that entity is accepted ("Who directed it?" -> "Who directed Bird Box?"); conversation acts never rewritten.)
Original w527 description: A follow-up is read through the conversation.
Ben 2026-10-09: "we have what we need for a proper chat model ... we can 10x chat capability easily now".
Measured before this fold (open dev dialogues, head w525): 32% of turns handled; follow-ups 1 of 22 - "Where was he born?"
was answered with an article about the word "he", "And of Iceland?" was summarised as a topic, "What does that cost?" asked
what "that" was. The core refused or misread because it never saw the conversation.

This fold keeps a small dialogue state per session (wander-train/chat_context_v1.py) and turns a turn that only makes sense
through the conversation into the standalone question it stands for - pronouns to the person or thing in play, ellipsis
("And its currency?", "And of Denmark?", "And on the Moon?", "Where?"), carried results ("that" = the previous result or
material, "x" = the solved x), and two-question turns split and answered part by part. The rewritten question is then
answered by the WHOLE chain exactly as if it had been asked outright: the fold asserts nothing of its own, and the reading
it used is shown in the path ("chat:resolved>...") and provenance. A turn with nothing to resolve is passed through unchanged.
NARROWED (2026-10-09, after the m52 replay showed 34 route changes - "got it", "why?", "did you run it?", "how does it work?"
rewritten away from the core's own conversation acts): a rewrite is ACCEPTED only when it is exactly right for the verified
layer - a relation rewrite must be a question the hand-written relation readers recognise; a numeric rewrite must continue a
numeric answer. The clarifying question for an unresolved pronoun is asked only on a turn the readers recognise. The dialogue
state takes context from FACTUAL turns only, and an entity already resolved keeps its identity (the reply's own receipt or
typed relation names it). m52 replay after narrowing: 0 route changes.
The fold never imports a runtime other than its parent; it touches no other module's state."""
from __future__ import annotations

from oracle_release_runtime_w399 import OracleReleaseRuntimeW399 as _Base

try:
    import chat_context_v2 as _CC
except Exception:  # noqa: BLE001 - without the engine the fold is exactly its parent
    _CC = None


import re  # noqa: E402

_RESULT = re.compile(r"(?:The answer is|is about|emits about|releases about|takes about|lands at about|=)\s+(\$?-?\d[\d,]*(?:\.\d+)?(?:e[+-]?\d+)?(?:\s*(?:kWh|kJ|MJ|J|kg|g|m/s|m|km|s|N|Pa|kPa|W|kW|L|m³|°C|%)\b)?)")


def _c527_answer_first(resp):
    """a follow-up computed through the conversation is answered ANSWER FIRST (the speaker's order): "In steps: 8 ^ 2 = 64.
    The answer is 64." -> "64. In steps: ..."; the rest of the reply - its working and receipt - is kept unchanged"""
    found = list(_RESULT.finditer(resp))
    if not found:
        return resp
    stated = [x for x in found if "answer is" in x.group(0).lower()]
    m = stated[0] if stated else found[0]          # "The answer is ..." when present, else the FIRST stated result
    lead = m.group(1).strip()
    if resp.lstrip().startswith(lead):
        return resp
    return "%s. %s" % (lead, resp)


class OracleReleaseRuntimeW529(_Base):
    def chat(self, text: str, session_id: str = "default") -> dict:
        if _CC is None:
            return super().chat(text, session_id=session_id)
        try:
            parts = _CC.split_parts(text)
        except Exception:  # noqa: BLE001
            parts = None
        if parts:
            return self._c527_parts(text, parts, session_id)
        try:
            standalone = _CC.rewrite(session_id, text)
        except Exception:  # noqa: BLE001
            standalone = None
        if isinstance(standalone, tuple) and standalone[0] == _CC.UNRESOLVED:
            # a short turn whose pronoun refers to nothing in this conversation: ask, never let the pronoun be read as the
            # topic (the core answered "Where was he born?" with an article about the word "he")
            return {"status": "clarification", "path": "chat:unresolved>%s" % standalone[1],
                    "response": "Who do you mean by \"%s\"? Nothing earlier in our conversation names them - tell me the name and I'll check."
                                % standalone[1], "references": [], "provenance": {"kind": "chat_unresolved", "pronoun": standalone[1]}}
        out = super().chat(standalone or text, session_id=session_id)
        try:
            _CC.update(session_id, standalone or text, out)
        except Exception:  # noqa: BLE001
            pass
        if standalone and isinstance(out, dict):
            new = dict(out)
            new["path"] = "chat:resolved>" + str(out.get("path"))
            if out.get("status") == "answered":
                new["response"] = _c527_answer_first(str(out.get("response", "")))
            prov = dict(out.get("provenance") or {})
            prov["chat_resolved"] = {"turn": text, "read_as": standalone}
            new["provenance"] = prov
            return new
        return out

    def _c527_parts(self, text, parts, session_id):
        replies, answered, read = [], 0, []
        for p in parts:
            try:
                standalone = _CC.rewrite(session_id, p) or p
            except Exception:  # noqa: BLE001
                standalone = p
            if not isinstance(standalone, str):
                standalone = p                             # an unresolved pronoun inside a part: the part goes as written
            r = super().chat(standalone, session_id=session_id)
            try:
                _CC.update(session_id, standalone, r)
            except Exception:  # noqa: BLE001
                pass
            read.append(standalone)
            if isinstance(r, dict) and r.get("status") == "answered":
                answered += 1
                replies.append(str(r.get("response", "")).strip())
            else:
                replies.append("(%s) I can't verify an answer to that part, so I won't guess." % standalone.rstrip("?"))
        return {"status": "answered" if answered else "withheld", "path": "chat:parts>%d of %d" % (answered, len(parts)),
                "response": " ".join(replies), "references": [],
                "provenance": {"kind": "chat_parts", "turn": text, "read_as": read, "answered": answered}}
