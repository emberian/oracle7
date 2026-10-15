#!/usr/bin/env python3
"""oracle_release_runtime_w490 - an isolated short English word is not a product of variables.

CORRECTNESS RELEASE. Found by the first nightly proposer brief (proposal_brief_v1.py), which puts every unanswered
question people asked to every organ: the math organ read "On what date in 1969 did Neil Armstrong first set foot on the
Moon?" as the expression 1969 * d**2 * i - the English word "did" taken as the implicit product d*i*d. The chain answers
that question itself, so the defect was latent, but any similar question the chain declines would have been answered
with algebra. math_organ_v3 reads a 2-3 letter run as an implicit product only when it is GLUED to mathematics ("2ah",
"xy+1"); a word standing alone between spaces is English. w482's math_organ_v2 is immutable (governance law), so this
fold imports v3. Measured on the textbook development instrument (dev modules only): v1 3,764 right / 598 wrong,
v3 3,742 right / 568 wrong - thirty fewer wrong answers, precision 86.3% -> 86.8%.
Also: a word-problem unit is pluralised ("250 centimeters", not "250 centimeter").
Parent: the serving tip, named. Methods _c490_.
"""

from __future__ import annotations

import re

from oracle_release_runtime_w488 import OracleReleaseRuntimeW488 as _Base

try:
    import math_organ_v3 as _math3
except Exception:  # noqa: BLE001
    _math3 = None

_UNITS = ("millimeter", "centimeter", "meter", "kilometer", "inch", "foot", "yard", "mile", "milligram", "gram",
          "kilogram", "ounce", "pound", "ton", "milliliter", "liter", "litre", "cup", "pint", "quart", "gallon",
          "second", "minute", "hour", "day", "week", "year")
_PLURAL = {"inch": "inches", "foot": "feet"}


class OracleReleaseRuntimeW490(_Base):

    def _c480_math(self):
        o = getattr(self, '_c490_m', None)
        if o is None and _math3 is not None:
            try:
                o = self._c490_m = _math3.MathOrgan()
            except Exception:  # noqa: BLE001
                o = self._c490_m = False
        return o or super()._c480_math()

    def _c480_dispatch(self, text, session_id, res):
        out = super()._c480_dispatch(text, session_id, res)
        if isinstance(out, dict) and str(out.get('path', '')).startswith('organ:math>word'):
            body = str(out.get('response', ''))

            def plural(m):
                n, u = m.group(1), m.group(2)
                return "%s %s" % (n, u if float(n.replace(',', '')) == 1 else _PLURAL.get(u, u + "s"))
            new = re.sub(r"(\d[\d,]*(?:\.\d+)?) (%s)\b" % "|".join(_UNITS), plural, body, count=1)
            if new != body:
                out = dict(out)
                out['response'] = new
        return out
