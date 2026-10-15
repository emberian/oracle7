#!/usr/bin/env python3
"""oracle_release_runtime_w511 - PRECISION GUARD over w510.

precision_guard_v4 - the second precision layer (fold w511 over w510, whose guard v3 stays in force). Found on SPENT sealed
test 3 and the dev probes; every rule is a property of (question, route, reply), none names an item.
  P1 declines-in-words  a reply that opens "I have no admitted entry/record for <phrase>" is a decline when the missing phrase
                        asks for a specific attribute (a symbol, a superlative, a capital, a speed ...), not a definition
  P2 number-asked       the question asks for a number (how many / how much / how long / convert / "in <unit>") and the
                        reply offers no number beyond the question's own givens
  P3 unit-dimension     the question asks "in <unit>" and the reply's number carries a unit of a different dimension
                        (a weight in newtons answered in kg)
  P4 lookup-for-compute the question gives numbers to compute with, and a lookup route (corpus / page / definition / bridge)
                        answers it: retrieval cannot compute with the asker's numbers
  P5 shape              a game built for a question that asks for no game; an integer square root when decimals were asked
  P6 body               the question is set on another body (on the Moon / Mars ...) and the reply never names it
  P7 premise            impossible givens (a negative distance, mass, time or volume; more than 24 hours a day; cooling up /
                        heating down; a zero volume to divide by), or a question about the asker's own private life
  P8 generic-you        "if you ... what happens", "what happens if you ...", "is it true that ..." are questions about the
                        world: a conversational reply to them is not an answer
"""
import re

from oracle_release_runtime_w375 import OracleReleaseRuntimeW375 as _Base

NO_ENTRY = re.compile(r"^\s*(?:\[ev:[a-z_]+\]\s*)?I have no admitted (?:entry|record) for [\"“]([^\"”]{1,120})[\"”]", re.I)
ATTR = re.compile(r"\b(largest|longest|smallest|highest|hardest|tallest|biggest|deepest|fastest|oldest|first|last|most|least|"
                  r"symbol|capital|currency|population|velocity|speed|mass|weight|number|name|author|year|date|age|height|"
                  r"length|distance|temperature|density|boiling|melting|freezing|area|volume)\b", re.I)
NUMQ = re.compile(r"^\s*(how many|how much|how long|how far|how fast|how old|convert|calculate|compute)\b|"
                  r"\bin (?:degrees |square |cubic )?(?:newtons?|joules?|kilojoules?|watts?|kwh|kg|kilograms?|grams?|pounds?|"
                  r"meters?|metres?|km|kilometers?|centimeters?|miles?|seconds?|minutes?|hours?|days?|years?|liters?|litres?|"
                  r"milliliters?|dollars?|pascals?|amps?|volts?|ohms?|celsius|fahrenheit|kelvin|m/s|km/s|km/h|mph|"
                  r"m/s squared|kg per cubic meter|grams per mole|moles?)\b", re.I)
NUM = re.compile(r"(?<![\w.])[-+]?(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?(?:[eE][-+]?\d+)?")
DIM = [("force", r"newtons?|\bN\b"), ("mass", r"kg|kilograms?|grams?|\bg\b|pounds?|lbs?|tonnes?"),
       ("energy", r"joules?|\bJ\b|kJ|kilojoules?|kWh|calories|kcal"), ("power", r"watts?|\bW\b|kW"),
       ("speed", r"m/s(?!²| squared|\^2)|km/s|km/h|mph|meters per second|kilometers per (?:hour|second)"),
       ("accel", r"m/s²|m/s\^2|m/s squared"), ("time", r"seconds?|\bs\b|minutes?|hours?|days?|years?"),
       ("length", r"meters?|metres?|\bm\b|km|kilometers?|centimeters?|cm|miles?|feet|ft|inches"),
       ("volume", r"liters?|litres?|\bL\b|milliliters?|mL|gallons?|cubic meters?|m³"),
       ("money", r"dollars?|\$"), ("pressure", r"pascals?|\bPa\b"), ("temp", r"degrees|°C|°F|celsius|fahrenheit|kelvin|\bK\b")]
RETRIEVAL = ("corpus_query", "factoid:", "arb:", "compose:", "deep_reach", "definitional", "cube:read")
BODIES = r"(?:the Moon|Moon|Mars|Jupiter|Venus|Mercury|Saturn|Neptune|Uranus|Pluto|Titan|Europa)"
GENERIC_YOU = re.compile(r"^\s*(if you\b|what happens (?:if|when) you|what will happen (?:if|when) you|what happens to you|"
                         r"is it (?:true|possible|safe|dangerous) |can you (?:really|actually|get|catch|die|survive)|"
                         r"what should you do|how long should you|why do (?:people|we)|do (?:all|most) )", re.I)


def _nums(text):
    return [float(t.replace(",", "")) for t in NUM.findall(text)]


def _dim(unit_text):
    for name, rx in DIM:
        if re.match(r"\s*(?:" + rx + r")", unit_text):
            return name
    return None


def guard(q: str, out: dict):
    st, path = str(out.get("status", "")), str(out.get("path", ""))
    if st != "answered":
        return None
    resp = " ".join(str(out.get("response", "")).split())
    ql = q.lower()
    # P7: impossible givens / private facts - asserting anything is a false yes
    if not re.search(r"[\^=]|\bfactor|\bsimplify|\bsolve|\bexpand|\bevaluate", ql) and \
            re.search(r"(?:^|(?<=\s))-\s?\d+(?:\.\d+)?\s*(?:m\b|meters?\b|metres?\b|km\b|kilometers?\b|miles?\b|kg\b|kilograms?\b|"
                      r"grams?\b|seconds?\b|minutes?\b|hours?\b|liters?\b|litres?\b)", q):
        return "P7_negative_given"
    m = re.search(r"\b(\d+(?:\.\d+)?)\s*hours? (?:a|per) day", ql)
    if m and float(m.group(1)) > 24:
        return "P7_over_24h_a_day"
    if re.search(r"\bcool\w*\b.*\bup to\b|\bheat\w*\b.*\bdown to\b", ql):
        return "P7_direction"
    if re.search(r"\bvolume of 0\b|\b0 (?:liters?|litres?|cubic)", ql):
        return "P7_zero_volume"
    if re.match(r"^\s*(what|what's|who|when|where|which|how old)\b.*\bmy (?:mother|father|mom|dad|best friend|friend|wife|"
                r"husband|partner|sister|brother|boss|neighbou?r)'s (?:\w+ )?(?:name|number|address|birthday|age|email|password)\b", ql):
        return "P7_private"
    # P1: declines in words
    m = NO_ENTRY.match(resp)
    if m and ATTR.search(m.group(1)) and not re.search(r"[{}();=<>]", m.group(1)):
        return "P1_declines_in_words"
    givens = _nums(q)
    rest = [x for x in _nums(resp) if not any(abs(x - g) <= 1e-9 * max(abs(g), 1) for g in givens)]
    asks_number = bool(NUMQ.search(q)) or bool(re.match(
        r"^\s*what(?:'s| is| was) the (?:kinetic |potential )?(?:area|volume|circumference|perimeter|energy|momentum|force|speed|"
        r"velocity|density|mass|weight|power|resistance|current|pressure|work|cost|price|average|mean|hypotenuse|ph|"
        r"square root|cube root|sum|product|value)\b", q, re.I))
    # P9: a symbolic maths question (derivative, integral, factor ...) answered by anything but a maths organ
    if re.search(r"\b(derivative|differentiate|integral|integrate|antiderivative|factori[sz]e|factor completely)\b", ql) and \
            not path.startswith(("organ:math", "algebra", "op:", "compute:", "math", "specialist_call>specialist:calculus", "synth")) and \
            not re.search(r"\b(python|code|script|function|program|javascript)\b", ql):
        return "P9_math_by_lookup"
    # P2: a number was asked and none was given
    if asks_number and not rest and not re.search(r"\b(zero|none|no|one|two|three|four|five|six|seven|eight|nine|ten|eleven|"
                                                  r"twelve|twenty|thirty|hundred|thousand|million|billion|dozen|half)\b", resp, re.I):
        return "P2_no_number"
    # P3: unit dimension mismatch
    mq = re.search(r"\bin ((?:degrees |square |cubic )?[a-z/²^ ]+?)(?:[?.,]|$)", q, re.I)
    if asks_number and mq and rest:
        want = _dim(mq.group(1))
        mr = re.search(r"(?<![\w.])" + re.escape(("%g" % rest[0]))[:6], resp)
        got = None
        for mm in NUM.finditer(resp):
            try:
                v = float(mm.group(0).replace(",", ""))
            except ValueError:
                continue
            if abs(v - rest[0]) <= 1e-9 * max(abs(v), 1):
                got = _dim(resp[mm.end():mm.end() + 24])
                break
        del mr
        if want and got and want != got and {want, got} != {"temp", "time"}:
            return "P3_unit_dimension"
    # P4: a lookup route answering a computation over the asker's numbers
    if givens and asks_number and path.startswith(RETRIEVAL):
        return "P4_lookup_for_compute"
    # P5: shape
    if path.startswith("game:") and not re.search(r"\b(game|play|puzzle|quiz|match|cards?|hanoi|maze|sudoku|chess)\b", ql) and \
            not re.match(r"^\s*(?:please\s+)?(?:write|build|make|create|program|code|design|generate)\b", ql):
        return "P5_game_not_asked"
    if "integer_sqrt" in path and re.search(r"\bdecimal|\bplaces?\b|\bapprox", ql):
        return "P5_integer_for_decimals"
    # P6: another body
    mb = re.search(r"\bon (?:the )?(" + BODIES + r")\b", q)
    if mb and path.startswith(("specialist_call", "network", "organ:math")) and \
            not re.search(r"\b" + mb.group(1).replace("the ", "") + r"\b", resp, re.I):
        return "P6_body_dropped"
    # P8: generic "you" questions are about the world
    if GENERIC_YOU.match(q) and path.startswith(("organ:converse", "organ:self", "self:", "worker:", "act:")):
        return "P8_generic_you_chat_reply"
    return None


class OracleReleaseRuntimeW511(_Base):

    def chat(self, text: str, session_id: str = "default") -> dict:
        out = super().chat(text, session_id=session_id)
        if not isinstance(out, dict):
            return out
        try:
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
