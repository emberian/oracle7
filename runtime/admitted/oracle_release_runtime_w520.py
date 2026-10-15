#!/usr/bin/env python3
"""oracle_release_runtime_w520 - CORRECTNESS RELEASE (presentation only; never changes status, route or what is asserted).

present_v4 - fold w520: presentation only (never changes status, route or what is asserted). Designed on the LIVE format
sweep of head w519 over 8,769 development questions per variant (0.15% of replies flagged, most of them audit false alarms)
and on the RC8 benchmark replies:
  1. a LABEL whose value the store stripped, inside a comma-separated bracket: "(Old Persian: 'Pars', New Persian: , Takht-e
     Jamshid)" -> "(Old Persian: 'Pars', Takht-e Jamshid)"
  2. a bracket group - nested ones included - that still carries debris after every repair is removed whole; these are
     alternate-name / pronunciation brackets: "The Marquesas Islands ( ; or or; Marquesan: (North Marquesan) and (South
     Marquesan), both meaning ...) are ..." -> "The Marquesas Islands are ..."
  3. a supporting sentence that begins with debris because its opening was stripped ("... facility. , Sing Sing housed
     approximately 1,500 inmates ...") is dropped; the answer sentence is never touched
"""
import re

from oracle_release_runtime_w519 import OracleReleaseRuntimeW519 as _Base

SEG_TAG = re.compile(r"(\s*\[(?:ev:[a-z_]+|[a-z]+_[0-9a-f]{6,}|\d+)\])")
SKIP = ("organ:code", "synth", "code", "game:", "self:expression")
DEBRIS = re.compile(r"^\s*[;,:]|[;,]\s*[;,]|\bor\s+or\b|:\s*[;,)]|:\s*$|\(\s*\)|[;,]\s*$|\(\s*[;,:]")
EMPTY_LABEL = re.compile(r"(^|[,;]\s*)[^\W\d][\w\s'’\-]{0,30}:\s*(?=[,;]|$)")


def _groups(s):
    """top-level balanced bracket groups as (start, end) - end exclusive"""
    out, depth, start = [], 0, None
    for i, ch in enumerate(s):
        if ch == "(":
            if depth == 0:
                start = i
            depth += 1
        elif ch == ")" and depth:
            depth -= 1
            if depth == 0:
                out.append((start, i + 1))
    return out


def _fix_group(inner):
    """repair one bracket's content; None = the bracket is debris and goes"""
    new = EMPTY_LABEL.sub(lambda m: m.group(1), inner)
    new = re.sub(r"([,;])\s*(?:[,;]\s*)+", r"\1 ", new)
    new = re.sub(r"^[\s,;:]+|[\s,;:]+$", "", new)
    if not new or DEBRIS.search(new) or re.search(r"\(\s*\)", new):
        return None
    return new


def _segment(s):
    for a, b in reversed(_groups(s)):
        inner = s[a + 1:b - 1]
        if not DEBRIS.search(inner) and not EMPTY_LABEL.search(inner):
            continue
        fixed = _fix_group(inner)
        if fixed is None:
            head = s[:a].rstrip(" ")
            s = head + s[b:] if s[b:b + 1] in (",", ".", ";", ":", ")") else head + " " + s[b:].lstrip(" ")
        elif fixed != inner:
            s = s[:a + 1] + fixed + s[b - 1:]
    # a supporting sentence that opens with debris (its first words were stripped): only after a real sentence end - a word
    # of 3+ letters before the period - and never inside an open bracket ("(pl. ; sign: R$)" is not a sentence)
    for m in reversed(list(re.finditer(r"(?<=[a-z0-9\"'”)]{3}[.!?])\s+[,;:]\s+[^.!?()]*[.!?]", s))):
        if s[:m.start()].count("(") == s[:m.start()].count(")"):
            s = s[:m.start()] + s[m.end():]
    return s


def present4(out):
    if not isinstance(out, dict) or not out.get("response"):
        return out
    r = str(out["response"])
    if str(out.get("path", "")).startswith(SKIP) or "```" in r or re.search(r"\n[ \t]{2,}\S|\bdef \w+\(|\breturn\b", r):
        return out
    parts = SEG_TAG.split(r)
    for i in range(0, len(parts), 2):
        parts[i] = _segment(parts[i])
    s = "".join(parts)
    if s == r:
        return out
    new = dict(out)
    new["response"] = s
    return new


class OracleReleaseRuntimeW520(_Base):

    def chat(self, text: str, session_id: str = "default") -> dict:
        out = super().chat(text, session_id=session_id)
        try:
            return present4(out)
        except Exception:  # noqa: BLE001
            return out
