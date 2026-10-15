#!/usr/bin/env python3
"""oracle_release_runtime_w517 - CORRECTNESS RELEASE: the leaks sealed test 8 and the RC6 benchmarks found (weak answers
asserted unchecked; desk and self replies to questions; broken text), as general rules over (question, route, reply), and the
verified-reach layer made fail-closed: if its verifier cannot be opened, weak answers to factual questions are withheld, and
opening it is retried instead of being given up for the life of the process.

precision_guard_v9 - fold w517 over w516: the leaks sealed test 8 and the RC6 benchmarks found, as general rules, and a
second presentation pass. Designed on DEVELOPMENT material only (the w515 harvest, the spent sealed tests 3-8, the RC6
benchmark replies - all spent); sealed test 9 was locked before this file existed.
  REACH v2   verified reach (w515) never saw three kinds of factual question, so their weak-route replies were asserted
             unchecked: a GENERIC "you" ("What will happen if you stand close to a microwave?", "Which vaccines modify your
             DNA?"), a trivia question with no question mark ("Rooney scored his first goal against which club"), and a
             relation question its definition exemption misread ("Who was Pierre Curie married to?" read as "who was X?").
             Those now go the same way: typed relation form first, else the cube's verification, else withheld.
  R3b        the assistant's "you've reached Oracle7 ... can't do that part myself" desk reply to a question that is not a
             request ("Do you only go out to bars on weekends?", "Which vaccines modify your DNA?")
  R7b        a decline written in words but labelled answered ("I didn't fully parse that, so I won't guess")
  R6b        algebra over the option letters of a multiple-choice question ("11059200*E*I*A*B*C")
  R10        an asserted sentence the store cut short ("an order by U.S.", "an autobiography by G.")
PRESENTATION v2 (never changes what is asserted): punctuation and empty labels left inside brackets by stripped
pronunciations ("( ; The Wayward Woman)", "(Berber: ; )"), a space before punctuation ("BC ."), a bracket the store left
unclosed ("1642 (N.S."), runs of spaces, a fraction restating the asked decimal ("5/2 hours" -> "2.5 hours"), year ranges
whose dash was stripped ("(1799 1853)").
"""
import html
import re
import time

from oracle_release_runtime_w516 import OracleReleaseRuntimeW516 as _Base

import oracle_release_runtime_w516 as _G8   # guard v8, as admitted in w516
import relation_forms_v2 as _F2
import verified_reach_v1 as _VR
import verified_retrieval_v1 as _V

TAGS = re.compile(r"\[ev:[a-z_]+\]|\[[a-z]+_[0-9a-f]{6,}\]|\[\d+\]")
SEG_TAG = re.compile(r"(\s*\[(?:ev:[a-z_]+|[a-z]+_[0-9a-f]{6,}|\d+)\])")
GENERIC_YOU2 = re.compile(
    r"\byour\s+(?:own\s+)?(?:dna|genes?|body|brain|skin|hair|heart|blood|teeth|tooth|eyes?|ears?|nose|stomach|liver|lungs?|bones?|"
    r"muscles?|health|immune\s+system|income|earnings|take-home|salary|pay|taxes|wages|savings|house|home|car|kids|children|child|"
    r"baby|dog|cat|pet|fingers?|nails?|face|head|legs?|arms?|feet|hands?|knuckles|eyesight|vision|weight|coworkers?|"
    r"co-workers?|boss|employer|landlord|neighbou?rs?|doctor|lawyer|bank|wallet|credit\s+score)\b|"
    r"\bhow\s+(?:can|should|could)\s+you\s+(?!feel\b|help\b)\w+|\bwhat\s+(?:will\s+)?happens?\s+(?:if|when)\b|"
    r"\b(?:would|could|might|do|can)\s+you\s+(?:find|see|expect\s+to\s+(?:find|see)|call|measure)\b|\bare\s+you\s+(?:allowed|required|legally)\b|"
    r"\bif\s+you(?:'re|\s+are)\b", re.I)
TRIVIA_NOQ = re.compile(r"^\s*(?:which|who|whom|whose|in\s+which|in\s+what|name\s+the|name)\b|"
                        r"\b(?:which|whom|what)(?:\s+[\w'\-]+){0,3}\s*\.?\s*$", re.I)
OPEN_REQ = re.compile(r"^\s*(?:what\s+is|what's|what\s+are|tell|explain|describe|give|list|write|show|make|create|compare|help|"
                      r"summari[sz]e|define|can|could|would|will|please|let's|lets)\b", re.I)
REQUEST = re.compile(r"^\s*(?:can|could|would|will)\s+you\b|\bplease\b|^\s*(?:book|order|call|send|buy|reserve|schedule|cancel|"
                     r"set|remind|text|email|pay|transfer|open|close|turn)\b", re.I)
DESK = re.compile(r"You've reached Oracle7, an AI assistant rather than a person or a front desk", re.I)
DECLINE_WORDS = re.compile(r"\bso I won't guess\b|\bI didn't fully parse that\b|\bI can't verify an answer\b", re.I)
OPTION_ALGEBRA = re.compile(r"(?:\*[A-J]){3,}")
NOT_DEF = re.compile(r"\b(?:to|at|on|about|as|into|after|for|by|with|from|in|of)\s*$|\b(?:married|born|died|buried|known|"
                     r"called|named|located|founded|played|written|painted|composed|directed|invented|discovered|elected|"
                     r"killed|assassinated|educated|raised|related|famous|responsible)\b", re.I)
DEBRIS = re.compile(r"^\s*[;,:]|[;,:]\s*$|[;,]\s*[;,]|:\s*;|^\s*$")
ABBR_END = re.compile(r"(?:^|[\s(])(?:U\.S|U\.K|U\.N|E\.U|St|Dr|Mr|Mrs|Ms|Mt|Vol|Inc|Ltd|Gen|Gov|Sen|Rev|Prof)\.$")
INITIAL_END = re.compile(r"(?:^|\s)([A-Z])\.$")
LETTER_NAMES = re.compile(r"\b(?:Vitamin|Malcolm|War|Hepatitis|Type|Plan|Generation|Class|Group|Category|Grade|Model|Section|"
                          r"Part|Appendix|Annex|Schedule|Article|Team|Block|Gate|Level|Row|Phase|Exhibit|Ward|Wing|Unit|"
                          r"Article|Tier|Vol|Volume|Track|Disc|Side|Channel|Platform|Pier|Terminal|Zone|Version)\s+[A-Z]\.$")


def visible(resp):
    return " ".join(TAGS.sub(" ", str(resp)).split())


def first_sentence(vis):
    # never split after an initial ("T. S. Eliot.")
    return re.split(r"(?<=[.!?])(?<!\b[A-Z]\.)\s+(?=[A-Z])", vis, 1)[0].strip()


def truncated(sent):
    """the asserted sentence ends on a fragment the store cut ("by U.S.", "by G.", "(N.S.")"""
    s = sent.rstrip()
    if s.endswith("…"):
        return False
    if ABBR_END.search(s) and not re.search(r"\bthe\s+U\.[SKN]\.$|\bthe\s+E\.U\.$|,\s*D\.C\.$|\bD\.C\.$", s):
        return True
    m = INITIAL_END.search(s)
    if m and not LETTER_NAMES.search(s) and not re.search(r"\b(?:World\s+War|Pope\s+\w+|King\s+\w+)\s+[IVX]+\.$|\b[IVX]{1,4}\.$", s):
        return True
    return False                                          # an unclosed bracket is repaired by present2, not withheld


def factual2(q):
    """the questions w515's verified reach did not see: generic-you, trivia without '?', plus everything guard v8 calls factual"""
    q = str(q or "")
    if _G8.factual(q):
        return True
    if "?" in q:
        if not _G8.CHAT.search(q):
            return False
        rest = GENERIC_YOU2.sub(" ", _G8.GENERIC_YOU.sub(" ", q))
        return not _G8.CHAT.search(rest) and bool(_G8.WHW.search(q) or _G8.YESNO.match(q) or re.match(r"^\s*how\b", q, re.I))
    words = q.split()
    return len(words) >= 5 and not _G8.CHAT.search(q) and not OPEN_REQ.match(q) and bool(TRIVIA_NOQ.search(q.strip().rstrip(".")))


def defines_asked2(q, out):
    m = _VR.DEF_Q.match(str(q))
    if not m:
        return False
    x = (m.group(1) or m.group(2) or "").strip()
    if NOT_DEF.search(x):
        return False
    return _VR.defines_asked(q, out)


REACH2_ON = {"generic_you", "no_qmark", "definition_misread"}


def reach2_category(q, out):
    """why w515 passed this weak-route turn over (None = it did not, or the turn is not a factual question)"""
    q = str(q or "")
    if not factual2(q) or defines_asked2(q, out):
        return None
    if _VR.factual(q):
        return "definition_misread" if _VR.defines_asked(q, out) else None
    if not q.rstrip().endswith("?"):
        return "no_qmark"
    if _G8.CHAT.search(q):
        return "generic_you"
    return "nonfront_wh"                                  # v8's R8 class: measured net-negative, off


def reach2(q, out, tt, cube):
    """verified reach for the turns w515 passed over; None = leave the reply as it is. tt/cube None = the verifier could not
    be opened this turn: a weak answer to a factual question is then withheld, never asserted unchecked (fail closed)."""
    if not isinstance(out, dict) or out.get("status") != "answered":
        return None
    path = str(out.get("path", ""))
    if not path.startswith(_VR.WEAK):
        return None
    if cube is None:
        if factual2(q) and not defines_asked2(q, out):
            new = dict(out)
            new.update({"status": "withheld", "path": "unverified:verifier_unavailable|%s" % path,
                        "response": "I can't check that answer right now, so I won't assert it."})
            return new
        return None
    if _VR.factual(q) and not _VR.defines_asked(q, out):
        # w515 must have handled this turn; a weak path still here means its verifier was down when the turn ran
        try:
            return _VR.turn(q, out, tt, _F2, cube, _V.verify)
        except Exception:  # noqa: BLE001
            new = dict(out)
            new.update({"status": "withheld", "path": "unverified:verifier_error|%s" % path,
                        "response": "I can't check that answer right now, so I won't assert it."})
            return new
    cat = reach2_category(q, out)
    if cat not in REACH2_ON:
        return None
    qq = q if q.rstrip().endswith("?") else q.rstrip(" .") + "?"
    if tt is not None and _F2.form_of(qq):
        try:
            a, form = _F2.answer(tt, qq)
        except Exception:  # noqa: BLE001
            a, form = None, None
        if a and a.get("answer"):
            return _VR.relation_reply(out, a, form)
    return _V.verify(qq, out, cube)


def guard8_any(q, out, cube, rs):
    """guard v8's rules for a question v8's own factual() did not recognise (generic-you, no '?')"""
    keep = _G8.factual
    _G8.factual = lambda _q: True
    try:
        return _G8.guard(q, out, cube, rs)
    finally:
        _G8.factual = keep


def guard9(q, out, cube, rs, changed=False):
    if not isinstance(out, dict) or out.get("status") != "answered":
        return None
    q = str(q or "")
    path = str(out.get("path", ""))
    resp = str(out.get("response", ""))
    vis = visible(resp)
    fact = factual2(q)
    if changed or (fact and not _G8.factual(q)):           # replies guard v8 never judged
        r8 = guard8_any(q, out, cube, rs) if fact else _G8.guard(q, out, cube, rs)
        if r8:
            return r8
    if DECLINE_WORDS.search(vis):
        return "R7b_decline_in_words"
    if OPTION_ALGEBRA.search(vis) and re.search(r"\(A\)|\bOptions?:", q):
        return "R6b_option_letter_algebra"
    asks = q.rstrip().endswith("?") or bool(_G8.WHW.search(q))
    if DESK.match(vis) and asks and not REQUEST.search(q):
        return "R3b_desk_reply_to_question"
    # "Fruit, cricket and horseshoe are varieties of what type of animal?" read as talking to someone called Fruit; a real
    # vocative turn ("Jenny, what's wrong with you?", "Hey Rachael, what's up?") carries the conversation's own words
    if re.search(r"got me mixed up with .{1,40}? - I'm Oracle7", vis) and "?" in q and _G8.WHW.search(q) and not _G8.CHAT.search(q):
        return "R3d_vocative_misread"
    if fact and path.startswith(("organ:converse", "organ:self", "act:about", "self:", "worker:")) and not _G8.factual(q) \
            and not re.search(r"\bboth\b", q, re.I):
        return "R3c_chat_reply_to_generic_fact"
    if fact and path.startswith("document_runtime") and (re.fullmatch(r"-?[\d.,]+", vis.strip()) or
                                                         re.search(r"\bI am the Oracle Relational\b", vis)):
        return "R5b_document_runtime_non_answer"
    if fact and not path.startswith(("organ:code", "synth", "code", "kernel_walk", "essay", "game:", "compose:essay", "organ:essay")):
        if truncated(first_sentence(vis)):
            return "R10_truncated_sentence"
    return None


def _clean_bracket(m):
    inner = m.group(1)
    if "(" in inner or len(inner) > 400 or not DEBRIS.search(inner):
        return m.group(0)
    parts = [p.strip() for p in inner.split(";")]
    keep = []
    for p in parts:
        p = re.sub(r"^[\s,;:]+|[\s,;]+$", "", p)
        if not p or p.endswith(":") or re.fullmatch(r"[\W_]+", p):
            continue
        keep.append(p)
    new = "; ".join(keep)
    if new and new == inner.strip():
        return m.group(0)
    return " (%s)" % new if new else ""


def _close_brackets(s):
    """a bracket the store left unclosed (no ")" anywhere after it): cut it and the rest of its passage, up to the next
    evidence tag; a bracket closed after a tag ("(directive [ev:x] 2026)") is whole and stays"""
    stack, unclosed = [], []
    for i, ch in enumerate(s):
        if ch == "(":
            stack.append(i)
        elif ch == ")" and stack:
            stack.pop()
    unclosed = stack
    for start in reversed(unclosed):
        tag = SEG_TAG.search(s, start)
        end = tag.start() if tag else len(s)
        if not re.search(r"\w", s[:start].split("]")[-1]):
            continue
        if re.search(r"[.!?]\s+[A-Z]", s[start:end]):     # more sentences follow inside the passage: not a cut-off tail
            continue
        head = s[:start].rstrip(" ,;:–-")
        s = head + ("" if head.endswith((".", "!", "?", "…")) else ".") + s[end:]
    return s


def _verdict_words(m):
    import ast
    try:
        d = ast.literal_eval(m.group(2))
    except Exception:  # noqa: BLE001
        return m.group(0)
    if not isinstance(d, dict):
        return m.group(0)
    bits = []
    for k, v in d.items():
        k = str(k).replace("_", " ")
        if isinstance(v, dict):
            inner = []
            for k2, v2 in v.items():
                k2 = str(k2).replace("_", " ")
                if isinstance(v2, (list, tuple)) and len(v2) == 2:
                    inner.append("%s %s against %s" % (k2, v2[1], v2[0]))
                else:
                    inner.append("%s %s" % (k2, v2))
            bits.append("%s (%s)" % (k, ", ".join(inner)))
        else:
            bits.append("%s %s" % (k, v))
    return "%s, %s" % (m.group(1), "; ".join(bits))


def present2(q, out):
    if not isinstance(out, dict) or not out.get("response"):
        return out
    path = str(out.get("path", ""))
    r = str(out["response"])
    # code is never touched (indentation and brackets are meaning); essays are prose and are
    if path.startswith(("organ:code", "synth", "code", "game:", "self:expression")) or \
            "```" in r or re.search(r"\n[ \t]{2,}\S|\bdef \w+\(|\breturn\b|\bfunc \w+\(|\bpackage \w+\n", r) or \
            path.startswith("organ:math") and "\n" in r:
        return out
    parts = SEG_TAG.split(r)
    for i in range(0, len(parts), 2):                   # prose segments; tags stay exactly as they are
        s = parts[i]
        if _G8.ENTITY.search(s):                        # "98.6&nbsp;F" (v8 never reached the essay walker)
            s = _G8.ENTITY.sub(lambda mm: html.unescape(mm.group(0)), s)
        # a passage the store cut at an initial or abbreviation ("an autobiography by G."): mark the cut
        core = s.rstrip()
        if core.endswith(".") and len(core) > 20:
            last = re.split(r"(?<=[.!?])(?<!\b[A-Z]\.)\s+(?=[A-Z])", core)[-1]
            if truncated(last) and last.count("(") <= last.count(")"):
                s = core[:-1] + "…" + s[len(core):]
        s = re.sub(r"\s?\(([^()]*)\)", _clean_bracket, s)
        s = re.sub(r"\((1\d{3}|20\d{2})\s+(1\d{3}|20\d{2})\)", "(\\1–\\2)", s)
        # "the wall stretches ." - a value was stripped after a lowercase word: say so ("stretches…"), never hide it
        s = re.sub(r"(?<=[a-z])[ \t]+\.(?=\s|$)", "…", s)
        s = re.sub(r"(?<=[\w)\]\"'])[ \t]+([.,;:!?])(?=[\s\"')\]]|$)", r"\1", s)
        s = re.sub(r"(?<=\S)[ ]{2,}(?=\S)", " ", s)
        parts[i] = s
    s = "".join(parts)
    # the self organ quotes its directive cut at a fixed width: "Ben Horn (directive, 2026-08-29: set a ... for the model t"
    s = re.sub(r"\(directive, (\d{4}-\d{2}-\d{2}):[^()]{0,80}?(?=,\s|\s+has\s)", r"(directive of \1)", s)
    # the self organ prints a gate verdict as a raw dict: "refusal was w511: {'below_baseline': {'answered_rate': [a, b]}}"
    s = re.sub(r"(\bw\d+): (\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\})", _verdict_words, s)
    # a stored phrase quoted at a fixed width ("... tell a joke o"): mark the cut
    s = re.sub(r'"([^"\n]{100,}?[A-Za-z0-9,])"', lambda mm: '"%s…"' % mm.group(1).rstrip(" ,"), s)
    s = _close_brackets(s)
    for m in list(re.finditer(r"(?<![\d./])(\d+)/(\d+)(?=\s+[a-z])", s)):
        a, b = int(m.group(1)), int(m.group(2))
        if not b:
            continue
        for t in re.findall(r"(?<![\d.])\d+\.\d+(?![\d.])", str(q)):
            if abs(float(t) - a / b) < 1e-9:
                s = s.replace(m.group(0), t)
                break
    if s == r:
        return out
    new = dict(out)
    new["response"] = s
    return new


WITHHELD = "I can't verify an answer to that exact question, so I won't guess."


class OracleReleaseRuntimeW517(_Base):

    def _c517(self):
        o = self._c515() if hasattr(self, "_c515") else None
        if not o and getattr(self, "_c515_o", None) is False:
            now = time.time()
            if now - getattr(self, "_c517_retry", 0.0) > 30.0:
                self._c517_retry = now
                self._c515_o = None
                try:
                    o = self._c515()
                except Exception:  # noqa: BLE001
                    o = None
        return o or None

    def chat(self, text: str, session_id: str = "default") -> dict:
        out = super().chat(text, session_id=session_id)
        if not isinstance(out, dict):
            return out
        q = str(text)
        try:
            o = self._c517()
            cube, tt = (o[0], o[1]) if o else (None, None)
            new = reach2(q, out, tt, cube)
            changed = new is not None
            cur = new if changed else out
            rule = guard9(q, cur, cube, getattr(tt, "rs", None), changed=changed)
        except Exception:  # noqa: BLE001 - fail closed: an unchecked weak answer to a factual question is not asserted
            cur, rule = out, None
            try:
                if out.get("status") == "answered" and str(out.get("path", "")).startswith(_VR.WEAK) and factual2(q):
                    rule = "verifier_error"
            except Exception:  # noqa: BLE001
                pass
        if rule and cur.get("status") == "answered":
            new = dict(cur)
            new.update({"status": "withheld", "path": "precision_guard:%s|%s" % (rule, cur.get("path")), "response": WITHHELD,
                        "references": [], "provenance": {"kind": "precision_guard", "rule": rule, "withheld_path": cur.get("path"),
                                                         "withheld_response": str(cur.get("response", ""))[:400]}})
            cur = new
        try:
            return present2(q, cur)
        except Exception:  # noqa: BLE001
            return cur
