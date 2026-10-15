#!/usr/bin/env python3
"""oracle_release_runtime_w518 - CORRECTNESS RELEASE (presentation only; never changes status, route or what is asserted).

Sealed test 9 (run once on full, on a harness later found contaminated, so retired) showed one reply with a separator doubled
where the store stripped a pronunciation between two commas: "Maria Salomea Sklodowska Curie, , better known as Marie
Curie". Presentation v2 (w517) cleaned such debris only INSIDE brackets. This fold collapses a run of separators in prose
("x, , y" -> "x, y"; "x; ; y" -> "x; y"; "x ,; y" -> "x, y"), outside code, games and drawings, and never inside an
evidence tag."""
import re

from oracle_release_runtime_w517 import OracleReleaseRuntimeW517 as _Base

_TAG = re.compile(r"(\s*\[(?:ev:[a-z_]+|[a-z]+_[0-9a-f]{6,}|\d+)\])")
_SKIP = ("organ:code", "synth", "code", "game:", "self:expression")


def present3(out):
    if not isinstance(out, dict) or not out.get("response"):
        return out
    r = str(out["response"])
    if str(out.get("path", "")).startswith(_SKIP) or "```" in r or re.search(r"\n[ \t]{2,}\S|\bdef \w+\(|\breturn\b", r):
        return out
    parts = _TAG.split(r)
    for i in range(0, len(parts), 2):
        parts[i] = re.sub(r"(?<=\S)\s*([,;])(?:\s*[,;])+(?=\s)", r"\1", parts[i])
    s = "".join(parts)
    if s == r:
        return out
    new = dict(out)
    new["response"] = s
    return new


class OracleReleaseRuntimeW518(_Base):

    def chat(self, text: str, session_id: str = "default") -> dict:
        out = super().chat(text, session_id=session_id)
        try:
            return present3(out)
        except Exception:  # noqa: BLE001
            return out
