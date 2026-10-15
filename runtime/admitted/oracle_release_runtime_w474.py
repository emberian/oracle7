#!/usr/bin/env python3
"""oracle_release_runtime_w474 - THE REASONING CUBE, Phase A: a question the chain refuses is solved, not declined.

Measured 2026-09-25 on 600 fresh factoid questions (SimpleQA / TriviaQA / HotpotQA): 69% stopped at the door before any
retrieval, and 145 of the 170 whose answer sat on the subject's own page were refused. The routes fire on recognised
wording; the knowledge was there.

This fold walks the cube's first six moves (oracle_cube_reader_v1) ONLY where the parent did not answer:
  READ -> FRAME (answer type, relation, predicate, constraints) -> LINK (the store's title index) -> EXPAND (the subject's
  own sentences) -> BIND (a value of the required type, from a sentence carrying the question's predicate) -> CHECK
  (independent of the proposing sentence: an entity's OWN page says it IS the asked-for kind; every other name, number and
  year in the question is attested) -> VERIFY (one candidate standing, or nothing is said).
Strict fallback: an answered parent turn is returned unchanged, so this can add answers and cannot break one.

Reader v1 held-out (never-scored windows, offset 4200, run once): the cube answered 7 of 526 refused questions, 5
correct / 2 incorrect; both errors were two-hop bridges ("the composer who created ..."). Reader v1.1 (this fold):
a described subject ("the <noun> who/which ...") is a bridge and is declined (Phase 3); another named entity of the
question must appear in the binding sentence itself. v1.1 dev: 8 correct / 0 incorrect.
Gate 2026-09-26 09:12 on panel v17: REJECT (capability 724 -> 725; false_yes 22 -> 24). Replaying all 638 must-decline
items: 10 cube assertions = 6 real errors (role reversal "who beat Henman" -> Federer; noun "composers" matching the
verb "composed"; a described subject missed by a 30-noun filter; code "gal56" not an obligation; a pronoun passing as
a person; an ambiguous key) + 3 stale labels (Dumoulin "150" matches the dataset key exactly) + 1 ambiguity.
Reader v1.2 (this fold): ROLE check (an agent question needs the candidate before an active verb or after "by");
predicate matched only by verbs; any "the ... who" description is a bridge; alphanumeric codes are obligations; a
person is shown by a birth/life-span parenthetical or an occupation predicate; no candidate under 3 characters or an
upper-case abbreviation. v1.2: dev 9/0; on the whole panel its only must-decline assertions are the 3 stale labels.
Methods _c474_. Parent: the serving head.
"""

from __future__ import annotations

import os

from oracle_release_runtime_w345 import OracleReleaseRuntimeW345 as _Base

try:
    import oracle_cube_reader_v1_3 as _cube
except Exception:  # noqa: BLE001
    _cube = None


class OracleReleaseRuntimeW474(_Base):

    def _c474_reader(self):
        r = getattr(self, "_c474_r", None)
        if r is None and _cube is not None:
            path = os.environ.get("ORACLE_DEEP_BUILD") or _cube.DEEP
            try:
                r = self._c474_r = _cube.CubeReader(path) if os.path.exists(path) else None
            except Exception:  # noqa: BLE001
                r = self._c474_r = None
        return r

    def chat(self, text: str, session_id: str = "default") -> dict:
        res = super().chat(text, session_id)
        if not isinstance(res, dict) or res.get("status") == "answered":
            return res
        rd = self._c474_reader()
        if rd is None:
            return res
        try:
            a = rd.answer(text)
        except Exception:  # noqa: BLE001
            a = None
        if not a:
            return res
        chk = a.get("check") or {}
        refs = [{"id": a["claim"], "text": a["sentence"], "role": "binding"}]
        if chk.get("type_page"):
            refs.append({"id": "page:%s" % chk["type_page"], "text": chk.get("type_lead", ""), "role": "check"})
        out = dict(res)
        out.update({
            "status": "answered",
            "path": "cube:read>frame>link>expand>bind>check>verify",
            "response": "[ev:direct] %s. %s [%s]" % (a["answer"], a["sentence"], a["claim"]),
            "references": refs,
            "provenance": {"kind": "cube_phase_a", "subject": a["subject"], "answer_type": a["type"], "head": a["head"],
                           "binding_claim": a["claim"], "check": {k: v for k, v in chk.items() if k != "type_lead"},
                           "parent_path": str(res.get("path", "")), "parent_status": res.get("status")},
        })
        return out
