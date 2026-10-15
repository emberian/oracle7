#!/usr/bin/env python3
"""oracle_release_runtime_w510 - PRECISION GUARD over w508.

precision_guard_v3 - withhold replies that do not answer the FACTUAL question that was asked (wiring sprint, step 1).

v3 = v2 with two corrections found on the gate's own panel: an advice request ("how to start learning guitar") is not a slot
question, and the evidence rule (G3) asks for at least ONE of the question's specifics instead of half (v2 withheld right
answers whose sentence names the subject only as "He ...").
v1 (fold w509) was rejected by the gate: capability 1156 -> 1137 (false yes 22 -> 17). Cause: it judged conversation turns as
factual questions ("Hi, Becky, what's up?" is not a question to be verified), and judged typed relation / cube answers by
their supporting sentence instead of by their checked relation. v2:
  CHAT   a turn that addresses the listener (you / I / hi / excuse me / please ...) is conversation: no factual rule applies
  G1     deflections: a vocative read only of a LIST ("A, B, and C are types of?"), not of someone addressed ("Cindy, ...");
         a chat/lookup reply (statement, request, advice) only when the question asks for a slot, not "what is/are X"
  G2     shape: a definition offered for an INSTANCE question ("what's a trait that ...", "what are some people who ...");
         a timeline/list/premises/evaluate/compare shape the question did not ask for (as v1)
  G3     evidence: retrieved sentences (page, full-text, bridge, both, comparison) must name half the question's specifics
  G3s    a specialist's reply must keep the qualifier it was given ("President OF COSTA RICA")
  G4     the reply says no specialist covers the question
  G5     one retrieved sentence offered for an "all / every / always ..." claim about a group
  G6     a typed relation must be the relation the question asks about: inception needs a founding question, citizenship
         cannot answer "born", a bare country cannot answer where an event was held
Rules are properties of (question, route, reply); none names an item. Designed on DEV windows; checked against the gate panel
(the gate's own instrument) before submission.
"""
import re

from oracle_release_runtime_w508 import OracleReleaseRuntimeW508 as _Base

WH = re.compile(r"^\s*(who|whom|whose|what|what's|which|where|when|why|how|in what|in which|at what|on what|for what|from what|"
                r"to what|by what|name the|determine|find|compute|calculate|solve|is|are|was|were|do|does|did|can|could|has|have)\b", re.I)
CHAT = re.compile(r"\b(you|your|yours|you're|you've|yourself|i|i'm|i've|i'd|me|my|mine|we|us|our|hi|hey|hello|excuse me|please|"
                  r"sir|madam|ma'am|mum|mom|dad|thanks|thank)\b", re.I)
OPEN = re.compile(r"\b(tell me|about|explain|describe|thoughts|opinion|how to|how do|how can|how should|how would|tips?|advice|"
                  r"best way|ways to|steps to|recommend)\b", re.I)
DEF_SHAPE = re.compile(r"^\s*(what|who)('s| is| are| was| were)\s+(?!some\b|any\b|something\b|one\b)", re.I)
RELATIVE = re.compile(r"\b(that|which|who|whom|whose|where|when)\b", re.I)
STOP = set("""a an the of in on at to for from by with and or but is are was were be been being do does did has have had what
which who whom whose where when why how that this these those it its as into than then there their they them he she his her
him we our you your i me my not no yes all any some many much more most one two first name called known type kind""".split())


def _question(q: str) -> bool:
    return q.rstrip().endswith("?") or bool(WH.match(q))


def _specifics(q: str) -> list:
    """the question's specifics: capitalised words not at sentence start, 4-digit years, quoted titles"""
    out = []
    for m in re.finditer(r"[\"“'‘]([^\"”'’]{3,60})[\"”'’]", q):
        out += [w for w in re.findall(r"[A-Za-z0-9]+", m.group(1)) if w.lower() not in STOP and len(w) > 2]
    words = re.findall(r"[A-Za-z][A-Za-z0-9'\-]*|\d{4}", q)
    for i, w in enumerate(words):
        if re.fullmatch(r"\d{4}", w) or (i > 0 and w[0].isupper() and w.lower() not in STOP and len(w) > 2):
            out.append(w)
    seen, uniq = set(), []
    for w in out:
        k = w.lower().strip("'")
        if k not in seen:
            seen.add(k)
            uniq.append(k)
    return uniq


def _covered(term: str, text: str) -> bool:
    stem = term[:5] if len(term) > 5 else term
    return re.search(r"\b" + re.escape(stem), text, re.I) is not None


def guard(q: str, out: dict):
    st, path = str(out.get("status", "")), str(out.get("path", ""))
    if st != "answered":
        return None
    resp = " ".join(str(out.get("response", "")).split())
    head = resp[:300]
    ql = q.lower()
    # G4: the reply says it is not covered (applies to every turn)
    if "none of my specialists covers" in resp.lower():
        return "G4_admitted"
    # CHAT: conversation is not a factual question; nothing below applies
    if CHAT.search(q) or not _question(q):
        return None
    # G1: deflections and chat replies to a direct factual question
    if path.startswith("organ:self>vocative") and q.count(",") >= 2:
        return "G1_deflect_list"
    if path.startswith(("organ:converse>statement", "organ:converse>request", "organ:converse>advice")) and \
            not OPEN.search(q) and not (DEF_SHAPE.match(q) and not RELATIVE.search(q)):
        return "G1_chat_reply_to_slot_question"
    if path.startswith("self:read_own_record"):
        return "G1_self_record"
    # G2: answer shape the question did not ask for
    if "definitional" in path and re.match(r"^\s*what('s| is| are| was| were)\s+(some|a|an|something|one|any)\b", q, re.I) \
            and RELATIVE.search(q):
        return "G2_definition_for_instance_question"
    if "timeline" in path and not re.search(r"\b(when|year|date|first|earlier|later|before|after|older|oldest|newer|"
                                            r"came first|century|decade|ago|how long)\b", ql):
        return "G2_time_not_asked"
    if "list_n" in path and not re.search(r"\b(list|name (some|a few|\d+|two|three|four|five)|examples?|\d+ (of|things|ways)|"
                                          r"two|three|four|five|six|seven|eight|nine|ten)\b", ql):
        return "G2_list_not_asked"
    if path.startswith("deduce:premises_held") and not re.search(r"\b(if|given|suppose|assume|premise|all|every|no|some)\b.*[,.;]", ql):
        return "G2_no_premises"
    if path.startswith("organ:math>evaluate") and re.search(r"\b(multiples?|divisible|primes?|digits?|ways|arrange|"
                                                            r"permutations?|combinations?|sequence|series)\b", ql):
        return "G2_not_an_expression"
    if path.startswith("arb:compare") and re.match(r"^\s*according to ", head, re.I):
        return "G2_compare_is_a_definition"
    # G6: a typed relation must be the relation asked about
    props = set(re.findall(r"RELATE:(?:fwd|inv):(P\d+)", path))
    if "P571" in props and not re.search(r"\b(found|establish|form|creat|start|open|launch|incorporat|incept|built|buil|began|begun)", ql):
        return "G6_inception_not_asked"
    if "P27" in props and (re.search(r"\bborn\b", ql) or not re.search(r"\b(citizen|nationality|national|from which country|"
                                                                       r"what country is|which country is)", ql)):
        return "G6_citizenship_not_asked"
    if "P17" in props and re.search(r"\bwhere\b", ql) and not re.search(r"\b(country|nation)\b", ql) and \
            re.search(r"\b(held|take place|took place|hosted|staged|played|fought)\b", ql):
        return "G6_country_for_a_venue"
    # G5: one sentence cannot establish a universal over a group
    if re.search(r"\b(all|every|always|never|only)\b\s+(?!of the time)\w+", ql) and \
            path.startswith(("factoid:fts", "factoid:page", "organ:converse", "compose:", "arb:")):
        return "G5_universal"
    # G3: a retrieved sentence must name the question's specifics
    if path.startswith(("factoid:page", "factoid:fts", "compose:bridge", "compose:both", "compose:comparison")):
        spec = _specifics(q)
        if len(spec) >= 2 and not any(_covered(t, head) for t in spec):
            return "G3_evidence_misses_question"
    # G3s: a specialist's reply must keep the qualifier it was given
    if path.startswith("specialist_call"):
        for m in re.finditer(r"\bof (?:the )?((?:[A-Z][a-z]+)(?: [A-Z][a-z]+)*)", q):
            if not all(_covered(w.lower(), head) for w in m.group(1).split()):
                return "G3s_qualifier_dropped"
    return None


class OracleReleaseRuntimeW510(_Base):

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
