#!/usr/bin/env python3
"""oracle_release_runtime_w514 - CORRECTNESS RELEASE: answer the slot the question asked (the whole unit phrase, the number
attached to the counted noun, "1/N of a" read as N), and six more kinds of reply that answer a different question are withheld.

Why a correctness release: its whole effect is to turn wrong answers into right ones ("a cube has 8 corners, 12 edges" read
as 12 for "how many edges") or into declines (a reply about something else). On SPENT sealed test 5 (w513 replies): full
66 right / 7 wrong / 2 false yes -> 70 / 2 / 0; slim 61 / 6 / 2 -> 65 / 2 / 0. On the gate panel (w508 replies through
guards v3-v5, the gate's own item scorer): capability +1, false yes +0.

precision_guard_v6 = v5 unit helpers + guard v6 (fold w514). (v5 docstring follows.)
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

from oracle_release_runtime_w513 import OracleReleaseRuntimeW513 as _Base

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



# ---------------------------------------------------------------- guard v6 (w514): found on SPENT sealed test 5
CITE = re.compile(r"\[\d+\]|\[[a-z]+_[0-9a-f]{6,}\]|\[ev:[a-z_]+\]")
UNIT_TOKENS = re.compile(r"\b(?:m/s²|m/s\^2|m/s|km/h|km/s|kg/m³|kg/m3|g/cm³|g/cm3|g/ml|mol|kwh)\b", re.I)


def asked_unit6(q):
    """v5's asked_unit, but "how many meters per second is ..." reads the WHOLE unit phrase (v5 stopped at "meters")"""
    m = re.match(r"^\s*how many ([a-zA-Z/\- ]{1,40}) (?:are|is|does|do|will|would|can)\b", q, re.I)
    if m:
        cc = m.group(1).strip().lower()
        u = unit_at(cc)
        if u and (cc in UNITS or cc in _SING or cc == u[0]):
            return u
    return asked_unit(q)


def _nums(text, givens):
    t = CITE.sub(" ", text)
    out = []
    for m in NUM.finditer(t):
        v = float(m.group(0).replace(",", ""))
        if not any(abs(v - g) <= 1e-9 * max(abs(g), 1) for g in givens):
            out.append((v, m))
    return t, out


def rewrite6(q, out):
    """answer the slot asked: the asked unit (whole phrase), the number attached to the counted noun, '1/N of a' as N"""
    if str(out.get("status")) != "answered":
        return None
    resp = str(out.get("response", ""))
    ql = q.lower()
    givens = [float(t.replace(",", "")) for t in NUM.findall(q)]
    t, nums = _nums(resp, givens)
    # unit asked as a whole phrase ("how many meters per second is 72 km/h") - convert same-dimension answers
    want = asked_unit6(q)
    if want and nums:
        v, m = nums[0]
        got = unit_at(t[m.end():m.end() + 40])
        if got and got[1] == want[1] and got[0] != want[0] and abs(got[2] - want[2]) > 1e-15:
            val = v * (10 ** got[3]) * got[2] / want[2]
            new = dict(out)
            new["response"] = "%s %s (= %s %s). %s" % (_fmt(val), want[0], m.group(0), got[0], resp)
            new["path"] = "unit:%s->%s|%s" % (got[0], want[0], out.get("path"))
            return new
    # counting: "how many edges does a cube have" + "a cube has 8 corners, 12 edges" -> 12
    mc = re.match(r"^\s*how many ([a-z]+?)s?\b", ql)
    if mc and not want:
        noun = mc.group(1)
        hits = [(v, m) for v, m in nums if re.match(r"\s+" + re.escape(noun) + r"(?:e?s)?\b", t[m.end():m.end() + 30], re.I)]
        if hits and nums and hits[0][1].start() != nums[0][1].start():
            v, m = hits[0]
            new = dict(out)
            new["response"] = "%s %s. %s" % (_fmt(v), noun + ("s" if v != 1 else ""), resp)
            new["path"] = "slot:count>%s|%s" % (noun, out.get("path"))
            return new
    # "how many milligrams are in a gram" + "a milligram is 1/1000 of a gram" -> 1000
    mi = re.match(r"^\s*how many ([a-z]+?)s? (?:are )?in an? ([a-z]+)\b", ql)
    if mi:
        if True:
            mf = re.search(r"\b(?:an?\s+)?" + re.escape(mi.group(1)) + r"s?\s+is\s+(?:one\s+|1\s*)?/\s*(\d[\d,]*)|\b" + re.escape(mi.group(1)) +
                           r"s?\s+is\s+1/(\d[\d,]*)\s+of\s+an?\s+" + re.escape(mi.group(2)), CITE.sub(" ", resp), re.I)
            if mf:
                n = float((mf.group(1) or mf.group(2)).replace(",", ""))
                new = dict(out)
                new["response"] = "%s %ss. %s" % (_fmt(n), mi.group(1), resp)
                new["path"] = "slot:inverse>%s|%s" % (mi.group(1), out.get("path"))
                return new
    return None


def guard6(q: str, out: dict):
    st, path = str(out.get("status", "")), str(out.get("path", ""))
    if st != "answered":
        return None
    resp = " ".join(str(out.get("response", "")).split())
    head = CITE.sub(" ", resp)[:300]
    ql = q.lower()
    givens = [float(t.replace(",", "")) for t in NUM.findall(q)]
    _, nums = _nums(resp, givens)
    # R1: the maths evaluator read an English question (units like m/s are not algebra; uppercase letters are variables too)
    mr = re.search(r"\bread ([^;]{1,60});", resp)
    q_noun = UNIT_TOKENS.sub(" ", ql)
    content = [w for w in re.findall(r"\b[a-z]{3,}\b", q_noun) if w not in ("what", "the", "is", "was", "are", "and", "how", "which", "who")]
    if path.startswith("organ:math>evaluate") and mr and re.search(r"[A-Za-z]", mr.group(1)) and len(content) >= 3 and \
            not re.search(r"[=]|\b(simplify|evaluate|expression|expand|factor|solve|x|y|z)\b", q_noun):
        return "R1_english_as_algebra"
    # R2: a number was asked and the reply gives none (citation markers are not numbers)
    want = asked_unit6(q)
    if want and not nums and not re.search(r"\b(zero|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|twenty|"
                                          r"thirty|hundred|thousand|million|billion|dozen|half)\b", head[:200], re.I):
        return "R2_no_number"
    # R3: the whole asked unit vs the reply's unit
    if want and nums:
        v, m = nums[0]
        got = unit_at(CITE.sub(" ", resp)[m.end():m.end() + 40])
        if got and got[1] != want[1]:
            return "R3_unit_dimension"
    # R4: a year was asked; the reply names no year
    if re.match(r"^\s*(?:in )?(?:what|which) year\b|^\s*when (?:did|was|were)\b", ql):
        if not re.search(r"\b(1\d{3}|20\d{2}|\d{1,3} (?:BC|BCE|AD|CE))\b", head):
            return "R4_no_year"
        # R5: "in what year did <Subject> <verb> ..." must be about that subject
        ms = re.match(r"^\s*(?i:in )?(?i:what|which) year did (?:the )?([A-Z][\w\-]+)(?:\s+[A-Z][\w\-]+)*\s+(?:win|lose|invent|discover|"
                      r"defeat|conquer|beat|sign|land|arrive|die|found|build|first)\b", q)
        if ms and not path.startswith(("organ:relation", "cube:", "network", "specialist_call")) and \
                not re.search(r"\b" + re.escape(ms.group(1)[:6]), head, re.I):
            return "R5_subject_missing"
    # R6: "what is the <attribute> of <X>" answered by retrieval must mention the attribute
    ma = re.match(r"^\s*what(?:'s| is| was)\s+the\s+(capital|currency|population|symbol|language|area|height|length|depth|"
                  r"altitude|elevation|diameter|radius|density|temperature|price)(?:\s+city)?\s+(?:of|for)\s+", ql)
    if ma and path.startswith(("corpus_query", "factoid:", "compose:", "arb:")) and \
            not re.search(r"\b" + re.escape(ma.group(1)[:5]), head, re.I):
        return "R6_attribute_missing"
    return None


class OracleReleaseRuntimeW514(_Base):

    def chat(self, text: str, session_id: str = "default") -> dict:
        out = super().chat(text, session_id=session_id)
        if not isinstance(out, dict):
            return out
        try:
            conv = rewrite6(str(text), out)
            if conv:
                out = conv
            rule = guard6(str(text), out)
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
