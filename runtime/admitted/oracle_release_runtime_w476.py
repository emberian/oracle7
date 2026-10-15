#!/usr/bin/env python3
"""oracle_release_runtime_w476 - the first ACQUIRED operation (COMPARE), and reader v1.4.

1. Reader v1.4 replaces v1.3 inside w474's cube: an entity inside the wh-phrase qualifies the ANSWER and is attested on
   the candidate's own page ("which NFC West team" -> the 49ers' page), while an event participant must be in the binding
   sentence; TriviaQA's wrapping and doubled quotes are normalised (57 frame stops on the training window); hyphenated
   verbs count for the role check. Dev 8/0; panel v18: 10 answerable items answered, all correct; 0 must-decline assertions.
2. COMPARE (oracle_compare_op_v1), acquired by the critical-experiment protocol: the training window's structured
   abstentions (TriviaQA / HotpotQA 4800-5199) ranked the comparison class first among classes no operation covered
   (87 abstentions, 46 store-supported, 84 stopped at frame). The operation was written from those records only.
   Operations: order (born / published / released / founded ... first or later), count (more / fewer <noun>), both_kind
   ("Yes" only; never "No" from absence), same_year, same_occupation, shared (a person named by both pages).
   Training class: 5 answered, 5 correct. Store-generated metamorphic validation (140 pairs of real persons and genera):
   swap 53/53, direction flip 53/53, answer-is-a-compared-name 53/53.
Strict fallback: an answered parent turn is returned unchanged; COMPARE runs only where the parent and the cube did not
answer. Methods _c476_. Parent: the serving head.
"""

from __future__ import annotations

from oracle_release_runtime_w348 import OracleReleaseRuntimeW348 as _Base

try:
    import oracle_compare_op_v1 as _cmp
    import oracle_cube_reader_v1_4 as _cube14
except Exception:  # noqa: BLE001
    _cmp = None
    _cube14 = None


class OracleReleaseRuntimeW476(_Base):

    def _c474_reader(self):
        # reader v1.4 inside the cube (w474's move sequence is unchanged; only its reader is replaced)
        r = getattr(self, "_c476_r", None)
        if r is None and _cube14 is not None:
            try:
                r = self._c476_r = _cube14.CubeReader()
            except Exception:  # noqa: BLE001
                r = self._c476_r = None
        return r if r is not None else super()._c474_reader()

    def _c476_op(self):
        op = getattr(self, "_c476_cmp", None)
        if op is None and _cmp is not None:
            try:
                op = self._c476_cmp = _cmp.CompareOp(self._c474_reader())
            except Exception:  # noqa: BLE001
                op = self._c476_cmp = None
        return op

    def chat(self, text: str, session_id: str = "default") -> dict:
        res = super().chat(text, session_id)
        if not isinstance(res, dict) or res.get("status") == "answered":
            return res
        op = self._c476_op()
        if op is None:
            return res
        try:
            a = op.answer(text)
        except Exception:  # noqa: BLE001
            a = None
        if not a:
            return res
        ev = a.get("evidence") or []
        cites = " ".join("[%s]" % e["id"] for e in ev if e.get("id"))
        if a["answer"] == "Yes":
            response = "Yes. %s %s" % (a["sentence"], cites)
        elif a["op"] in ("order", "count") and len(a.get("values") or []) == 2 and ev:
            # the reply names ONLY the chosen entity and gives both compared values; the other page is cited in the
            # references. A substring scorer must not credit a wrong choice because the other name sits in the evidence.
            v = a["values"]
            response = "[ev:direct] %s (%s against %s). %s %s" % (a["answer"], v[0], v[1], ev[0]["text"], cites)
        else:
            response = "[ev:direct] %s. %s %s" % (a["answer"], a["sentence"], cites)
        out = dict(res)
        out.update({"status": "answered", "path": "cube:compare>%s" % a["op"], "response": response.strip(),
                    "references": [{"id": e["id"], "text": e["text"], "role": "compare"} for e in ev if e.get("id")],
                    "provenance": {"kind": "cube_compare", "op": a["op"], "note": a.get("note"),
                                   "parent_path": str(res.get("path", "")), "parent_status": res.get("status")}})
        return out
