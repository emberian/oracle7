#!/usr/bin/env python3
"""oracle_release_runtime_w547 - CORRECTNESS RELEASE (3.1): seven kinds of wrong reply found by the research record become right
or become declines. Every rule is a property of (question, route, reply); none names an item.

Found by the standing research programs on release patch 3 (prometheus7.com/research, composition rounds R1/R2 and the
re-examination E-20261017-0013) and the habitable-zone Workbench example:
1. AN ANSWER ABOUT SOMETHING NOT ASKED (narrowing). The astronomy specialist answered "Is a world receiving 1.4 times
   Earth's sunlight from a 3,100 K star in the habitable zone?" with "Sunlight takes about 8.3 minutes to reach Earth",
   and "How much sunlight does Mars get compared to Earth?" with Mars's MASS ratio. A specialist reply that states a
   travel time when the question asks no time, or a ratio of a property the question never names, is withheld.
2. THE UNIT ASKED FOR (capability, exact). "...What does a full water butt of water weigh on Earth, in kilonewtons?" was
   answered "30810 N". When a quantity route answers in a unit of the same dimension as the one asked, the number is
   restated in the asked unit by an exact factor (30.81 kN), with the route's own figure kept in brackets.
3. "IT" NAMED ONE SENTENCE EARLIER (capability). "4 litres of ice sit at 0 °C. How many kilojoules does it take to melt
   all of it?" got "What does 'it' refer to?". When the conversation layer asks what "it" means and the question's
   previous sentence names a measured thing ("4 litres of ice"), the last sentence is asked again with that thing in
   place of "it"; the reply is kept only if a quantity route answers it (every check in the chain still applies).
4. A DIFFERENT QUANTITY (narrowing, then capability). Asked "What is the wavelength in air of the sound at its fundamental
   frequency?", the acoustics specialist answered "The frequency is 50 Hz". When the quantity the question names (a noun the
   specialists' own exams ask for, learned by network v6: "wavelength" is a length) and the reply's quantity have different
   dimensions, the reply is withheld - and, as for a half answer, network v6 is asked; its answer is kept when it reaches
   what was asked through a learned operation.
5. A DIFFERENT CALCULATION (narrowing). "Find the second derivative of f(t) = ..." and "what is f'(0)?" were answered with
   the first derivative's expression by the maths organ; such a reply is withheld (the w548 fold then asks the specialist).
6. DEFINITIONS FOR A REQUEST (narrowing). "Calculate the OSHA noise dose" was answered by the multi-step route with "Since
   you mention hours: An hour is ...", and "Graph with weighted edges A-B 7, ... Find the shortest path" by the conversation
   organ with "Since you mention edges: Edge can mean ..."; a reply that defines the turn's words, given to a turn that asks
   for something with numbers (find, calculate, convert, how many ...), is withheld (the w548 fold then asks the specialist).
   First pre-check (2026-10-17): the first version of rules 4-6 cost 11 capability items - two conversation statements ("I wonder
   what that means"), eight NIOSH "recommended weight limit" questions (weight in everyday use is a mass), one derivative AT a
   point answered with its value - and was narrowed: rule 6 needs numbers and a calculation verb, rule 4 lets a mass stand for a
   "weight", rule 5 withholds a value-at-a-point reply only when it is still an expression.
7. THE UNIT'S CASE (display). Network answers printed the asked unit lower-cased ("886 mj" for MJ - mj reads as
   millijoules); the unit is printed as the question wrote it.
The fold imports no runtime other than its parent."""
from __future__ import annotations

import re

from oracle_release_runtime_w550 import OracleReleaseRuntimeW550 as _Base

# ---------------------------------------------------------------- 1. the property answered must be the one asked
TIME_CUE = re.compile(r"\b(how long|how many (?:seconds|minutes|hours|days)|minutes?|seconds?|hours?|light[- ]?(?:minutes?|seconds?|"
                      r"hours?|time|travel)|take[s]?\b.*\bto (?:reach|get|arrive|travel)|travel time)\b", re.I)
RATIO_PROP = re.compile(r"^\s*(?:\[ev:[a-z_]+\]\s*)?[A-Z][\w' ]*?'s?\s+([a-z][a-z ]{2,40}?)\s+is\s+[\d.,]+\s+times\b")
PROP_WORDS = {"mass": r"mass|massive|heav", "diameter": r"diameter|size|big|wide|width|radius|across", "density": r"dens",
              "gravity": r"gravit|weigh|g\b", "surface gravity": r"gravit|weigh", "escape velocity": r"escape",
              "length of day": r"day", "orbital period": r"year|orbit|period", "distance from the sun": r"distance|far|from the sun",
              "mean temperature": r"temperat|hot|cold|warm", "number of moons": r"moons?", "orbital velocity": r"orbit|speed|fast"}


def _c547_off_topic(q: str, out: dict):
    path = str(out.get("path", ""))
    if out.get("status") != "answered" or "astronomy" not in path:
        return None
    if path.endswith(">light_time") and not TIME_CUE.search(q):
        return "A1_time_not_asked"
    if path.endswith(">ratio"):
        m = RATIO_PROP.match(str(out.get("response", "")))
        if m:
            prop = m.group(1).strip().lower()
            cue = PROP_WORDS.get(prop, re.escape(prop.split()[0]))
            if not re.search(r"\b(?:%s)" % cue, q, re.I):
                return "A2_property_not_asked"
    return None


# ---------------------------------------------------------------- 5/6. a different calculation, or none
OTHER_DERIV = re.compile(r"\b(second|third|2nd|3rd) derivative\b|f''|\bd2\b|d\^2|f'\s*\(\s*-?\d|\bat [a-z] *= *-?\d|\bevaluate", re.I)
CALC_ASK = re.compile(r"\b(calculate|compute|work out|find|determine|solve|convert|evaluate)\b|^\s*how (?:many|much|long|far)\b",
                      re.I)
AT_POINT = re.compile(r"f'\s*\(\s*-?\d|\bat [a-z] *= *-?\d|\bevaluate", re.I)


def _c547_wrong_calc(q: str, out: dict):
    path, resp = str(out.get("path", "")), str(out.get("response", ""))
    if out.get("status") != "answered":
        return None
    if path.endswith(">derivative") and OTHER_DERIV.search(q) and resp.count("differentiate") <= 1:
        head = re.split(r"\bIn steps\b", re.sub(r"^\s*\[ev:[a-z_]+\]\s*", "", resp), 1)[0]
        expression = bool(re.search(r"[a-z]\s*(?:\*\*|\^)|\d\s*\*?\s*[a-z]\b", head))
        if not AT_POINT.search(q) or expression:        # a value was asked and an expression came back, or f'' asked
            return "C1_other_derivative"                # (a value at a point answered WITH a value is kept)
    if path.startswith(("capability:multi_step", "organ:converse")) and CALC_ASK.search(q) and re.search(r"\d", q) \
            and "Since you mention" in resp:
        return "M1_definitions_not_a_calculation"       # a numbered request (find, calculate ...) answered with definitions
    return None


def _c547_unit_case(q: str, out: dict):
    """a network answer prints the asked unit lower-cased ("886 mj" for MJ, megajoules - mj reads as millijoules): print it
    as the question wrote it"""
    if out.get("status") != "answered" or not str(out.get("path", "")).startswith("network"):
        return None
    resp = str(out.get("response", ""))
    m = re.match(r"^(The answer is -?[\d,.]+(?:e[+-]?\d+)?) ([A-Za-z]+)\b", resp)
    if not m or m.group(2) != m.group(2).lower():
        return None
    for w in re.findall(r"[A-Za-z]+", q):
        if w.lower() == m.group(2) and w != m.group(2):
            return resp[:m.start(2)] + w + resp[m.end(2):]
    return None


# ---------------------------------------------------------------- 2. the unit asked for
UNITS = {  # symbol: (dimension, factor to SI, words)
    "N": ("force", 1.0, ["newtons", "newton", "n"]), "kN": ("force", 1e3, ["kilonewtons", "kilonewton", "kn"]),
    "MN": ("force", 1e6, ["meganewtons", "meganewton", "mn"]),
    "J": ("energy", 1.0, ["joules", "joule", "j"]), "kJ": ("energy", 1e3, ["kilojoules", "kilojoule", "kj"]),
    "MJ": ("energy", 1e6, ["megajoules", "megajoule", "mj"]), "Wh": ("energy", 3600.0, ["watt-hours", "watt hours", "watt-hour", "wh"]),
    "kWh": ("energy", 3.6e6, ["kilowatt-hours", "kilowatt hours", "kilowatt-hour", "kwh"]),
    "W": ("power", 1.0, ["watts", "watt", "w"]), "kW": ("power", 1e3, ["kilowatts", "kilowatt", "kw"]),
    "g": ("mass", 1e-3, ["grams", "gram", "g"]), "kg": ("mass", 1.0, ["kilograms", "kilogram", "kg"]),
    "t": ("mass", 1e3, ["tonnes", "tonne", "metric tons"]),
    "mm": ("length", 1e-3, ["millimetres", "millimeters", "mm"]), "cm": ("length", 1e-2, ["centimetres", "centimeters", "cm"]),
    "m": ("length", 1.0, ["metres", "meters", "metre", "meter", "m"]), "km": ("length", 1e3, ["kilometres", "kilometers", "km"]),
    "mL": ("volume", 1e-6, ["millilitres", "milliliters", "ml"]), "L": ("volume", 1e-3, ["litres", "liters", "litre", "liter", "l"]),
    "m3": ("volume", 1.0, ["cubic metres", "cubic meters", "m3", "m³"]),
}
WORD2SYM = {w: s for s, (_d, _f, ws) in UNITS.items() for w in ws}
ASKED = re.compile(r"\bin\s+(%s)\s*[?.!]?\s*$" % "|".join(sorted((re.escape(w) for w in WORD2SYM), key=len, reverse=True)), re.I)
QTY_ROUTES = ("network", "specialist_call>", "op:", "organ:math", "weight:", "unit:", "compute:")
NUMU = re.compile(r"(?<![\w.])(-?\d[\d,]*(?:\.\d+)?(?:e[+-]?\d+)?)\s*(%s)\b" % "|".join(
    sorted((re.escape(s) for s in UNITS), key=len, reverse=True)))


def _fmt(x: float) -> str:
    if x == 0:
        return "0"
    a = abs(x)
    s = ("%.4g" % x) if (a >= 1e-3 and a < 1e9) else ("%.4e" % x)
    if "e" not in s and "." not in s and a >= 1e4:
        s = "{:,}".format(int(round(x)))
    return s


def _c547_unit(q: str, out: dict):
    if out.get("status") != "answered" or not str(out.get("path", "")).startswith(QTY_ROUTES):
        return None
    ma = ASKED.search(q.strip())
    if not ma:
        return None
    want = WORD2SYM.get(ma.group(1).lower()) or WORD2SYM.get(ma.group(1))
    head = re.split(r"\s\(path:|\s\[", str(out.get("response", "")), 1)[0]
    found = [(m.group(1), m.group(2)) for m in NUMU.finditer(head)]
    if not want or len(found) != 1:
        return None
    num, sym = found[0]
    if sym == want or UNITS[sym][0] != UNITS[want][0]:
        return None
    try:
        v = float(num.replace(",", "")) * UNITS[sym][1] / UNITS[want][1]
    except ValueError:
        return None
    return "The answer is %s %s (%s %s)." % (_fmt(v), want, num, sym)


# ---------------------------------------------------------------- 3. "it" named one sentence earlier
THING = re.compile(r"^\s*((?:an?|the|\d[\d,]*(?:\.\d+)?)\s+(?:[a-z]+\s+){0,3}(?:of\s+[a-z]+(?:\s+[a-z]+)?)?)\s+"
                   r"(?:sits?|is|are|was|were|has|have|stands?|lies|lie|weighs?|holds?|contains?)\b([^.?!]*)[.!]\s+(.+\?)\s*$", re.I)
AT_STATE = re.compile(r"\b(?:already\s+)?at\s+(-?\d[\d,]*(?:\.\d+)?\s*(?:°\s*|degrees?\s*)?[CFK])\b", re.I)


def _c547_it(q: str):
    m = THING.match(q)
    if not m:
        return []
    thing, rest, last = m.group(1).strip(), m.group(2), m.group(3)
    if not re.search(r"\b(?:all of it|it)\s*\?\s*$", last, re.I):
        return []
    st = AT_STATE.search(rest)
    outs = []
    if st:
        outs.append(re.sub(r"\b(?:all of it|it)\s*\?\s*$", "%s that is already at %s?" % (thing, st.group(1)), last, flags=re.I))
    outs.append(re.sub(r"\b(?:all of it|it)\s*\?\s*$", "%s?" % thing, last, flags=re.I))
    return outs


class OracleReleaseRuntimeW547(_Base):
    def chat(self, text: str, session_id: str = "default") -> dict:
        out = super().chat(text, session_id=session_id)
        if not isinstance(out, dict):
            return out
        q = str(text or "")
        try:
            why = _c547_off_topic(q, out)
            if not why and out.get("status") == "answered" and str(out.get("path", "")).startswith(("specialist_call>", "network")):
                want, got = self._c546_dims(q, out.get("response", ""))
                if want is not None and got is not None and want != got and \
                        not (re.search(r"\bweigh", q, re.I) and tuple(got) == (0, 1, 0, 0, 0, 0)):
                    why = "A3_other_quantity"                  # asked for a wavelength, answered with a frequency
                    #                                            ("weight" in everyday use is a mass: a weight limit in kg stands)
            if not why:
                why = _c547_wrong_calc(q, out)
            if why or str(out.get("path", "")).startswith("precision_guard:Q2_half_answer>"):
                alt = self._c546_solve(q, out)                 # the learned network may reach what was asked
                if alt:
                    return alt
            if why:
                new = dict(out)
                new.update({"status": "withheld", "path": "precision_guard:%s>%s" % (why, out.get("path")), "references": [],
                            "response": "I have an answer about something close, but not about what you asked, so I won't give it."})
                return new
            if out.get("status") == "clarification" and str(out.get("path", "")).startswith("act:clarify_specific"):
                for alt in _c547_it(q):
                    r = super().chat(alt, session_id=session_id + "~it")
                    if isinstance(r, dict) and r.get("status") == "answered" and str(r.get("path", "")).startswith(QTY_ROUTES):
                        new = dict(r)
                        new["path"] = "it_named>%s" % r.get("path")
                        new.setdefault("provenance", {})
                        new["provenance"] = dict(new.get("provenance") or {}, asked_as=alt)
                        out = new
                        break
            cased = _c547_unit_case(q, out)
            if cased:
                out = dict(out, response=cased)
            restated = _c547_unit(q, out)
            if restated:
                new = dict(out)
                new.update({"path": "%s>unit_restated" % out.get("path"), "response": restated})
                return new
        except Exception:  # noqa: BLE001 - a failure here never costs the chain's reply
            return out
        return out
