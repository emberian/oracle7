#!/usr/bin/env python3
"""oracle_release_runtime_w539 - CORRECTNESS RELEASE + COVERAGE: two confident wrong answers become declines, and the general
relation reader answers on reading declines (2026-10-14). Evidence: the held-out run in research/coverage_reader/ and the
release-day cases below.

1. COVERAGE: the general relation reader, on declines only. Of the questions the release declines, many have their answer
   one fact away from an entity the question names; the relation specialists miss them because each fires only on phrasings
   it was built for. general_reader_v1 reads them without depending on phrasing, and answers only when independent signals
   agree: the relation is named by the question's own words, the answer is the kind of thing asked for (a person; a city, a
   country... checked on the answer's own classes), exactly one candidate survives, every name the question gives is one it
   linked, and when the question names two or more things at least two agree. Held-out (run once, 2026-10-14) and its
   judging rule are in the release's research folder. It runs only when the chain DECLINED for lack of a reading (did not
   parse, unverified passage, no admitted sentence, a route that withheld); never when a check declined, never on
   conversation acts, a turn that names a year, a private question, or a multi-part turn. Its answer carries the receipt.

2. A NAME IS NOT ARITHMETIC: "What is the half-life of carbon-14?" was answered "-14" by evaluating the name. When the only
   numbers in a question sit inside names (carbon-14, COVID-19, F-35) and it asks no arithmetic, an arithmetic answer is
   withheld.

3. A COMPOSED PROGRAM MUST COUNT WHAT WAS ASKED: the code composer answered "count the vowels in a string" with a program
   that counts the items of a list, checked only against its own reading. A composed program (synth:composed) for a request
   to count a particular thing (vowels) is withheld when it never mentions that thing. Programs from the verified set, and
   other wording differences, are unaffected."""
from __future__ import annotations

import re

from oracle_release_runtime_w538 import OracleReleaseRuntimeW538 as _Base

try:
    import chat_context_v2 as _CC
except Exception:  # noqa: BLE001
    _CC = None
try:
    import general_reader_v1 as _GR
except Exception:  # noqa: BLE001
    _GR = None

READING_DECLINES = ("act:clarify", "unverified:", "corpus_query", "factoid", "deliberation", "capability:", "arb:", "compose",
                    "family_precedence:low_credit", "verified:", "cube:")
CHECK_DECLINES = ("precision_guard", "same_name_guard", "weight:", "chat:unresolved")
PRIVATE = re.compile(r"\b(my|our|your|mine|me|i|we|us)\b", re.I)
YEAR = re.compile(r"\b(1[0-9]{3}|20[0-9]{2})\b")
MULTI = re.compile(r"\b(and|also|then)\b.*\?", re.I)

NAME_NUMBER = re.compile(r"\b[A-Za-z]{1,}-\d+\b")
ARITH = re.compile(r"[+*/^=×÷]|\b(plus|minus|times|divided|multipl\w*|sum|product|difference|quotient|square|cube|root|percent|"
                   r"power|squared|cubed|solve|evaluate|calculate|compute|derivative|integral)\b", re.I)
MATH_PATH = re.compile(r"(^|[>|])(organ:math|op:|algebra:|agent:maths)")

CODE_FILLER = set(("write make create give build python function program code script method class string strings list lists "
                   "number numbers integer integers int text word returns return takes take given input output prints print "
                   "that which the and for with from into each every all its this one two using use then can could would should "
                   "please small simple short new way how what does do show me count counts counting").split())


def _stem(w):
    for suf in ("ing", "es", "s", "ed"):
        if len(w) > len(suf) + 3 and w.endswith(suf):
            return w[: -len(suf)]
    return w


def eligible(q, out):
    if _GR is None or not isinstance(out, dict) or out.get("status") == "answered":
        return False
    path = str(out.get("path", ""))
    if path.startswith(CHECK_DECLINES) or "precision_guard" in path:
        return False
    if not path.startswith(READING_DECLINES) and not any(k in path for k in READING_DECLINES):
        return False
    if "act:clarify" in path and not q.strip().endswith("?") and not re.match(r"(?i)(who|what|which|where|when|in which|name)\b", q.strip()):
        return False
    if PRIVATE.search(q) or YEAR.search(q) or MULTI.search(q) or q.count("?") > 1:
        return False
    return True


def name_is_not_arithmetic(q, out):
    """True when an arithmetic answer came only from numbers that are parts of names"""
    if not isinstance(out, dict) or out.get("status") != "answered" or not MATH_PATH.search(str(out.get("path", ""))):
        return False
    if not NAME_NUMBER.search(q) or ARITH.search(q):
        return False
    rest = NAME_NUMBER.sub(" ", q)
    return not re.search(r"\d", rest)


COUNT_OBJ = re.compile(r"\b(?:count(?:s|ing)?|number of|how many)\s+(?:the\s+|all\s+|every\s+|of\s+the\s+)?([a-z]+)", re.I)
GENERIC_OBJ = set(("words word items item elements element values value numbers number characters character chars char letters letter "
                   "lines line entries entry things thing occurrences occurrence times time digits digit strings string list lists "
                   "unique distinct total them those these they each ones").split())


def composed_misses_request(q, out):
    """a composed (not verified-set) program for a request to count a particular thing that never mentions that thing:
    "count the vowels in a string" answered by a program that counts the items of a list (2026-10-14). Narrow on purpose:
    other wording differences (minimum vs min(), descending vs reverse=True) are not evidence of a wrong program."""
    if not isinstance(out, dict) or out.get("status") != "answered" or not str(out.get("path", "")).startswith("synth:composed"):
        return []
    body = str(out.get("response", "")).lower()
    have = set(_stem(w) for w in re.findall(r"[a-z]+", body))
    miss = []
    for m in COUNT_OBJ.finditer(q):
        w = m.group(1).lower()
        if w not in GENERIC_OBJ and len(w) > 3 and _stem(w) not in have and w not in body:
            miss.append(w)
    return miss


class OracleReleaseRuntimeW539(_Base):
    def chat(self, text: str, session_id: str = "default") -> dict:
        out = super().chat(text, session_id=session_id)
        q0 = str(text or "")
        q = ((out.get("provenance") or {}).get("chat_resolved") or {}).get("read_as") or q0 if isinstance(out, dict) else q0
        if name_is_not_arithmetic(q, out):
            new = dict(out)
            new.update({"status": "withheld", "path": "precision_guard:N1_name_not_arithmetic>%s" % out.get("path"), "references": [],
                        "response": "The number in that question is part of a name, not something to calculate, so I won't answer "
                                    "it as arithmetic."})
            return new
        miss = composed_misses_request(q, out)
        if miss:
            new = dict(out)
            new.update({"status": "withheld", "path": "precision_guard:C1_composed_misses_request>%s" % out.get("path"), "references": [],
                        "response": "I composed a program, but it does not deal with %s, which you asked for, so I won't hand it "
                                    "over. I can write and prove the programs in my verified set." % ", ".join(sorted(set(miss)))})
            return new
        if not eligible(q, out):
            return out
        try:
            r = _GR.answer(q)
        except Exception:  # noqa: BLE001
            r = None
        if not r:
            return out
        new = dict(out)
        new.update({"status": "answered", "path": "general_reader:%s:P%d:%s>%s" % (r["kind"], r["prop"], r["dir"], out.get("path")),
                    "response": "%s. From the Wikidata relation store: %s." % (r["answer"], r["receipt"]), "references": [],
                    "provenance": {"kind": "general_reader", "property": r["prop"], "direction": r["dir"], "asked": r["kind"],
                                   "declined_by": out.get("path"), "declined_response": str(out.get("response", ""))[:300]}})
        if _CC is not None:
            try:
                _CC.update(session_id, q, new)
            except Exception:  # noqa: BLE001
                pass
        return new
