#!/usr/bin/env python3
"""oracle_release_runtime_w472 - an acknowledgement carries the thread, and is never itself a referent.

CORRECTNESS RELEASE. The gate's held-out corpus has no topic -> acknowledgement -> pointer conversation, so no gate metric
can rise; the first submission (v1) was rejected no_gain with capability unchanged 623 -> 623. What this removes is a
WRONG OUTPUT, measured by ack_anaphora_ab_v1.py (20 scripted conversations, same script on both arms):
  pointer bound to the acknowledgement word ("how old is cool")   w333 15/20  ->  w472 0/20
  acknowledgement reply names the conversation's subject          w333  9/20  ->  w472 18/20
Every remaining w472 reply binds the pointer to the person's subject, or asks which subject was meant.

Measured 2026-09-25 on the serving head (w333) with the status probes:
  "ok thanks" -> path arb:act_acknowledge->act:acknowledge -> "Noted. The session state is kept; ask on." (a status line;
                 w468's thread-carrying acknowledgement only matches paths that START with act:acknowledge)
  "where is the Eiffel Tower" ... "cool" ... "how old is it" -> "I read that as "how old is cool", taking "it" to mean
                 cool." The acknowledgement word became the referent of the next pointer (WordNet gives "cool" a noun
                 sense, so the anaphora folds accepted it). Under w468 the same script answered "137 years".

Rule, a STRICT FALLBACK in w468's style (every other turn is returned unchanged):
  1. ACK: an answered turn whose path names an acknowledgement act (act:acknowledge, arb:act_acknowledge,
     register:acknowledgement) and whose reply carries no thread gets w468's thread-carrying reply.
  2. NOT A REFERENT: the words of acknowledgement turns are remembered per session. If a later reply (answered OR
     withheld - the parent often withholds after mis-binding) says it took a pointer to mean one of them, OR a withheld
     reply restates the person's pointer literally (it was never bound), the turn goes through w468's door with the
     thread's subject (subjects the PERSON named in answered turns; acknowledgement turns are never remembered there).
     Only a door:bound result replaces the parent's reply. Repair a referent, never supply one.

v2 (same day, measured by ack_anaphora_ab_v1.py, 20 scripted topic -> acknowledgement -> pointer conversations):
  v1 cut pointer-bound-to-an-acknowledgement-word from 15/20 (w333) to 7/20. The 7 left had three causes, all fixed here:
  the parent routes the POINTER turn itself ("how old is it") down act:acknowledge, so v1 took it for an acknowledgement
  (now: an acknowledgement is a turn of closed-class acknowledgement words, or an acknowledgement path with no pointer);
  "ok great" entered w468's thread as the subject "great" (acknowledgement-word entries are now removed from the thread);
  and w468's no-answer phrasing "I took "it" to mean X" was not recognised. When w468's door cannot bind, its specific
  question ("Which do you mean by ...") replaces a reply that bound the pointer to an acknowledgement word.
Methods _r472_. Parent: the serving head.
"""

from __future__ import annotations

import re

from oracle_release_runtime_w333 import OracleReleaseRuntimeW333 as _Base

ACK_PATH = re.compile(r"act:acknowledge|act_acknowledge|register:acknowledgement")
TOOK = re.compile(r"""(?:taking|I took) ["“]([^"”]{1,40})["”] to mean ([^.,;:]{1,60})""", re.I)
WORD = re.compile(r"[a-z][a-z'\-]*")
POINTER = re.compile(r"\b(it|its|that|this|they|them|those|these)\b", re.I)
# closed class: a turn made only of these words is an acknowledgement ("got it", "ok thanks", "right", "sounds good")
ACK_LEX = frozenset("ok okay k kk thanks thank thx ty you cool nice great perfect awesome sure right got it alright "
                    "good yes yeah yep gotcha understood fine excellent wonderful sounds makes sense lovely neat "
                    "interesting wow oh ah i see".split())
ACK_CORE = ACK_LEX - {"it", "you", "i", "see", "oh", "ah", "makes", "sounds"}


def _is_ack_text(text):
    w = WORD.findall(text.lower())
    return bool(w) and len(w) <= 5 and "?" not in text and all(x in ACK_LEX for x in w) and any(x in ACK_CORE for x in w)


class OracleReleaseRuntimeW472(_Base):

    def _r472_ackwords(self, sid):
        a = getattr(self, "_r472_acks", None)
        if a is None:
            a = self._r472_acks = {}
        return a.setdefault(sid, set())

    def _r472_thread(self, sid):
        fn = getattr(self, "_r468_thread", None)
        return fn(sid) if fn else []

    def chat(self, text: str, session_id: str = "default") -> dict:
        res = super().chat(text, session_id)
        if not isinstance(res, dict):
            return res
        path = str(res.get("path", ""))
        body = str(res.get("response", ""))
        is_ack = _is_ack_text(text) or (res.get("status") == "answered" and ACK_PATH.search(path)
                                        and not POINTER.search(text) and not TOOK.search(body))
        if is_ack:
            acks = self._r472_ackwords(session_id)
            acks.update(w for w in WORD.findall(text.lower()) if w in ACK_LEX)
            th = self._r472_thread(session_id)
            th[:] = [s for s in th if not set(WORD.findall(s.lower())) <= acks]   # an acknowledgement is never a subject
            if th and th[-1].lower() not in body.lower():
                out = dict(res)
                out["status"] = "answered"
                out["response"] = ("Glad that helps. We were on %s: I can go further into it, compare it with "
                                   "something, or move to a new topic." % th[-1])
                prov = dict(res.get("provenance") or {})
                prov["r472"] = {"act": "acknowledged", "thread": th[-1], "parent_path": path,
                                "parent_status": res.get("status")}
                out["provenance"] = prov
                out["path"] = "r472:acknowledged|" + path
                return out
            return res
        m = TOOK.search(body)
        acks = self._r472_ackwords(session_id)
        door = getattr(self, "_r468_door", None)
        misbound = False
        if m and acks:
            meant = set(WORD.findall(m.group(2).strip().lower()))
            misbound = bool(meant) and meant <= acks
        # a withheld reply that restates the person's pointer literally ("... on how hot is it ...") never bound it
        unbound = res.get("status") == "withheld" and POINTER.search(text) and text.strip().lower().rstrip("?.!") in body.lower()
        if (misbound or unbound) and door is not None and self._r472_thread(session_id):
            try:
                out = door(text, session_id, res)
            except Exception:  # noqa: BLE001
                out = None
            p = str(out.get("path", "")) if isinstance(out, dict) else ""
            if p.startswith("door:bound") or (misbound and p.startswith("act:clarify_specific")):
                out = dict(out)
                prov = dict(out.get("provenance") or {})
                prov["r472"] = {"act": "rebound" if misbound else "bound", "parent_path": path}
                out["provenance"] = prov
                out["path"] = "r472:" + p
                return out
        return res
