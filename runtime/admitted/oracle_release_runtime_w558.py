#!/usr/bin/env python3
"""oracle_release_runtime_w558 - ORACLE7 4.0, PRONOUN RE-ENTRY (Ben 2026-10-19: "add pronouns to 4.0"). A CORRECTNESS RELEASE
in the sense the gate uses: it may not lower any column; its effect is measured on the second sealed V4 panel's follow-ups.

4.0's law (w557, I1): a past answer does not become state; a later turn may use it only by RE-ENTERING it as cited evidence.
3.2 already resolves many pronoun follow-ups ("When was she born?" after "Who wrote Emma?" -> 16 December 1775). Where it
cannot - the resolved question does not parse ("What is its capital?" after "Which country is Kyoto in?" was withheld as
subject-missing; "What else did he direct?" after "Who directed Vertigo?" asked to clarify) - this fold re-enters the
previous answer itself: the pronoun is replaced by that answer and the question is asked once more ("What is Japan's
capital?"). Conditions, all required:
  - the session's previous answer stood on something (a citation, a proof, a checked route: w557's stands_on_something)
    and named one thing: a person after a "who" question (he/she/him/her/his), a place or thing after a "which/what
    <country|city|...>" question (it/its);
  - the new turn was NOT answered by the chain, is short (<= 14 words), names nothing of its own (no capitalised word after
    the first) and carries a pronoun of the right kind;
  - the re-entered question is answered; otherwise the chain's own reply stands.
The reply says what was re-entered ("taking 'its' as Japan, from my previous answer"). The ledger keeps one entry per turn:
this fold repeats w557's bookkeeping around its own turn instead of calling w557's chat twice."""
from __future__ import annotations

import re
import time

from oracle_release_runtime_w557 import OracleReleaseRuntimeW557 as _Base
from oracle_release_runtime_w557 import ledger_append, ledger_entry, stands_on_something, recall_organs

PERSON_Q = re.compile(r"^\s*who\b", re.I)
THING_Q = re.compile(r"^\s*(?:which|what)\s+(country|city|town|state|province|island|planet|moon|river|mountain|lake|sea|ocean|"
                     r"continent|region|book|novel|film|movie|play|opera|painting|team|club|company|band|album|song)\b", re.I)
PERSON_P = re.compile(r"\b(he|she|him|her|his|hers)\b", re.I)
THING_P = re.compile(r"\b(it|its)\b", re.I)
TAG = re.compile(r"^\s*(?:\[[^\]]+\]\s*)+")
NOT_POSS = {"in", "on", "at", "to", "for", "with", "from", "by", "and", "or", "about", "as", "of", "?"}


def answer_entity(reply):
    """the one thing a reply names first: 'Jane Austen' from 'Jane Austen. From the Wikidata relation store: ...'"""
    head = TAG.sub("", str(reply or "")).split(". ", 1)[0].strip().rstrip(".")
    words = head.split()
    if not words or len(words) > 6 or re.search(r"\d", head) or not words[0][:1].isupper():
        return None
    return head


def substitute(text, entity, kind):
    rx = PERSON_P if kind == "person" else THING_P
    toks = re.split(r"(\W+)", text)
    out, used = [], False
    for i, t in enumerate(toks):
        low = t.lower()
        if rx.fullmatch(t or "") and low:
            nxt = next((x for x in toks[i + 1:] if x.strip()), "?").lower()
            poss = low in ("his", "its", "hers") or (low == "her" and nxt not in NOT_POSS and nxt.isalpha())
            out.append(entity + ("'s" if poss else ""))
            used = True
        else:
            out.append(t)
    return "".join(out) if used else None


class OracleReleaseRuntimeW558(_Base):
    def _v4_turn(self, text, session_id):
        """the chain's reply, or - where it could not resolve a pronoun - the previous cited answer re-entered"""
        r = super(_Base, self).chat(text, session_id)      # the chain below w557 (w556 and down), as w557 itself calls it
        disc = getattr(self, "_v4_disc", None)
        if disc is None:
            disc = self._v4_disc = {}
        q = str(text or "")
        if isinstance(r, dict) and r.get("status") == "answered":
            rec0 = disc.get(session_id)
            kind = "person" if PERSON_Q.search(q) else ("thing" if THING_Q.search(q) else None)
            if kind and stands_on_something(r):
                ent = answer_entity(r.get("response"))
                disc[session_id] = {"entity": ent, "kind": kind} if ent else None
            elif not (rec0 and (PERSON_P if rec0["kind"] == "person" else THING_P).search(q)):
                disc[session_id] = None                 # a new subject: the old answer is no longer what a pronoun means
            return r                                    # (a follow-up the chain resolved itself keeps the record)
        rec = disc.get(session_id)
        words = q.split()
        if (not rec or len(words) > 14 or any(w[:1].isupper() for w in words[1:])
                or not (PERSON_P if rec["kind"] == "person" else THING_P).search(q)):
            return r
        q2 = substitute(q, rec["entity"], rec["kind"])
        if not q2:
            return r
        r2 = super(_Base, self).chat(q2, session_id)
        if not (isinstance(r2, dict) and r2.get("status") == "answered"):
            return r
        pron = ((PERSON_P if rec["kind"] == "person" else THING_P).search(q).group(0))
        out = dict(r2)
        out["path"] = "reentry:cited>" + str(r2.get("path", ""))
        out["response"] = "(Taking '%s' as %s, from my previous answer.) %s" % (pron, rec["entity"], r2.get("response", ""))
        out["reentry"] = {"pronoun": pron, "entity": rec["entity"], "question": q2}
        return out

    def chat(self, text: str, session_id: str = "default") -> dict:
        # w557's bookkeeping (snapshot, non-identity, recall counts, the ledger entry) around this fold's turn - once per turn
        hits0 = sum(rc.hits for rc in self._v4_recall())
        try:
            snap = self._v4_snapshot(session_id)
        except Exception:  # noqa: BLE001
            snap = None
        t0 = time.perf_counter()
        r = self._v4_turn(text, session_id)
        L = round(1000.0 * (time.perf_counter() - t0), 1)
        extra = {}
        try:
            if (isinstance(r, dict) and r.get("status") == "answered" and snap is not None
                    and not str(r.get("path", "")).startswith("act:") and not stands_on_something(r)):
                self._v4_restore(session_id, snap)
                extra["discourse_record"] = True
            if isinstance(r, dict) and r.get("reentry"):
                extra["reentry"] = r["reentry"]["entity"]
            hits = sum(rc.hits for rc in self._v4_recall())
            if hits > hits0:
                extra["recalled_walks"] = hits - hits0
            self._v4_n = getattr(self, "_v4_n", 0) + 1
            import os as _os
            if _os.environ.get("ORACLE7_V4_RECALL") != "0" and (self._v4_n in self.SCAN_AT or self._v4_n % 233 == 0):
                recall_organs()
            ledger_append(ledger_entry(text, session_id, r, L, self.LAW, extra))
        except Exception:  # noqa: BLE001
            pass
        return r
