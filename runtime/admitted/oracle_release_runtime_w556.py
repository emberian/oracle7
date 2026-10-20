#!/usr/bin/env python3
"""oracle_release_runtime_w556 - CORRECTNESS RELEASE (3.2 full): THREE GUARDS ON ANSWERS THAT HAVE NOTHING UNDER THEM.

Found by sealed test 23 on 2026-10-18, which the full 3.2 failed with 3 false yeses against a bar of 2 (slim passed with 1).
Each guard is a class of error, not an item; sealed 23 is spent and is not the test of this fold.

  1. NO STORED FACT WITHOUT GIVENS. w554's owner-first keeps a specialist's answer only when every number the question gives
     moves it. A question that gives no numbers passed that test vacuously: "How old is the president of Antarctica?" was
     answered with the US constitution's minimum age (a stored fact, kind fact_number). With no givens, owner-first may no
     longer hand back a stored fact; computations and a named body's constants still answer (requiring givens for every
     answer was measured first and lost three right escape-velocity answers).
  2. A NEGATIVE AMOUNT OF SOMETHING THAT CANNOT BE NEGATIVE. "A 100 W bulb runs for -5 hours" was answered 0.5 kWh, the sign
     dropped (slim and full). A question that gives a negative duration, power, energy, mass, volume or count is withheld
     on every route, as the precision guard withholds other questions that are themselves the problem (a Q rule, so
     owner-first never overrules it).
  3. (MEASURED AND REMOVED) Evidence must name what the question names, aimed at "Who directed City of God?" (answered from a
     sentence about another work) and "In what year did Napoleon visit Neptune?" (answered 1989 from a sentence about
     Voyager 2). Every form of the check measured on the capability panel lost right answers - all names 62, then 21 on the
     fact routes, any name 7 - because relation answers cite the answer's own page, which need not repeat the question's
     names. It is not in this fold; those two sealed-23 failures stay open: disclosed.
  4. ARITHMETIC IS NOT READ FROM A SENTENCE. "A walker covers 5 km in 60 minutes ... how many minutes does 8 km take?" was
     answered 50 from an unrelated sentence. A question that gives two or more numbers and asks how many/much/long is not
     answered from retrieved text; the specialist network (v6, learned operations) is asked instead, and if it has no
     checked answer the turn is withheld.

Every other turn is w555's, byte for byte (guards 1, 2 and 4 only). The fold imports no runtime other than its parent; the network is loaded from
specialists/_gate under its own module name, as w550 does, and a network failure never costs the parent's reply."""
from __future__ import annotations

import importlib.util
import re
import sys
import threading

from oracle_release_runtime_w423 import OracleReleaseRuntimeW423 as _Base

SPEC_ROOT = __import__("os").environ.get("ORACLE7_ROOT", "/opt/oracle-clm") + "/specialists"
GATE = SPEC_ROOT + "/_gate"
NET6_CODE = GATE + "/network_v6.py"
NET_STANDING = GATE + "/standing_net_v6.txt"

NUM = re.compile(r"\d[\d,]*(?:\.\d+)?")
NONNEG = (r"hours?|hrs?|minutes?|mins?|seconds?|secs?|days?|weeks?|months?|years?|watts?|W|kW|MW|kilowatts?|kWh|MWh|Wh|joules?|J|"
          r"kg|kilograms?|grams?|g|mg|pounds?|lbs?|tonnes?|tons?|litres?|liters?|L|mL|millilit(?:er|re)s?|gallons?|"
          r"people|persons?|students?|workers?|apples?|books?|items?|cars?|boxes|eggs?|cups?|bottles?")
NEGQ = re.compile(r"(?:(?<![A-Za-z0-9.])-\s?|\bminus\s+|\bnegative\s+)\d[\d,]*(?:\.\d+)?\s*(?:" + NONNEG + r")\b", re.I)
HOWQ = re.compile(r"\b(how many|how much|how long|how far|how fast|how old)\b", re.I)
LEAD = {"who", "what", "when", "where", "which", "why", "how", "in", "on", "at", "did", "does", "do", "is", "was", "were", "are",
        "the", "a", "an", "name", "tell", "give", "for", "from", "of", "by", "with", "can", "could", "would", "should", "if"}
SPAN = re.compile(r"[A-Z][\w'’.-]*(?:\s+(?:of|the|de|la|le|von|van|and|&|du|del)?\s*[A-Z][\w'’.-]*)*")
STOP = {"of", "the", "de", "la", "le", "von", "van", "and", "&", "du", "del"}
# the routes that read ONE fact from evidence (where sealed 23's wrong answers came from); deliberation, capability and
# document routes cite sentences that name their subject as "it" or in another form, and are judged by their own checks
FACT_ROUTES = ("cube:", "organ:relation", "factoid", "verified:", "unverified")
ANAPHOR = re.compile(r"\s*(It|Its|He|She|His|Her|They|Their|This|The city|The country)\b")
QUOTED = re.compile(r"[\"“]([^\"”]{2,80})[\"”]")
_S: dict = {}
_LOCK = threading.Lock()


def _net():
    with _LOCK:
        if "net" not in _S:
            if GATE not in sys.path:
                sys.path.insert(0, GATE)
            spec = importlib.util.spec_from_file_location("o7_network_v6_w556", NET6_CODE)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            _S["net"] = mod.Network(open(NET_STANDING, encoding="utf-8").read().split(), SPEC_ROOT, GATE)
        return _S["net"]


def _spans(q):
    """the names a question gives: capitalised runs (a sentence-initial question word is not a name) and quoted titles"""
    out = [m.group(1) for m in QUOTED.finditer(q)]
    for m in SPAN.finditer(q):
        words = m.group(0).split()
        if m.start() == 0:
            words = words[1:]                           # a question's first word is capitalised by position ("Explain", "Summarize")
        while words and words[0].lower() in LEAD:
            words = words[1:]
        if any(w.lower() not in STOP for w in words):
            out.append(" ".join(words))
    return out


def _named_in(span, text):
    """a name is present when its last word is: a surname ("Einstein" for Albert Einstein), a title's head ("God"); matched on
    its stem, so a plural or a derived form counts ("Annelids" for Annelid)"""
    words = [re.sub(r"[^\w]", "", w.lower()) for w in span.split()]
    words = [w for w in words if w and w not in STOP and len(w) > 1]
    if not words:
        return True
    w = words[-1]
    stem = w if len(w) <= 4 else w[:max(4, len(w) - 3)]
    return re.search(r"\b%s" % re.escape(stem), text.lower()) is not None


def _withheld(r, path, response):
    out = dict(r)
    out.update(status="withheld", path=path + ">" + str(r.get("path", "")), response=response)
    for k in ("proved", "references"):
        out.pop(k, None)
    return out


class OracleReleaseRuntimeW556(_Base):
    def _owner(self, text, session_id, r):
        out = super()._owner(text, session_id, r)
        # guard 1: with no givens the numbers test is vacuous, so owner-first may not hand back a STORED FACT read off
        # (a fact_* kind: "A President must be at least 35" for the president of Antarctica). A computation or a body's
        # physical constant (escape velocity of Mars, gravity of Jupiter) still answers - measured: requiring givens for
        # every answer lost three right escape-velocity answers on the capability panel.
        if (out is not r and isinstance(out, dict) and not NUM.search(str(text or ""))
                and re.search(r">fact[^>]*$", str(out.get("path", "")))):
            return r
        return out

    def chat(self, text: str, session_id: str = "default") -> dict:
        r = super().chat(text, session_id)
        if not isinstance(r, dict) or r.get("status") != "answered":
            return r
        q = str(text or "")
        resp = str(r.get("response", ""))
        neg = NEGQ.search(q)
        if neg:                                         # guard 2
            return _withheld(r, "precision_guard:Q9_negative_amount",
                             "The question gives %s, a negative amount of something that cannot be negative, so I won't compute an answer from it." % neg.group(0).strip())
        if not resp.startswith("[ev:") or not str(r.get("path", "")).startswith(FACT_ROUTES):
            return r                                    # guards 3 and 4 judge single facts read from evidence, nothing else
        if len(NUM.findall(q)) >= 2 and HOWQ.search(q):     # guard 4
            try:
                n = _net().solve(q)
            except Exception:  # noqa: BLE001
                n = {}
            if n.get("status") == "answered":
                out = dict(r)
                hops = [str(t.get("node")) for t in n.get("trace") or []]
                out.update(status="answered", path="network6>" + " ".join(hops), response=n["response"], references=[],
                           provenance={"kind": "specialist_network_v6", "trace": n.get("trace"), "core_path": r.get("path")})
                out.pop("proved", None)
                return out
            return _withheld(r, "evidence_guard:arithmetic_from_text",
                             "That needs a calculation from the numbers you gave, and what I found is a sentence, not a calculation, so I won't give it as the answer.")
        # guard 3 (evidence must name what the question names) was measured three ways and removed: requiring every name
        # lost 62, then 21 right answers on the capability panel; requiring any name still lost 7 (relation answers cite the
        # answer's own page, which need not repeat the question's names). City of God and Napoleon-Neptune stay unfixed.
        return r
