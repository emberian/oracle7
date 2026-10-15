#!/usr/bin/env python3
"""oracle_release_runtime_w537 - CORRECTNESS RELEASE: family precedence never swallows a multi-part turn. Found by SEALED
CONVERSATION TEST 4 (run once 2026-10-13, head w536): "Who wrote Daniel Deronda, and who wrote Cranford?" had been answered
part by part (chat:parts, 2 of 2); w536's family-precedence rule saw a question a relation reader recognises answered by a
non-relation route ("chat:parts") and replaced the WHOLE turn with the relation family's answer to its first part - the
second answer was lost. Sealed test 16 (single questions) could not see it; the dialogue test did.
RULE: when the final answer is a family-precedence replacement and the turn holds two or more questions (the conversation
engine's own split_parts, or two wh-questions joined by "and"), each part is answered by the whole pipeline in its own
sub-session (so precedence applies per part, where it belongs) and the replies are joined; a part nothing answers is said to
be uncovered, never guessed. A single question is untouched (single-turn answers are byte-identical to w536's).
The fold imports no runtime other than its parent."""
from __future__ import annotations

import re

from oracle_release_runtime_w536 import OracleReleaseRuntimeW536 as _Base

try:
    import chat_context_v2 as _CC
except Exception:  # noqa: BLE001
    _CC = None

MULTI = re.compile(r"\s*,?\s+and\s+(?=(?:what|who|whom|where|when|which|how|in what|in which|on what)\b)", re.I)
QSTART = re.compile(r"^\s*(?:what|who|whom|whose|where|when|which|why|how|is|are|was|were|do|does|did|can|could|name|tell me|in what|"
                    r"in which|on what)\b", re.I)


def parts_of(q):
    if _CC is not None:
        try:
            p = _CC.split_parts(q)
            if p and len(p) >= 2:
                return p
        except Exception:  # noqa: BLE001
            pass
    p = [x.strip() for x in MULTI.split(q) if x.strip()]
    return p if 2 <= len(p) <= 3 and QSTART.match(p[0]) else None


class OracleReleaseRuntimeW537(_Base):
    def chat(self, text: str, session_id: str = "default") -> dict:
        out = super().chat(text, session_id=session_id)
        if not isinstance(out, dict) or (out.get("provenance") or {}).get("kind") != "family_precedence":
            return out
        q = ((out.get("provenance") or {}).get("chat_resolved") or {}).get("read_as") or str(text or "")
        parts = parts_of(q)
        if not parts:
            return out
        replies, paths = [], []
        for i, p in enumerate(parts):
            p = p if p.rstrip().endswith("?") else p.rstrip(" .") + "?"
            try:
                r = super().chat(p, session_id="%s#part%d" % (session_id, i))
            except Exception:  # noqa: BLE001
                r = None
            ok = isinstance(r, dict) and r.get("status") == "answered"
            replies.append(str(r.get("response", "")) if ok else "(I can't verify an answer to: \"%s\")" % p)
            paths.append(str((r or {}).get("path")))
        answered = sum(1 for x in replies if not x.startswith("(I can't verify"))
        if not answered:
            return out
        new = dict(out)
        new.update({"status": "answered", "path": "chat:parts_w537>%d of %d" % (answered, len(parts)), "response": " ".join(replies),
                    "references": [], "provenance": {"kind": "parts_after_precedence", "parts": [{"part": p, "path": pp} for p, pp in zip(parts, paths)],
                                                     "chat_resolved": (out.get("provenance") or {}).get("chat_resolved")}})
        return new
