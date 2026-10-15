#!/usr/bin/env python3
"""oracle_release_runtime_w521 - CAPABILITY RELEASE: the core calls two new kinds of Oracle7 agent on the turns it declines.

Ben 2026-10-04: use Oracle7's own agents. The 99 standing specialists answered 3 of 1,100 MMLU-Pro / MATH development
questions; these agents were built from those benchmarks' own development material (spent windows only):
  MATHS AGENT (wander-train/math_solver_v1.py): competition-format problems (LaTeX in $...$ / \\[...\\]) answered exactly by
    typed families (evaluate, solve, solve-then-evaluate, substitute, function values, number theory, counting); every
    answer checked by an independent second method; runs in a forked child with a hard 4 s limit. Development (400 spent
    MATH-500 problems): 19 answered, 19 right (2 scored wrong by the benchmark scorer's TeX normaliser: 11\\sqrt2 vs
    11\\sqrt{2}). Gate panel v25 competition_math (MATH test outside MATH-500, independent, counts only): 7 answered, 6 right.
  CHEMISTRY AGENTS (wander-train/chem_agents_v1.py: gas, pH, photon, colligative, kinetics) on MULTIPLE-CHOICE turns:
    asked the question stem without the options; an option is chosen only if EXACTLY ONE option carries the computed value
    in the same dimension within 1.5% (wander-train/mc_adapter_v1.py). Development (595 spent MMLU-Pro chemistry rows):
    4 right, 0 wrong.
Never overridden: any turn the core answered (guard v11 may still withhold it), the core's deliberate verdicts (paths
ending does_not_follow / out_of_fragment). Agent replies are labelled with the agent that gave them.

precision_guard_v11 - fold w521: four reply classes that answered benchmark-shaped questions wrongly far more often than
rightly on the live development harvest of head w520 (4,500 questions, spent windows only):
  Q1 dump-for-question   an explain-simply / definition / timeline / compare / summary reply to a QUESTION that does not ask
                         for an explanation, a definition, a timeline or a comparison ("Does learning music help boost your
                         thinking?" -> "In simple terms: Learning is ...")                      harvest: 18 wrong / 3 right
  Q2 mention-reply       the conversation route's "Got it. Since you mention X: <definition of X>" to a wh-question
                         ("Summer Holiday starred what actor ...?")                              harvest: 10 wrong / 2 right
  Q3 sentence-start name "I think you've got me mixed up with Who / Typically / Generals Gallieni" - the question's own first
                         words read as a person being addressed                                  harvest: 5 wrong / 0 right
  Q4 bare value          a document reply that is only a number, to a question asking for something else ("Specify the day,
                         month, and year ..." -> "0.666666666667")
Conversation turns are protected by the question test: a request ("Summarize the Great Wall of China.", "Jenny, what's wrong
with you?") is not a question of the kinds these rules read. guard11(q, out) -> rule name or None.
"""
import re

from oracle_release_runtime_w381 import OracleReleaseRuntimeW381 as _Base

try:
    import math_solver_v1 as _MS
    import chem_agents_v1 as _CA
    import mc_adapter_v1 as _MC
except Exception:  # noqa: BLE001 - without its agents the fold is its parent plus guard v11
    _MS = _CA = _MC = None

TAGS = re.compile(r"\[ev:[a-z_]+\]|\[[a-z]+_[0-9a-f]{6,}\]|\[\d+\]")
WH = re.compile(r"\b(who|whom|whose|what|which|where|when|why|how)\b", re.I)
AUX = re.compile(r"^\s*(?:is|are|was|were|do|does|did|can|could|has|have|had|will|would|should)\b", re.I)
ASKS_DUMP = re.compile(r"\b(explain|explanation|simple|simply|define|definition|meaning|mean\b|what is an? |what are |what's an? |"
                       r"summar|overview|timeline|history of|chronolog|compare|comparison|difference|differ|versus|vs\.?|"
                       r"tell me about|describe)\b", re.I)
REQUEST = re.compile(r"^\s*(?:please|can you|could you|would you|will you|let's|lets|write|tell|give|show|make|list|summari[sz]e|"
                     r"explain|describe|compare|define)\b", re.I)
CHATTY = re.compile(r"\b(i|i'm|i've|me|my|we|us|our|hi|hey|hello|thanks|thank)\b", re.I)


def visible(r):
    return " ".join(TAGS.sub(" ", str(r)).split())


def question(q):
    """a question asked of the world: ends with '?' or opens with a wh-word / auxiliary, or embeds a wh-word in a long
    trivia-style sentence; not a request, not small talk"""
    q = str(q or "").strip()
    if REQUEST.match(q) or CHATTY.search(q):
        return False
    if q.endswith("?"):
        return bool(WH.search(q) or AUX.match(q))
    return len(q.split()) >= 7 and bool(WH.search(q))


def guard11(q, out):
    if not isinstance(out, dict) or out.get("status") != "answered":
        return None
    q = str(q or "")
    path = str(out.get("path", ""))
    vis = visible(out.get("response", ""))
    if not question(q):
        return None
    # Q1 / Q2 RETIRED by tally (Q1 cost 9 conversation turns and 14 right panel answers; Q2 net +1)
    m = re.search(r"got me mixed up with (.{1,40}?) - I'm Oracle7", vis)
    if m and len(q.split()) >= 7:
        first = re.split(r"[\s,]+", q.strip())[0]
        name = m.group(1).split()[0].strip(",")
        if name == first and (re.fullmatch(r"(?i)who|whom|whose|what|which|where|when|why|how|is|are|was|were|do|does|did|can|"
                                           r"could|has|have|had|will|would|should|the|a|an|in|on|at|of|for|from|after|before|"
                                           r"during|since|until|although|though|if|while", name) or name.lower().endswith("ly")):
            return "Q3_sentence_start_name"
    if path.startswith("document_runtime") and re.fullmatch(r"-?[\d.,]+", vis.strip()):
        return "Q4_bare_value"
    return None


WITHHELD = "I can't verify an answer to that exact question, so I won't guess."
DELIBERATE = ("does_not_follow", "out_of_fragment")
OPTION = re.compile(r"\(([A-J])\)\s*(.*?)(?=\s*\([A-J]\)\s|$)", re.S)
_CHEM = {}


def _vals(s):
    """the set of exact values (integers, decimals, fractions) a short answer states: "x = -4/3 or x = 5/2" -> {-4/3, 5/2}"""
    from fractions import Fraction
    out = set()
    for m in re.finditer(r"(?<![\w.])(-?\d+(?:\.\d+)?)(?:\s*/\s*(\d+))?(?![\w.])", re.sub(r"\[[^\]]*\]", " ", str(s))):
        try:
            v = Fraction(m.group(1)) / (int(m.group(2)) if m.group(2) else 1)
        except (ValueError, ZeroDivisionError):
            continue
        out.add(v)
    return frozenset(out)


def _agents():
    if not _CHEM and _CA is not None:
        _CHEM.update({k: v() for k, v in _CA.AGENTS.items()})
    return _CHEM


class OracleReleaseRuntimeW521(_Base):

    def chat(self, text: str, session_id: str = "default") -> dict:
        out = super().chat(text, session_id=session_id)
        if not isinstance(out, dict):
            return out
        q = str(text)
        try:
            if out.get("status") == "answered":
                rule = guard11(q, out) or self._c521_check(q, out)
                if rule:
                    new = dict(out)
                    new.update({"status": "withheld", "path": "precision_guard:%s|%s" % (rule, out.get("path")),
                                "response": WITHHELD, "references": [],
                                "provenance": {"kind": "precision_guard", "rule": rule, "withheld_path": out.get("path"),
                                               "withheld_response": str(out.get("response", ""))[:400]}})
                    return new
                return out
            if str(out.get("path", "")).endswith(DELIBERATE):
                return out
            new = self._c521_agents(q)
            return new if new else out
        except Exception:  # noqa: BLE001 - an agent failure never costs the core's own reply
            return out

    @staticmethod
    def _c521_check(q, out):
        """R_mc: on a multiple-choice turn an answer must name an option or match exactly one option's value.
        R_sci: a specialist's reply to a question stated in scientific notation must carry that power of ten (the water
        specialist read "2.7 x 10^-6 M" as 6 and answered pH -0.78)."""
        body = " ".join(str(out.get("response", "")).split())
        if "Options:" in q and "(A)" in q and _MC is not None:
            if not re.match(r"(?:\[ev:[a-z_]+\]\s*)?Option \([A-J]\)", body):
                options = [o.strip() for _, o in OPTION.findall(q.partition("Options:")[2])]
                quoted = [o for o in options if len(o) >= 8 and o.lower() in body.lower()]
                first = re.split(r"\.\s+(?:In steps|Checked|Method)", body)[0]
                mine = _vals(first)
                same = [o for o in options if mine and _vals(o) == mine]
                if _MC.match(body, options) is None and len(quoted) != 1 and len(same) != 1:
                    return "R_mc_no_option"
        if str(out.get("path", "")).startswith("specialist_call"):
            exps = re.findall(r"10\s*\^\s*\(?\s*([-+]?\d+)", q)
            if exps and not any(re.search(r"(?:10\s*\^\s*\(?\s*|e)" + re.escape(e.lstrip("+")) + r"\b", body) for e in exps):
                return "R_sci_exponent_dropped"
        return None

    def _c521_agents(self, q):
        if _MS is None:
            return None
        if "Options:" in q and "(A)" in q:
            stem, _, opts = q.partition("Options:")
            options = [o.strip() for _, o in OPTION.findall(opts)]
            got = []
            for name, ag in _agents().items():
                r = ag.answer(stem)
                if r and r.get("status") == "answered":
                    got.append((name, r))
            if len(got) != 1 or len(options) < 2:
                return None
            name, r = got[0]
            k = _MC.match(r["response"], options)
            if k is None:
                return None
            letter = "ABCDEFGHIJ"[k]
            return {"status": "answered", "path": "agent:%s>mc_unique_option" % name,
                    "response": "Option (%s) %s. %s [%s agent]" % (letter, options[k], r["response"], name), "references": [],
                    "provenance": {"kind": "agent", "agent": name, "check": "exactly one option matches the computed value"}}
        if re.search(r"\$[^$]+\$|\\\[|\\\(", q):
            r = _MS.solve_bounded(q, 4.0)
            if not r:
                return None
            return {"status": "answered", "path": "agent:maths>%s" % r["family"], "response": _MS.reply(r) + " [maths agent]",
                    "references": [], "verified_warrant": r["check"],
                    "provenance": {"kind": "agent", "agent": "maths", "family": r["family"], "check": r["check"]}}
        return None
