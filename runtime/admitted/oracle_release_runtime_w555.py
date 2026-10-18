#!/usr/bin/env python3
"""oracle_release_runtime_w555 - CORRECTNESS RELEASE (3.2): OWNER-FIRST NEVER OVERRULES A QUESTION THAT IS ITSELF THE PROBLEM.

Found by the release-candidate smoke (smoke_compose_reloc_v3, probe "zentar", the published miss of sealed test 20) on
2026-10-18, before sealed test 23 ran: asked "How many minutes are in a day on the planet Zentar?", the head rightly withholds
(precision_guard:Q5_unknown_body - there is no planet Zentar), and w554's owner-first step then answered "1 day is 1440
minutes" from the units specialist; the same for Tralfamadore. Its list of declines that must stand named "unknown_place"
and "other_body" but not "unknown_body".

Also found then: asked "What is the orbital period of a circular orbit at 200 km altitude around Earth?", the astronomy
reader answers Earth's own orbital period (365.2 days) - and the proved cross-check marks it, because the kernel reads the
question the same way (veri7vn proves the computation; its recognizer, which reads the question, is not proved). An
astronomy answer to a question that names an orbit's altitude is now withheld as the wrong reading, and owner-first may
answer it from #18 orbits under its numbers test.

Narrowing otherwise. Owner-first (w554 step 2) no longer acts when the head's withholding is any of the precision guard's Q rules
- the rules that say the QUESTION is the problem: an unknown body or place, half an answer, a wrong gravity, paths that
disagree, not physical, a pronoun or name missing, a bare numeral. Every other turn is w554's, byte for byte; the star
specialists (w554 step 1) are unchanged. The fold imports no runtime other than its parent and changes no module state of any
other fold."""
from __future__ import annotations

import re

from oracle_release_runtime_w554 import OracleReleaseRuntimeW554 as _Base


def _guard_rule(path):
    p = str(path or "")
    if not p.startswith("precision_guard:"):
        return None
    return p.split(":", 1)[1].split(">")[0].split("|")[0]


ALTITUDE = re.compile(r"\b\d[\d,]*(?:\.\d+)?\s*(?:km|kilomet(?:er|re)s?|miles?)\s+(?:altitude|above|high)\b|\baltitude of\b|\bcircular orbit\b", re.I)


class OracleReleaseRuntimeW555(_Base):
    def _owner(self, text, session_id, r):
        rule = _guard_rule(r.get("path", ""))
        if rule is not None and rule[:1] == "Q":
            return r                                    # the question is the problem: the head's decline stands
        return super()._owner(text, session_id, r)

    def chat(self, text: str, session_id: str = "default") -> dict:
        r = super().chat(text, session_id)
        # the astronomy readers answer a planet's own figures ("Earth's orbital period is 365.2 Earth days"); a question that
        # names an orbit's altitude asks about a spacecraft's orbit around that body, which #18 orbits computes. The planet
        # figure is withheld as the wrong reading, and owner-first may ask the family (its numbers test applies).
        if isinstance(r, dict) and r.get("status") == "answered" and "specialist:astronomy" in str(r.get("path", "")) and ALTITUDE.search(text):
            held = dict(r, status="withheld", path="reader_guard:planet_figure_for_an_orbit>" + str(r.get("path", "")),
                        response="That asks about an orbit at a given altitude, and what I found is the planet's own figure, so I won't give it as the answer.")
            held.pop("proved", None)
            out = self._owner(text, session_id, held)
            return out
        return r
