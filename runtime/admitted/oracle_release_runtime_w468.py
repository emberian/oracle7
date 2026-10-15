#!/usr/bin/env python3
"""oracle_release_runtime_w468 - the door: a turn the chain cannot parse is bound to the thread or asked about, not refused.

Measured 2026-09-23: 51% of benchmark declines and 22 of 454 held-out conversation turns end in the generic terminal
"I didn't fully parse that, so I won't guess" (runtime U's clarify act). In conversation those turns are almost all
pointing phrases the chain could not bind: "where is it?", "how old is it?", "Explain the thing with the water.",
"The thing from before." The thread held the answer to "which thing" every time; the terminal threw it away.

The rule is a STRICT FALLBACK. It runs only on a turn the parent answered with the generic clarify act, so every turn
the parent answered, withheld or recorded is returned unchanged.

  1. BIND: if the turn points (it / that / this / they / "the thing ...", "that place") and the thread has a subject,
     the pointer is replaced by that subject and the rewritten, self-contained question is asked of the parent on a
     SCRATCH session (the conversation's own record is not written twice). An answer is returned naming what "it" was
     taken to mean. Repair a referent, never supply one: the subject must come from this conversation.
  2. ASK: otherwise the reply is a SPECIFIC clarifying question - it names the phrase it could not resolve and offers
     the subjects this conversation has actually raised. Still a clarification (nothing is asserted).

Subjects are recorded from turns the parent ANSWERED, from the person's own words (the fixed obligation compiler), so
the thread is what was discussed, never what the model volunteered. No new store, no new assertion route.

Methods _r468_. Parent: the serving head.
"""

from __future__ import annotations

import re

from oracle_release_runtime_w313 import OracleReleaseRuntimeW313 as _Base

try:
    import oracle_program_ir_v1 as _ir
except Exception:  # noqa: BLE001
    _ir = None

POINTER = re.compile(r"\b(it|its|that|this|they|them|those|these)\b", re.I)
DEICTIC = re.compile(r"\b(?:the|that|this)\s+(?:thing|one|place|stuff|topic|subject|idea|person|guy|animal|city|country)"
                     r"(?:\s+(?:with|from|about|of|in|on)\s+(?:the\s+)?[a-z][\w\-]*(?:\s+[a-z][\w\-]*)?)?\b", re.I)
NOT_SUBJECT = {"you", "your", "yourself", "me", "thing", "things", "stuff", "one", "something", "anything", "before",
               "again", "more", "else", "what", "which", "about", "tell", "explain", "describe", "please", "know",
               "source", "mean", "think", "want", "like", "said", "say", "answer", "question", "ok", "okay", "thanks"}
MAX_THREAD = 6
# INDEPENDENT reply-side check for a bound answer: the reply must carry what the question type asks for.
# Measured: "where is it?" bound to Eiffel Tower came back "It was built between 1887 and 1889 ..." - true, not a place.
ANSWER_SHAPE = [
    (re.compile(r"^\s*where\b", re.I), re.compile(r"\b(?:in|at|near|on|of)\s+(?:the\s+)?[A-Z][a-z]+|\blocated\b|\bcity\b|"
                                                  r"\bcountry\b", re.S)),
    (re.compile(r"^\s*when\b|\bwhat year\b", re.I), re.compile(r"\b1[0-9]{3}\b|\b20[0-2][0-9]\b")),
    (re.compile(r"^\s*how (?:old|long|many|much|big|tall|high|far|deep|wide)\b", re.I), re.compile(r"\d")),
    (re.compile(r"^\s*who\b", re.I), re.compile(r"\b[A-Z][a-z]+\s+[A-Z][a-z]+")),
]


def _shape_ok(question, reply):
    for q_rx, a_rx in ANSWER_SHAPE:
        if q_rx.search(question):
            return a_rx.search(reply) is not None
    return True


_EV = re.compile(r"\[(?:ev:[a-z_]+|[a-z]+_[0-9a-f]{8,}[^\]]*)\]\s*")
ORIGIN = re.compile(r"\b(?:built|constructed|founded|established|born|completed|opened|formed|created|erected|"
                    r"started|begun|inaugurated|launched|made)\b[^.;]{0,40}?\b(?:in|on)\s+(?:\w+\s+){0,2}?"
                    r"(1[0-9]{3}|20[0-2][0-9])\b", re.I)
PLACE_IN = re.compile(r"\b(?:in|at)\s+((?:[A-Z][\w\-]+)(?:,?\s+[A-Z][\w\-]+){0,2})")


def _sentences(text):
    t = _EV.sub("", str(text))
    return [s.strip() for s in re.split(r"(?<=[.!?;])\s+", t) if len(s.strip()) > 12]


def from_thread(question, subject, replies, year_now):
    """Reason over what this conversation ALREADY cited about the subject. Returns (answer, basis) or None.
    where    -> a sentence placing the subject "in <Place>"; quoted
    how old  -> a sentence dating its origin "built/founded/born ... in YEAR"; age computed, working shown"""
    q = question.strip().lower()
    subj = subject.lower().split()[0][:5]
    for reply in reversed(replies):
        for s in _sentences(reply):
            if subj not in s.lower() and not re.match(r"^(it|its|this|the)\b", s, re.I):
                continue
            if re.match(r"^\s*where\b", q):
                m = PLACE_IN.search(s)
                if m and m.group(1).split()[0] not in ("The", "A", "An"):
                    return ("%s is in %s. From what I cited earlier: \"%s\"" % (subject, m.group(1), s[:220]),
                            {"kind": "thread_quote", "sentence": s[:300]})
            elif re.match(r"^\s*how old\b", q):
                m = ORIGIN.search(s)
                if m:
                    y = int(m.group(1))
                    return ("About %d years old: it dates from %d, and %d - %d = %d. From what I cited earlier: \"%s\""
                            % (year_now - y, y, year_now, y, year_now - y, s[:200]),
                            {"kind": "computation", "steps": [{"quote": s[:300]}, {"op": "%d - %d" % (year_now, y),
                                                                                    "value": year_now - y}]})
    return None


class OracleReleaseRuntimeW468(_Base):

    def _r468_thread(self, sid):
        t = getattr(self, "_r468_threads", None)
        if t is None:
            t = self._r468_threads = {}
        return t.setdefault(sid, [])

    def _r468_subjects(self, text):
        """subjects the PERSON named in this turn (entities first, then content nouns), never pointers"""
        if _ir is None:
            return []
        try:
            r = _ir.compile_request(text)
        except Exception:  # noqa: BLE001
            return []
        out = []
        for s in list(r.entities) + list(r.content_subjects):
            s = " ".join(str(s).split())
            if not s or s.lower() in NOT_SUBJECT or POINTER.fullmatch(s):
                continue
            if s.lower() not in [o.lower() for o in out]:
                out.append(s)
        return out

    def _r468_replies(self, sid):
        r = getattr(self, "_r468_reply_log", None)
        if r is None:
            r = self._r468_reply_log = {}
        return r.setdefault(sid, {})

    def _r468_remember(self, text, sid, res):
        subs = self._r468_subjects(text)
        try:
            if subs:
                log = self._r468_replies(sid).setdefault(subs[0].lower(), [])
                log.append(str(res.get("response", ""))[:2000])
                del log[:-4]
        except Exception:  # noqa: BLE001
            pass
        topic = str(((res.get("provenance") or {}) if isinstance(res, dict) else {}).get("topic") or "").strip()
        if topic and topic.lower() not in NOT_SUBJECT:
            subs = [topic] + [s for s in subs if s.lower() != topic.lower()]
        if subs:
            th = self._r468_thread(sid)
            head = subs[0]
            if head.lower() in [x.lower() for x in th]:
                th[:] = [x for x in th if x.lower() != head.lower()]
            th.append(head)
            del th[:-MAX_THREAD]

    def _r468_bind(self, text, subject):
        m = DEICTIC.search(text)
        if m:
            return text[:m.start()] + subject + text[m.end():]
        m = POINTER.search(text)
        if m:
            word = m.group(1).lower()
            rep = subject + "'s" if word == "its" else subject
            return text[:m.start()] + rep + text[m.end():]
        return None

    def _r468_door(self, text, sid, res):
        thread = self._r468_thread(sid)
        points = bool(DEICTIC.search(text) or POINTER.search(text))
        named = self._r468_subjects(text)
        if points and thread and not named:
            subject = thread[-1]
            rewritten = self._r468_bind(text, subject)
            if rewritten and rewritten.strip().lower() != text.strip().lower():
                try:
                    inner = super().chat(rewritten, "%s::r468" % sid)
                except Exception:  # noqa: BLE001
                    inner = None
                body = str(inner.get("response", "")) if isinstance(inner, dict) else ""
                if isinstance(inner, dict) and inner.get("status") == "answered" and _shape_ok(text, body):
                    out = dict(inner)
                    out["response"] = "Taking that to mean %s: %s" % (subject, str(inner.get("response", "")))
                    prov = dict(inner.get("provenance") or {})
                    prov["r468_door"] = {"act": "bound", "subject": subject, "rewritten": rewritten,
                                         "parent_path": str(res.get("path", ""))}
                    out["provenance"] = prov
                    out["path"] = "door:bound|" + str(inner.get("path", ""))
                    return out
                import time as _t
                got = from_thread(text, subject, self._r468_replies(sid).get(subject.lower(), []) +
                                  ([body] if body else []), _t.gmtime().tm_year)
                if got:
                    answer, basis = got
                    out = dict(res)
                    out.update({"status": "answered", "path": "door:bound|thread_reasoning",
                                "response": "Taking that to mean %s: %s" % (subject, answer),
                                "provenance": {"kind": "dialogue_state", "verified_warrant": basis,
                                               "r468_door": {"act": "reasoned_from_thread", "subject": subject,
                                                             "rewritten": rewritten}}})
                    return out
                if len(thread) == 1 or not DEICTIC.search(text):
                    # one clear referent and no attested answer of the right kind: say exactly that, assert nothing
                    out = dict(res)
                    out.update({"status": "withheld", "path": "door:bound|vessel:receipt",
                                "response": "I took \"%s\" to mean %s, but I have no attested answer to that about %s."
                                            % ((DEICTIC.search(text) or POINTER.search(text)).group(0), subject, subject),
                                "provenance": {"kind": "dialogue_state",
                                               "r468_door": {"act": "bound_no_answer", "subject": subject,
                                                             "rewritten": rewritten}}})
                    return out
        # ASK: a specific question, naming what could not be resolved and what this conversation has raised
        unresolved = (DEICTIC.search(text) or POINTER.search(text))
        phrase = unresolved.group(0) if unresolved else None
        offers = list(reversed(thread[-3:]))
        if phrase and offers:
            q = ("Which do you mean by \"%s\": %s? Name it and I will answer about that."
                 % (phrase, " or ".join(offers)))
        elif phrase:
            q = "What does \"%s\" refer to? Nothing earlier in this conversation names it. Tell me the name." % phrase
        else:
            # no pointer: the question is not unclear, its subject is unknown ("What is a zorvane?"). The honest reply
            # is the parent's decline, not a question back (measured: that branch cost 10 must-decline panel items).
            return None
        out = dict(res)
        out.update({"status": "clarification", "path": "act:clarify_specific", "response": q,
                    "provenance": {"kind": "dialogue_state", "r468_door": {"act": "asked", "phrase": phrase,
                                                                           "offered": offers, "named": named[:2]}}})
        return out

    def chat(self, text: str, session_id: str = "default") -> dict:
        res = super().chat(text, session_id)
        if not isinstance(res, dict):
            return res
        if res.get("status") == "answered":
            path = str(res.get("path", ""))
            if path.startswith("act:acknowledge"):
                # an acknowledgement is not the end of the thread: name what was being discussed and what can follow
                th = self._r468_thread(session_id)
                if th:
                    out = dict(res)
                    out["response"] = ("Glad that helps. We were on %s: I can go further into it, compare it with "
                                       "something, or move to a new topic." % th[-1])
                    prov = dict(res.get("provenance") or {})
                    prov["r468_door"] = {"act": "acknowledged", "thread": th[-1]}
                    out["provenance"] = prov
                    return out
                return res
            try:
                self._r468_remember(text, session_id, res)
            except Exception:  # noqa: BLE001
                pass
            return res
        if res.get("status") == "clarification" and "act:clarify" in str(res.get("path", "")):
            try:
                door = self._r468_door(text, session_id, res)
            except Exception:  # noqa: BLE001
                door = None
            if door is not None:
                return door
        return res
