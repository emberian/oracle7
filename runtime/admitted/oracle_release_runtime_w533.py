#!/usr/bin/env python3
"""oracle_release_runtime_w533 - CORRECTNESS RELEASE + the RELATION FAMILY v5: answer guards from SEALED TEST 13 (run once
2026-10-13, RC13b head w532: full missed the format bar with 1 expression reply, slim missed precision at 89.2%), and the
main model calling every admitted relation specialist - including the 52 admitted 2026-10-13 - as ONE family, so a turn
can be answered from several of them, part by part (Ben 2026-10-13: "oracle7 main can efficiently use and combine the
specialists as needed in real conversation").

GUARDS (each a general rule over a CLASS of reply, written from the failures and tested on fresh examples, never on the
spent items; v1 of this fold lost 6 capability items on precheck because G5 matched single characters and G6 any letter -
both narrowed here):
  G4 THOUSANDS - a number written with thousands separators ("2,025") is one number: the question is passed on with the
     separators removed (only digit + 3-digit groups; "1990,1991" and "1, 2, 3" untouched).
  G5 ECHO - a maths route answered with the question's own text: an unconverted fraction when the question asks for a
     decimal or a percentage ("7/16 as a decimal" -> "7/16"), or an equation "x = 3" that the question itself states.
  G6 UNITS ARE NOT VARIABLES - organ:math answered with a symbolic expression whose every letter is a UNIT letter of the
     question ("9 m by 5 m" -> "9*m"; "in kg/m3" -> "3*g*k/m") and the question has no algebra.
  G7 WORD SENSE - astronomy (the planet) answering a question that measures a quantity of a substance ("0.5 litres of
     mercury"); chemistry (the element) answering a question about moons, orbits, planets, rings or spacecraft.
FAMILY v5: /opt/oracle-clm/specialists/_gate/standing_new_v5.txt (161 relation specialists = every one the gate admitted;
pinned, never edited after this fold is measured), called exactly as w526 calls v2 - only on turns the whole chain declined;
a disagreement between two specialists leaves the decline standing. NEW: in a multi-part turn, a part no specialist covers
is asked of the main model itself (its own chain, in a sub-session so the conversation's state is not touched) and its
answer is used only if it is answered; otherwise that part is reported as not covered.
CONVERSATION (found on dev probes, never on a sealed item): (a) people are introduced by what they do - "the speed skater
Sven Kramer", "the fencer Aron Szilagyi" - and the descriptor stopped the relation readers from linking the name; when the
family finds nothing, it is asked once more with the descriptor removed (the specialist's own domain check still decides).
(b) two questions joined by "and" without a comma ("What is the capital of Chile and what is 12% of 300?") reached the
chain as one, which answered one part; such a turn is split before a question word and each part goes through the whole
pipeline in a sub-session; a part nothing answers is said to be uncovered, never guessed.
The fold never imports a runtime other than its parent; it touches no other module's state."""
from __future__ import annotations

import importlib.util
import re
import threading

from oracle_release_runtime_w532 import OracleReleaseRuntimeW532 as _Base

SPEC_ROOT = __import__("os").environ.get("ORACLE7_ROOT", "/opt/oracle-clm") + "/specialists"
GATE = SPEC_ROOT + "/_gate"
FAMILY_CODE = GATE + "/combo_runtime_v1.py"
NEW_STANDING = GATE + "/standing_new_v5.txt"
DELIBERATE = ("does_not_follow", "out_of_fragment", "validity")
_S: dict = {}
_LOCK = threading.Lock()

THOUSANDS = re.compile(r"(?<![\d,.])(\d{1,3})((?:,\d{3})+)(?![\d,])")
MATH_PATHS = ("organ:math", "algebra:")
AS_DECIMAL = re.compile(r"\bas an? (?:decimal|percentage|percent)\b", re.I)
FRACTION = re.compile(r"^\s*-?\d+\s*/\s*\d+\s*$")
EQUATION = re.compile(r"^\s*([a-z])\s*=\s*(-?\d+(?:\.\d+)?)\s*$", re.I)
ALGEBRA = re.compile(r"\b(simplify|expand|factori[sz]e|factor|solve|expression|polynomial|derivative|differentiate|integral|"
                     r"integrate|equation|variable|function)\b|\d[a-z](?![a-z])|(?<![A-Za-z/])[a-z](?![A-Za-z/])\s*[\^=+*<>]|"
                     r"[\^=+*(]\s*[a-z](?![A-Za-z/])|\$", re.I)   # "/" is left out: m/s, km/h, kg/m3 are units
UNIT_TOK = re.compile(r"\d\s*([a-zA-Z]{1,3}(?:/[a-zA-Z]{1,3}\d?)?)\b|\bin\s+([a-zA-Z]{1,3}/[a-zA-Z]{1,3}\d?)\b")
SUBSTANCE = re.compile(r"\b\d+(?:\.\d+)?\s*(?:litres?|liters?|l|ml|millilitres?|milliliters?|grams?|g|kg|kilograms?|"
                       r"cubic\s+\w+|m3|cm3)\s+of\b", re.I)
SKY = re.compile(r"\b(moons?|orbits?|orbiting|planets?|rings?|satellites?|spacecraft|probes?|telescope)\b", re.I)
WITHHELD = "I can't verify an answer to that exact question, so I won't guess."
DESCRIPTOR = re.compile(r"\bthe ((?:[a-z]+[ -]){0,2}[a-z]+) (?=[A-Z][a-z])")
MULTI = re.compile(r"\s*,?\s+and\s+(?=(?:what|who|whom|where|when|which|how|in what|in which|on what)\b)", re.I)
PARTS_PATHS = ("chat:parts", "specialist_call>combo:parts", "combo:parts")
QSTART = re.compile(r"^\s*(?:what|who|whom|whose|where|when|which|why|how|is|are|was|were|do|does|did|can|could|name|tell me|in what|"
                    r"in which|on what)\b", re.I)


def unthousand(q):
    return THOUSANDS.sub(lambda m: m.group(1) + m.group(2).replace(",", ""), q)


def math_value(reply):
    """the stated value of a maths-route reply: '[ev:derived] 7/16. In steps...' -> '7/16'; 'x = 3. read it...' -> 'x = 3'"""
    t = re.sub(r"^\s*\[ev:[a-z_]+\]\s*", "", str(reply))
    m = re.match(r"(.+?)(?:\.\s|\.$|$)", t)
    return (m.group(1) if m else t).strip()


def _norm(s):
    return re.sub(r"\s+", "", str(s)).lower()


def echoed(q, reply):
    v = math_value(reply)
    if FRACTION.match(v) and AS_DECIMAL.search(q) and _norm(v) in _norm(q):
        return True
    m = EQUATION.match(v)
    # only a value the question STATES as a given ("at x = 3", "when x = 3", "if x = 3", ", x = 3") - never the right-hand side
    # of the equation to be solved ("Solve 49 / x = 7" -> x = 7 is the answer, not an echo; precheck 2026-10-13)
    given = r"(?:^|[,;(]|\b(?:at|when|if|where|given|with|for|and))\s*%s\s*=\s*%s(?![\d.])" % (re.escape(m.group(1)), re.escape(m.group(2))) if m else None
    return bool(m) and re.search(given, q, re.I) is not None


def unit_symbolic(q, reply):
    v = math_value(reply)
    letters = set(re.findall(r"[A-Za-z]", v))
    if not letters or ALGEBRA.search(q):
        return False
    units = set()
    for a, b in UNIT_TOK.findall(q):
        units |= set(re.findall(r"[A-Za-z]", a or b))
    return letters <= units


def wrong_sense(q, path):
    if "specialist:astronomy" in path and SUBSTANCE.search(q):
        return True
    return "specialist:chemistry" in path and bool(SKY.search(q))


def _withhold(out, rule):
    new = dict(out)
    path = str(out.get("path", ""))
    new.update({"status": "withheld", "path": "precision_guard:%s|%s" % (rule, path), "response": WITHHELD, "references": [],
                "provenance": {"kind": "precision_guard", "rule": rule, "withheld_path": path,
                               "withheld_response": str(out.get("response", ""))[:400]}})
    return new


def _c533_family():
    with _LOCK:
        if "fam" not in _S:
            spec = importlib.util.spec_from_file_location("o7_combo_runtime_v1_w533", FAMILY_CODE)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            ids = open(NEW_STANDING, encoding="utf-8").read().split()
            _S["fam"] = mod.Family(["%s/%s/manifest.json" % (SPEC_ROOT, i) for i in ids], ["%s/%s" % (SPEC_ROOT, i) for i in ids])
        return _S["fam"]


def _c533_lacks(out):
    st, path = str(out.get("status", "")), str(out.get("path", ""))
    return st in ("withheld", "clarification") and not path.endswith(DELIBERATE)


class OracleReleaseRuntimeW533(_Base):
    def _c533_part(self, part, session_id):
        """a part no specialist covers, asked of the main model's own chain in a sub-session"""
        try:
            r = _Base.chat(self, part, session_id="%s#part" % session_id)
        except Exception:  # noqa: BLE001
            return None
        return r if isinstance(r, dict) and r.get("status") == "answered" else None

    def _c533_family_reply(self, text, out, session_id):
        try:
            r = _c533_family().reply(text, "core:%s" % session_id)
            if not r and DESCRIPTOR.search(text):
                r = _c533_family().reply(DESCRIPTOR.sub("", text, count=1), "core:%s" % session_id)
        except Exception:  # noqa: BLE001 - a family failure never costs the chain's own reply
            return out
        if not r or r.get("status") == "disagree":
            return out
        prov = r.get("provenance") or {}
        if prov.get("per_part"):
            parts = prov.get("parts") or []
            if not any(p.get("specialist") and not p.get("declined") for p in parts):
                return out
            lines = []
            for p in parts:
                if p.get("specialist"):
                    lines.append("%s [%s]" % (p["response"], p["specialist"]))
                    continue
                c = None if p.get("disagree") else self._c533_part(p["part"], session_id)
                if c is not None:
                    p["core_path"] = c.get("path")
                    lines.append(str(c.get("response", "")))
                else:
                    lines.append("(None of my specialists covers: \"%s\")" % p["part"])
            status, response = "answered", " ".join(lines)
        else:
            status = "withheld" if prov.get("declined") else "answered"
            response = "%s [%s]" % (r["response"], prov.get("specialist"))
        new = dict(out)
        new.update({"status": status, "path": "specialist_call>" + str(r.get("path")), "response": response, "references": [],
                    "provenance": {"kind": "core_called_specialist", "family": "new_v5", "core_status": out.get("status"),
                                   "core_path": out.get("path"), "specialist": prov.get("specialist"), "parts": prov.get("parts")}})
        return new

    def chat(self, text: str, session_id: str = "default") -> dict:
        clean = unthousand(str(text or ""))                       # G4
        out = self._c533_one(clean, session_id)
        parts = [p.strip() for p in MULTI.split(clean) if p.strip()]
        # only two QUESTIONS are split: "Everything is fine, and how are you?" is one social turn (precheck 2026-10-13)
        if (len(parts) < 2 or len(parts) > 3 or str(out.get("path", "")).startswith(PARTS_PATHS + ("organ:dialogue",))
                or not QSTART.match(parts[0])):
            return out
        answers = []
        for i, p in enumerate(parts):
            p = p if p.rstrip().endswith("?") else p.rstrip(" .") + "?"
            r = self._c533_one(p, "%s#and%d" % (session_id, i))
            answers.append(r if r.get("status") == "answered" else None)
        if not any(answers):
            return out
        lines = [str(r.get("response", "")) if r else "(I can't verify an answer to: \"%s\")" % p for p, r in zip(parts, answers)]
        new = dict(out)
        new.update({"status": "answered", "path": "chat:and_parts>%d of %d" % (sum(1 for r in answers if r), len(parts)),
                    "response": " ".join(lines), "references": [],
                    "provenance": {"kind": "and_parts", "parts": [{"part": p, "path": (r or {}).get("path")} for p, r in zip(parts, answers)],
                                   "whole_path": out.get("path")}})
        return new

    def _c533_one(self, clean, session_id):
        out = super().chat(clean, session_id=session_id)
        if not isinstance(out, dict):
            return out
        if _c533_lacks(out):
            out = self._c533_family_reply(clean, out, session_id)
        if str(out.get("status", "")) != "answered":
            return out
        path, reply = str(out.get("path", "")), str(out.get("response", ""))
        if path.startswith(MATH_PATHS):
            if echoed(clean, reply):
                return _withhold(out, "G5_echo")
            if path.startswith("organ:math") and unit_symbolic(clean, reply):
                return _withhold(out, "G6_units_not_variables")
        if path.startswith("specialist_call>") and wrong_sense(clean, path):
            return _withhold(out, "G7_word_sense")
        return out
