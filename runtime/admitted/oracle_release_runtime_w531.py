#!/usr/bin/env python3
"""oracle_release_runtime_w531 - CAPABILITY RELEASE: GENERAL MATHEMATICS READER (Ben 2026-10-11: "more robust and general";
"massive on the benchmarks").
The maths agent (w521/w522, math_solver_v3) reads a fixed set of problem families with its own TeX reader; on MATH TRAIN it
declined most short, directly computable problems - its reader did not know ordinary notation (log_b, |x|, sums, binomials,
factorials, inequalities, exponent equations) and it did not read the ASKED OPERATION ("the positive difference between the
solutions", "the degree of the polynomial", "the units digit"). wander-train/math_general_v1.py is the general form: sympy's
own LaTeX parser (antlr runtime 4.11.1 vendored at /opt/oracle-clm/vendor, BSD-3 - a parser, not a model), the asked
operation read in mathematics' own vocabulary, exact computation CHECKED by a second method (numeric agreement / residual 0 /
agreement at test points), and declines for word problems, unread operations and anything unchecked.
MEASURED on MATH TRAIN (700, never MATH-500 or the release windows): 32 right / 0 wrong; 20 of them problems the maths agent
declines (0 wrong among them). The agent alone: 35 right.
RULE: on a turn the whole chain declined (not a deliberate verdict) that carries TeX, and only when the maths agent also
declines, the general reader is asked (4 s bound, forked); its checked answer is the reply, in the maths agent's own format.
TeX RULE (application audit 2026-10-11, audit_v1 + route_rules_dev_v1 on dev replies, never release windows): on a TeX
question, an answer from any route other than the checked maths agents is withheld (removed 10 wrong for 1 right: SQL,
statistics and geometry specialists, premise echoes, conversation acts answering competition maths).
The fold never imports a runtime other than its parent; it touches no other module's state."""
from __future__ import annotations

import re

from oracle_release_runtime_w530 import OracleReleaseRuntimeW530 as _Base

try:
    import math_general_v1 as _MG
    import math_solver_v3 as _MS3
except Exception:  # noqa: BLE001 - without the reader the fold is exactly its parent
    _MG = _MS3 = None

DELIBERATE = ("does_not_follow", "out_of_fragment", "validity")
TEX = re.compile(r"\$[^$]+\$|\\\[|\\\(")


MATHS_AGENTS = ("agent:maths", "chat:resolved>agent:maths")
WITHHELD = "I can't verify an answer to that exact question, so I won't guess."


class OracleReleaseRuntimeW531(_Base):
    def chat(self, text: str, session_id: str = "default") -> dict:
        out = super().chat(text, session_id=session_id)
        if _MG is None or not isinstance(out, dict):
            return out
        st, path = str(out.get("status", "")), str(out.get("path", ""))
        q = str(text or "")
        tex = bool(TEX.search(q)) and not ("Options:" in q and "(A)" in q)
        if tex and st == "answered" and not path.startswith(MATHS_AGENTS):
            # TeX RULE (audit 2026-10-11, dev replies never release windows): on a competition-maths question, answers from
            # non-maths routes were wrong 10 times for 1 right (SQL / statistics / geometry specialists, premise echo,
            # conversation acts). Only the CHECKED maths agents answer such a question; the general reader is tried below.
            out = dict(out)
            out.update({"status": "withheld", "path": "precision_guard:R_tex_not_maths_agent|%s" % path, "response": WITHHELD,
                        "references": [], "provenance": {"kind": "precision_guard", "rule": "R_tex_not_maths_agent",
                                                         "withheld_path": path, "withheld_response": str(out.get("response", ""))[:400]}})
            st, path = "withheld", out["path"]
        if st not in ("withheld", "clarification") or path.endswith(DELIBERATE):
            return out
        if not tex:
            return out
        try:
            r = _MG.compute_bounded(q, 4.0)
        except Exception:  # noqa: BLE001
            return out
        if not r or not r.get("answer"):
            return out
        new = dict(out)
        new.update({"status": "answered", "path": "agent:maths_general>checked",
                    "response": _MS3.reply(r) + " [maths agent]", "references": [], "verified_warrant": r["check"],
                    "provenance": {"kind": "agent", "agent": "maths_general", "check": r["check"],
                                   "core_status": st, "core_path": path}})
        return new
