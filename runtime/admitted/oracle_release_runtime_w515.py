#!/usr/bin/env python3
"""oracle_release_runtime_w515 - VERIFIED REACH: connect the typed relation store to the questions it can answer, and stop
unverified sentences from answering the rest (Ben 2026-10-03, option 3: "fix retrieval properly").

Measured before submission on DEV data only (spent sealed tests 3-6, door probes, WebQuestions train, gate panel replies):
  sealed 3-6 full: wrong 50 -> 33, false yes 11 -> 8, right held; slim: right 235 -> 246, wrong 41 -> 29, false yes 11 -> 8
  (slim's relation answers are corroborated from Simple English Wikipedia, the pages slim actually ships).
Modules (new versions; v1/v2 stay frozen for the admitted folds that import them):
  oracle_tritree_v3 - RULE A corroboration from EITHER side (the answer's own page naming the subject counts); a property a
                      question form names establishes the role; such an answer is not a restatement
  relation_forms_v2 - forms for more of the store's 98 properties (country, continent, creator, performer, spouse, parents,
                      place of death, nationality, instrument, sport, headquarters, named after, published, author of ...)
  verified_retrieval_v1, verified_reach_v1 - below.

verified_reach_v1:
verified_reach_v1 - fold w515's turn logic: connect the typed relation store to the questions it can answer, and stop
unverified sentences from answering the rest.

For a factual question (conversation turns are never touched):
  A. TYPED RELATION FIRST. If the question's form names a relation the store holds (capital, currency, author, country,
     continent, creator, performer, spouse, parents, place of birth/death, nationality, instrument, sport, publication,
     headquarters, named-after, inception, birth/death dates, where), the tri-tree v3 answers it with every check
     (type, exactly one value, two-sided corroboration). Its answer replaces any WEAK-route reply; a reply from an already
     checked route (maths, specialists, network, relation, cube, unit/slot rewrites) is never replaced.
  B. VERIFIED RETRIEVAL. A weak-route reply that A did not replace must pass the reasoning cube (its own chain, or its
     CHECK on the weak sentence's candidate); otherwise it is withheld and the passage shown as unverified.
Stores: the deep store when it is populated (full release), else Simple English Wikipedia (slim) - so slim's relation
answers are corroborated from the pages it actually has.

verified_retrieval_v1:
verified_retrieval_v1 - a retrieved sentence is not an answer until something independent checks it.

The four weak retrieval routes (full-text search, page reading, corpus lookup, the bridge/compose readers) answer from a
sentence that is near the question; on four sealed tests they were right about half the time, while every checked route
(maths, specialists, network, the typed relation reader, the reasoning cube) was right ~95%. LAW (09-09): a proposal must
be checked by something independent of what generated it. The independent checker already exists: the reasoning cube's
CHECK (the candidate's OWN page must say it is the asked type; agent/patient role; every other name and year of the
question attested; a value unique in its sentence). This layer routes every weak-route answer through it:
  1. the cube's own full chain answers the question (frame -> link -> bind -> check -> verify): its answer stands;
  2. else the weak route's own sentence yields exactly one candidate of the asked type, and that candidate passes the
     cube's CHECK with the question's linked subject: the weak answer stands, restated with the checked value first;
  3. else the reply is WITHHELD; the passage is still shown, marked unverified.
verify(q, out, cube) -> new out (or None when the turn is not a weak-route answer).
"""
import os
import re

from oracle_release_runtime_w514 import OracleReleaseRuntimeW514 as _Base

try:
    os.environ.setdefault("TT_RULES", "A,B")
    import verified_reach_v1 as _VR
    import verified_retrieval_v1 as _V
    import oracle_tritree_v3 as _T3
    import relation_forms_v2 as _F2
    from oracle_cube_reader_v1_4 import CubeReader as _Cube
except Exception:  # noqa: BLE001 - without its modules the fold is exactly its parent
    _VR = None


class OracleReleaseRuntimeW515(_Base):

    def _c515(self):
        o = getattr(self, "_c515_o", None)
        if o is None and _VR is not None:
            try:
                cube = _Cube(path=_VR.page_store())
                o = (cube, _T3.TriTree(reader=cube))
            except Exception:  # noqa: BLE001
                o = False
            self._c515_o = o
        return o or None

    def chat(self, text: str, session_id: str = "default") -> dict:
        out = super().chat(text, session_id=session_id)
        o = self._c515()
        if not o or not isinstance(out, dict):
            return out
        try:
            new = _VR.turn(str(text), out, o[1], _F2, o[0], _V.verify)
        except Exception:  # noqa: BLE001 - the layer never costs the turn
            return out
        return new if new is not None else out
