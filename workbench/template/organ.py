"""__NAME__ - a specialist for Oracle7.

The organ gets the user's turn and returns ONE of:
  None                                                  not mine: the core keeps the turn
  {"kind": "<an accept.kinds entry>", "status": "answered", "response": "..."}      an answer (say where it comes from)
  {"kind": "underspecified", "status": "withheld", "response": "..."}              in my domain, but I cannot answer it
                                                                                      (shown only when the turn carries
                                                                                      the manifest's context_regex words)
Anything it returns with a kind that is not in manifest.json accept.kinds is ignored, so a mistake falls through to the
core instead of reaching the user. Exceptions are ignored the same way.

No language model: answers come from rules, tables and computation you can read. Keep each rule narrow; the exam's
LANE rule fails a specialist that takes general questions."""
import re

CUE = re.compile(r"\b(?:__CUE__)\b", re.I)

# (pattern over the question, answer, kind). Write the answer the way you want it said, with its source.
RULES = [
    # (r"\bboiling point of water\b", "100 degrees C at sea level (101.325 kPa). Source: CRC Handbook.", "fact"),
]


class Organ:
    def answer(self, text, session):
        t = str(text or "").strip()
        if not CUE.search(t):
            return None
        for pat, ans, kind in RULES:
            if re.search(pat, t, re.I):
                return {"kind": kind, "status": "answered", "response": ans}
        return None
