#!/usr/bin/env python3
"""oracle_release_runtime_w540 - CORRECTNESS RELEASE: three false yeses found by sealed test 18 on RC13h (2026-10-14) become
declines. Narrowing only: every change below withholds an answer the chain gave; none adds one.

1. A QUESTION'S DIRECTION: "Which planet orbits the Moon?" was answered "Earth" by the general relation reader, which read
   the Moon's own parent body. When a question asks for the SUBJECT of its verb ("which N <verb>s E"), a forward reading of
   E is the answer only for relations that name who did it (author, director, architect, founder, winner, head of state...).
   For any other relation (orbits, part of, located in) the forward reading points the wrong way, so it is withheld.
2. A ZERO READ BACK IS NOT A RESULT: "A 5 kg cube has a density of 0 kg/m3. What is its volume?" was answered "0" by
   evaluating a zero copied from the question. An arithmetic answer that is just a zero taken from a worded question is
   withheld (other read-back numbers can be the right answer and are left alone).
3. A PRIVATE QUESTION IS NOT A REQUEST FOR A DEFINITION: "Who is my favourite singer?" was answered with what "singer"
   means. When the conversation route answers a question about the asker's own things (my favourite, my own, our...) with a
   definition from its sources, it is withheld; recalling what the asker said is untouched."""
from __future__ import annotations

import re

from oracle_release_runtime_w411 import OracleReleaseRuntimeW411 as _Base

AGENT_PROPS = {50, 57, 58, 84, 86, 87, 61, 112, 170, 175, 162, 287, 1431, 676, 88, 2554, 344, 1040, 1346, 35, 6, 169, 1037, 286,
               488, 943, 110, 98, 655, 1779, 527, 138, 941, 10, 449, 272, 750, 123, 264, 123, 1408}
AUX = r"(?:is|was|are|were|does|did|do|has|had|have|can|could|will|would|should|may|might)"
# "which N [N] <verb>s ..." with the verb straight after the noun phrase: the asked thing is the verb's SUBJECT
SUBJECT_FORM = re.compile(r"^\s*(?:which|what)\s+(?!%s\b)[a-z\-]+(?:\s+(?!%s\b)[a-z\-]+)?\s+(?!%s\b)[a-z]+(?:s|ed)\b" % (AUX, AUX, AUX), re.I)
READ_BACK = re.compile(r"\bread (-?\d+(?:\.\d+)?); then evaluate\b", re.I)
MATH_PATH = re.compile(r"(^|[>|])(organ:math|op:|algebra:)")
OWN = re.compile(r"\b(my|our)\s+(?:own\s+)?(favou?rite|best|first|last|current|next|usual|own|favou?rites)\b|\b(?:who|what|which|when|where)\b.*\b(my|our)\b", re.I)


def wrong_direction(q, out):
    p = str(out.get("path", "")) if isinstance(out, dict) else ""
    m = re.match(r"general_reader:[a-z]+:P(\d+):(fwd|inv)>", p)
    if not m or m.group(2) != "fwd" or int(m.group(1)) in AGENT_PROPS:
        return False
    return bool(SUBJECT_FORM.search(q))


def read_back(q, out):
    if not isinstance(out, dict) or out.get("status") != "answered" or not MATH_PATH.search(str(out.get("path", ""))):
        return False
    m = READ_BACK.search(str(out.get("response", "")))
    if not m:
        return False
    nums = re.findall(r"-?\d+(?:\.\d+)?", q)
    words = [w for w in re.findall(r"[a-z]+", q.lower()) if w not in ("what", "is", "evaluate", "compute", "calculate", "the", "of")]
    # only a ZERO read back (2026-10-14 pre-check: reading back a given number is right on worded questions whose answer IS
    # that given; the sealed failure was a density of 0 returned as a volume)
    return m.group(1) in nums and float(m.group(1)) == 0 and len(words) >= 3


def own_thing_on_converse(q, out):
    # only the definition dump ("Here's what my sources say about singer") - a conversation that recalls what the asker said
    # ("what is my name?") is right, and stays
    return (isinstance(out, dict) and out.get("status") == "answered" and str(out.get("path", "")).startswith("organ:converse>request")
            and str(out.get("response", "")).lstrip().startswith("Here's what my sources say") and bool(OWN.search(q)))


class OracleReleaseRuntimeW540(_Base):
    def chat(self, text: str, session_id: str = "default") -> dict:
        out = super().chat(text, session_id=session_id)
        q = str(text or "")
        if not isinstance(out, dict):
            return out
        if wrong_direction(q, out):
            prov = out.get("provenance") or {}
            new = dict(out)
            new.update({"status": "withheld", "path": "precision_guard:D1_question_direction>%s" % out.get("path"), "references": [],
                        "response": prov.get("declined_response") or "I can't verify an answer to that exact question, so I won't guess."})
            return new
        if read_back(q, out):
            new = dict(out)
            new.update({"status": "withheld", "path": "precision_guard:N2_number_read_back>%s" % out.get("path"), "references": [],
                        "response": "That would only repeat a number from your question, not work anything out, so I won't answer it."})
            return new
        if own_thing_on_converse(q, out):
            new = dict(out)
            new.update({"status": "withheld", "path": "precision_guard:G3_private_on_converse>%s" % out.get("path"), "references": [],
                        "response": "That depends on something only you know; my records can't tell me."})
            return new
        return out
