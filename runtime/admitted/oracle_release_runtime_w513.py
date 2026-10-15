#!/usr/bin/env python3
"""oracle_release_runtime_w513 - CORRECTNESS RELEASE: the answer is given in the unit the question asked, and five more kinds
of reply that answer a different question are withheld.

Why a correctness release: its whole effect is to turn wrong answers into right ones (a true value in the wrong unit becomes
the same value in the asked unit) or into declines (a reply about something else). On SPENT sealed test 4 (w511 replies):
full 66 right / 13 wrong / 3 false yes -> 73 / 5 / 0; slim 65 / 9 / 3 -> 71 / 2 / 0. On the gate panel (w508 replies, the
gate's own item scorer): capability +0, false yes +0 - the panel has no unit-asked items, so it cannot see the gain.

precision_guard_v5 - fold w513 over the head (guards v3 + v4 stay in force). Found on SPENT sealed tests 3 and 4.

ANSWER IN THE UNIT ASKED. When a question asks for a quantity "in <unit>" (or "how many <unit>") and the reply's number
carries another unit of the SAME dimension, the reply is restated in the asked unit, exactly converted, with the original
kept: "19.282 g/cm³" asked in kg per cubic meter -> "19282 kg per cubic meter (= 19.282 g/cm³)". Different dimensions are
never converted (that is guard v4's P3, a withhold).
Guard rules (each a property of question, route, reply):
  Q1 english-as-algebra  the maths evaluator "read" an English sentence as an expression (no operator or variable asked)
  Q2 period              a quantity asked per week / month / year answered for one day
  Q3 subject-missing     "what is the <attribute> of <X>" or "<Name> did ..." answered by a reply that never names X / Name
  Q4 numeral             the question names "World War I", the reply is about "World War II" (any Name + roman numeral)
  Q5 pronoun-who         a "who" question answered by a sentence that names no one ("She was the first woman ...")
  P2' / P3'              v4's number-asked check reads number words only at the start of the reply; v4's unit check reads
                         the unit after a "x 10^n" exponent
"""
import re

from oracle_release_runtime_w511 import OracleReleaseRuntimeW511 as _Base

NUM = re.compile(r"(?<![\w.])[-+]?(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?(?:[eE][-+]?\d+)?")
# unit -> (dimension, factor to SI). Longest names first when matching.
UNITS = {
    "kilometers per hour": ("speed", 1 / 3.6), "km/h": ("speed", 1 / 3.6), "kph": ("speed", 1 / 3.6), "mph": ("speed", 0.44704),
    "miles per hour": ("speed", 0.44704), "meters per second": ("speed", 1.0), "m/s": ("speed", 1.0), "km/s": ("speed", 1000.0),
    "kilometers per second": ("speed", 1000.0), "meters per minute": ("speed", 1 / 60),
    "kg per cubic meter": ("density", 1.0), "kg/m³": ("density", 1.0), "kg/m3": ("density", 1.0), "g/cm³": ("density", 1000.0),
    "g/cm3": ("density", 1000.0), "g/ml": ("density", 1000.0), "grams per cubic centimeter": ("density", 1000.0),
    "kilowatt-hours": ("energy", 3.6e6), "kwh": ("energy", 3.6e6), "wh": ("energy", 3600.0), "mwh": ("energy", 3.6e9),
    "kilojoules": ("energy", 1000.0), "kj": ("energy", 1000.0), "joules": ("energy", 1.0), "j": ("energy", 1.0),
    "kilocalories": ("energy", 4184.0), "kcal": ("energy", 4184.0), "calories": ("energy", 4.184),
    "megawatts": ("power", 1e6), "mw": ("power", 1e6), "kilowatts": ("power", 1000.0), "kw": ("power", 1000.0),
    "watts": ("power", 1.0), "w": ("power", 1.0),
    "milliamps": ("current", 0.001), "ma": ("current", 0.001), "amps": ("current", 1.0), "amperes": ("current", 1.0),
    "kilonewtons": ("force", 1000.0), "kn": ("force", 1000.0), "newtons": ("force", 1.0), "n": ("force", 1.0),
    "kilopascals": ("pressure", 1000.0), "kpa": ("pressure", 1000.0), "pascals": ("pressure", 1.0), "pa": ("pressure", 1.0),
    "kilometers": ("length", 1000.0), "km": ("length", 1000.0), "centimeters": ("length", 0.01), "cm": ("length", 0.01),
    "millimeters": ("length", 0.001), "mm": ("length", 0.001), "meters": ("length", 1.0), "metres": ("length", 1.0),
    "m": ("length", 1.0), "miles": ("length", 1609.344), "feet": ("length", 0.3048), "ft": ("length", 0.3048),
    "inches": ("length", 0.0254),
    "kilograms": ("mass", 1.0), "kg": ("mass", 1.0), "grams": ("mass", 0.001), "g": ("mass", 0.001),
    "milligrams": ("mass", 1e-6), "mg": ("mass", 1e-6), "pounds": ("mass", 0.45359237), "lb": ("mass", 0.45359237),
    "lbs": ("mass", 0.45359237), "tonnes": ("mass", 1000.0),
    "hours": ("time", 3600.0), "hour": ("time", 3600.0), "h": ("time", 3600.0), "minutes": ("time", 60.0), "min": ("time", 60.0),
    "seconds": ("time", 1.0), "s": ("time", 1.0), "days": ("time", 86400.0),
    "milliliters": ("volume", 1e-6), "ml": ("volume", 1e-6), "liters": ("volume", 1e-3), "litres": ("volume", 1e-3),
    "l": ("volume", 1e-3), "cubic meters": ("volume", 1.0), "m³": ("volume", 1.0), "gallons": ("volume", 3.785411784e-3),
}
_SING = {"meter": "meters", "kilometer": "kilometers", "mile": "miles", "foot": "feet", "inch": "inches", "kilogram": "kilograms",
         "gram": "grams", "pound": "pounds", "second": "seconds", "minute": "minutes", "liter": "liters", "litre": "litres",
         "joule": "joules", "kilojoule": "kilojoules", "watt": "watts", "kilowatt": "kilowatts", "newton": "newtons",
         "pascal": "pascals", "amp": "amps", "ampere": "amperes", "day": "days", "gallon": "gallons", "milliliter": "milliliters",
         "centimeter": "centimeters", "millimeter": "millimeters", "milligram": "milligrams", "megawatt": "megawatts",
         "kilowatt-hour": "kilowatt-hours", "kilocalorie": "kilocalories", "calorie": "calories", "tonne": "tonnes"}
_NAMES = sorted(UNITS, key=len, reverse=True)


def unit_at(text):
    """the unit that starts text (after a 'x 10^n' exponent, if any) -> (name, dim, factor, exponent) or None"""
    t = text
    exp = 0
    me = re.match(r"\s*[×x]\s*10\s*\^?\s*([⁻\-]?[\d⁰¹²³⁴⁵⁶⁷⁸⁹]+)", t)
    if me:
        sup = str.maketrans("⁰¹²³⁴⁵⁶⁷⁸⁹⁻", "0123456789-")
        exp = int(me.group(1).translate(sup))
        t = t[me.end():]
    t = t.lstrip().lower()
    for name in _NAMES:
        if t.startswith(name) and (len(t) == len(name) or not t[len(name)].isalpha()):
            d, f = UNITS[name]
            return name, d, f, exp
    w = re.match(r"([a-z\-]+)", t)
    if w and w.group(1) in _SING:
        d, f = UNITS[_SING[w.group(1)]]
        return _SING[w.group(1)], d, f, exp
    return None


def asked_unit(q):
    m = re.search(r"\bin (?:units of )?((?:square |cubic )?[a-zA-Z/³²\- ]{1,30}?)\s*(?:[?.,]|$)", q)
    cands = [m.group(1)] if m else []
    m2 = re.match(r"^\s*how many ([a-zA-Z/\- ]{1,30}?) (?:are|is|does|do|will|would|per|in|of)\b", q, re.I)
    if m2:
        cands.append(m2.group(1))
    m3 = re.match(r"^\s*how many ([a-zA-Z/\- ]{1,30}?) (?:per|an?) ", q, re.I)
    if m3:
        cands.append(m3.group(1))
    for c in cands:
        u = unit_at(c)
        cc = c.strip().lower()
        if u and (cc in UNITS or cc in _SING or cc == u[0] or (cc.endswith(" squared") and cc[:-8] in UNITS)):
            return u
    return None


def _fmt(x):
    if x == 0:
        return "0"
    r = float("%.4g" % x)
    if 1e-4 <= abs(r) < 1e9:
        return ("%d" % r) if r == int(r) else ("%.6f" % r).rstrip("0").rstrip(".")
    mant, e = ("%.4g" % x).split("e")
    return "%s × 10^%d" % (mant, int(e))


def convert(q, out):
    """restate an answered reply in the unit the question asked for (same dimension only); returns new out or None"""
    if str(out.get("status")) != "answered":
        return None
    want = asked_unit(q)
    if not want:
        return None
    resp = str(out.get("response", ""))
    givens = [float(t.replace(",", "")) for t in NUM.findall(q)]
    for m in NUM.finditer(resp):
        try:
            v = float(m.group(0).replace(",", ""))
        except ValueError:
            continue
        if any(abs(v - g) <= 1e-9 * max(abs(g), 1) for g in givens):
            continue
        got = unit_at(resp[m.end():m.end() + 40])
        if not got:
            return None
        if got[1] != want[1] or got[0] == want[0] or abs(got[2] - want[2]) < 1e-15:
            return None
        val = v * (10 ** got[3]) * got[2] / want[2]
        new = dict(out)
        mo = re.match(r"\S+(?:\s*[×x]\s*10\s*\^?\s*[⁻\-]?[\d⁰¹²³⁴⁵⁶⁷⁸⁹]+)?\s*[^\s,.;()]+(?: per [a-z]+| [a-z]+ per [a-z]+)?", resp[m.start():])
        orig = mo.group(0) if mo else m.group(0)
        new["response"] = "%s %s (= %s). %s" % (_fmt(val), want[0], orig, resp)
        new["path"] = "unit:%s->%s|%s" % (got[0], want[0], out.get("path"))
        return new
    return None


def guard(q: str, out: dict):
    st, path = str(out.get("status", "")), str(out.get("path", ""))
    if st != "answered":
        return None
    resp = " ".join(str(out.get("response", "")).split())
    head = re.sub(r"^\s*\[ev:[a-z_]+\]\s*", "", resp)[:300]
    ql = q.lower()
    givens = [float(t.replace(",", "")) for t in NUM.findall(q)]
    rest = [float(t.replace(",", "")) for t in NUM.findall(resp) if not any(abs(float(t.replace(",", "")) - g) <= 1e-9 * max(abs(g), 1) for g in givens)]
    # Q1: the evaluator read English as an expression
    mr = re.search(r"\bread ([^;]{1,60});", head)
    content = [w for w in re.findall(r"\b[a-z]{3,}\b", ql) if w not in ("what", "the", "is", "was", "are", "and", "how", "which", "who")]
    if path.startswith("organ:math>evaluate") and mr and re.search(r"[a-z]", mr.group(1)) and len(content) >= 3 and \
            not re.search(r"[+\-*/^=]|\b(simplify|evaluate|expression|expand|x|y|z)\b", ql):
        return "Q1_english_as_algebra"
    # P2': a number was asked, none given, and no number word opens the reply
    asks_number = re.match(r"^\s*(how many|how much|how long|how far|convert|calculate|compute)\b", ql) or asked_unit(q) or \
        re.match(r"^\s*what(?:'s| is| was) the (?:kinetic |potential )?(?:area|volume|circumference|perimeter|energy|momentum|"
                 r"force|speed|velocity|density|mass|weight|power|resistance|current|pressure|work|cost|average|mean|"
                 r"hypotenuse|frequency|acceleration|surface gravity|ph)\b", ql)
    if asks_number and not rest and not re.search(r"\b(zero|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|"
                                                  r"twenty|thirty|hundred|thousand|million|billion|dozen|half)\b", head[:200], re.I):
        return "P2b_no_number"
    # P3': unit after an exponent, different dimension from the one asked
    want = asked_unit(q)
    if want and rest:
        for m in NUM.finditer(resp):
            v = float(m.group(0).replace(",", ""))
            if any(abs(v - g) <= 1e-9 * max(abs(g), 1) for g in givens):
                continue
            got = unit_at(resp[m.end():m.end() + 40])
            if got and got[1] != want[1]:
                return "P3b_unit_dimension"
            break
    # Q2: a period asked, one day answered
    if re.search(r"\b(?:in|per|each|every|over) (?:a |one |the )?(week|month|year)\b|\bin (\d+) (days|weeks)\b", ql) and \
            re.search(r"\(one day\)|\bper day\b|\ba day\b|\bdaily\b", head, re.I) and "day" not in ql.split("in a")[-1][:0]:
        if not re.search(r"\b(week|month|year|\d+ days)\b", head, re.I):
            return "Q2_period"
    # Q3: the subject the question asks about must be named
    ms = re.match(r"^\s*what(?:'s| is| was| are)\s+the\s+[a-z ]{2,30}?\s+(?:of|for)\s+([a-z][a-z\-]{3,30})\s*\??\s*$", ql)
    if ms and not path.startswith(("organ:math", "algebra", "op:", "compute:", "network", "unit:", "organ:relation", "cube:")) and \
            not re.search(r"\b" + re.escape(ms.group(1)[:6]), head, re.I):
        return "Q3_subject_missing"
    mn = re.search(r"\b(?:was|is|did|does|were|has|had)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\b", q)
    if mn and path.startswith("specialist_call") and not re.search(re.escape(mn.group(1).split()[-1]), resp, re.I):
        return "Q3_name_missing"
    # Q4: Name + roman numeral must match
    for mrn in re.finditer(r"\b([A-Z][a-z]+(?: [A-Z][a-z]+)*) (I{1,3}|IV|VI{0,3}|IX|X)\b(?![a-z])", q):
        name, num = mrn.group(1), mrn.group(2)
        others = re.findall(re.escape(name) + r" (I{1,3}|IV|VI{0,3}|IX|X)\b(?![a-z])", head)
        if others and num not in others:
            return "Q4_numeral"
    # Q5: a "who" question needs a named someone
    if re.match(r"^\s*who\b", ql) and re.match(r"^(?:She|He|They|It)\b", head) and \
            not [w for w in re.findall(r"\b[A-Z][a-z]+", head) if w not in ("She", "He", "They", "It", "The", "In", "A")
                 and w.lower() not in ql]:
        return "Q5_pronoun_who"
    return None


class OracleReleaseRuntimeW513(_Base):

    def chat(self, text: str, session_id: str = "default") -> dict:
        out = super().chat(text, session_id=session_id)
        if not isinstance(out, dict):
            return out
        try:
            conv = convert(str(text), out)
            if conv:
                out = conv
            rule = guard(str(text), out)
        except Exception:  # noqa: BLE001 - the guard never costs the turn
            return out
        if not rule:
            return out
        new = dict(out)
        new.update({"status": "withheld", "path": "precision_guard:%s|%s" % (rule, out.get("path")),
                    "response": "I can't verify an answer to that exact question, so I won't guess.",
                    "references": [], "provenance": {"kind": "precision_guard", "rule": rule, "withheld_path": out.get("path"),
                                                     "withheld_response": str(out.get("response", ""))[:400]}})
        return new
