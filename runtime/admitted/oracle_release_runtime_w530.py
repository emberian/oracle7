#!/usr/bin/env python3
"""oracle_release_runtime_w530 - CAPABILITY RELEASE, THREE DISCLOSED PARTS (w528 was REJECTED twice for its size, not its
direction: 2026-10-09 novelty noise; 2026-10-11 capability 1257 -> 1258, a gain of one item does not exceed the resolution -
so its two parts ride with the film / television relations):
  (3) FILM AND TELEVISION RELATIONS - rel-films-v2 (held-out 52/84, 0 wrong; head 10, 6 wrong) and rel-tvseries-v2 (held-out
      52/72, 1 wrong; head 3, 6 wrong), both ADMITTED 2026-10-11 by spec_gate_v4 (pronoun guard; fresh unambiguous panels),
      core panel unchanged. PINNED: /opt/oracle-clm/specialists/_gate/standing_new_v4.txt (never edited after this fold is
      measured). Called on a turn the whole chain declined, or over a WEAK core reading when its verified answer differs
      (the w528 precedence rule), on the standalone question when the conversation layer resolved the turn.
The w528 description follows unchanged.

oracle_release_runtime_w528 - TWO DISCLOSED PARTS:
  (1) GRAVITY ON OTHER WORLDS - specialist bodies-v2 (ADMITTED 2026-10-09) - the panel gain;
  (2) VERIFIED RELATION ANSWERS TAKE PRECEDENCE OVER WEAK CORE READINGS - measured on TRAINING pools; neutral on the panel.

(1) bodies-v2 reads a named Solar System body in any form ("on Mars", "Titan's surface", "above Venus") and computes weight,
fall time, impact speed and pendulum period from NASA surface gravity; a body-named gravity turn it cannot read fully is
declined in-domain. Its gate (spec_gate_v4, FRESH panel after v1's held-out was spent NEGATIVE): held-out 38/38, 0 wrong; the
head 2/38 with 9 CONFIDENT WRONG answers - the chain computed with Earth's g on Io, Titan and Jupiter (physics-r2 reads the
amounts, not the world). Core panel 144 -> 145, false yes 0 -> 0. The gate measured the specialist FIRST on every turn it
replies to; this fold uses a SUBSET of that, the safer one:
  ANSWER   bodies-v2's verified computation is given first - on the turn as asked, or on the standalone question a
           conversation layer read it as (provenance chat_resolved.read_as, when such a layer is in the chain)
  DECLINE  its in-domain decline replaces the chain's reply ONLY when the chain answered through a physics path (a number
           computed with Earth's gravity for a named other world); otherwise the chain's own reply stands (a history
           question that mentions the Moon is not a gravity question)
  PINNED: /opt/oracle-clm/specialists/_gate/standing_new_v3.txt (= bodies-v2; never edited after this fold is measured).

(2) Found through the conversation tests: "When was J. R. R. Tolkien born?" was answered 1620 (a passage about the Tolkien
family, path verified:cube) while the admitted relation family holds the receipt "J. R. R. Tolkien (Q892) - date of birth
(P569) - 3 January 1892". The family is called only on turns the chain DECLINES (w526), so a weak core answer silenced a
verified one. MEASURED FIRST, on TRAINING pools only (prec_measure_v1.py: TriviaQA train cache + Mintaka train +
WebQuestions train - never the capability panel; 400 questions the relation readers recognise and the family answers, head
w526): 377 agree. On the core's WEAK readings (compose:bridge, cube:read, verified:cube, verified:weak, corpus_query,
deliberation, factoid:page, organ:converse) where the two disagree: family right / core wrong 9 (Elvis born 1935 not 1962;
Principia by Isaac Newton not Samuel Pepys; the Missouri ends in the Mississippi; Valletta is the capital of Malta; ...),
core right / family wrong 1 (Dickens: "Landport" - itself the Portsmouth district Wikidata records). On the core's own
RELATION ORGAN the record is mixed (2 / 1, one a real family miss: "The Snowman" read as Jo Nesbo's novel) - NOT overruled.
Panel precheck of (2) alone (2026-10-09, head w526 + names_v2): gains none, worse none, false yes 11 -> 11, m52 0 route
changes, regcheck 0 - the panel holds no item of this kind, so (2) rides with (1) and is disclosed as such.
  RULE: on a turn the chain ANSWERED through one of the weak readings, if the question (or the standalone question a
  conversation layer read it as) is one the hand-written relation readers recognise, the pinned family is asked; a verified
  answer (receipt; not a decline, not a disagreement between domains) whose stated answer differs from the core's replaces
  it, and the core's reading is kept in the provenance.
  PINNED: /opt/oracle-clm/specialists/_gate/standing_new_v2.txt - the SAME list w526 pinned (never edited).
The fold never imports a runtime other than its parent; it touches no other module's state."""
from __future__ import annotations

import importlib.util
import re
import threading

from oracle_release_runtime_w403 import OracleReleaseRuntimeW403 as _Base

try:
    import chat_context_v1 as _CC
except Exception:  # noqa: BLE001 - without the readers part (2) is off; part (1) stands
    _CC = None

SPEC_ROOT = __import__("os").environ.get("ORACLE7_ROOT", "/opt/oracle-clm") + "/specialists"
GATE = SPEC_ROOT + "/_gate"
FAMILY_CODE = GATE + "/combo_runtime_v1.py"
REL_STANDING = GATE + "/standing_new_v2.txt"
BODIES_STANDING = GATE + "/standing_new_v3.txt"
WEAK = ("compose:", "cube:", "verified:cube", "verified:weak", "corpus_query:", "deliberation:", "factoid:", "organ:converse")
_SPLIT = re.compile(r"(?<![\s.][A-Z]\.)(?<!^[A-Z]\.)(?<=[.!?])\s")
_S: dict = {}
_LOCK = threading.Lock()


def _c528_family(key, standing):
    with _LOCK:
        if key not in _S:
            spec = importlib.util.spec_from_file_location("o7_combo_runtime_v1_w528_%s" % key, FAMILY_CODE)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            ids = open(standing, encoding="utf-8").read().split()
            _S[key] = mod.Family(["%s/%s/manifest.json" % (SPEC_ROOT, i) for i in ids], ["%s/%s" % (SPEC_ROOT, i) for i in ids])
        return _S[key]


def _c528_lead(text):
    t = re.sub(r"^\s*\[ev:[a-z_]+\]\s*", "", str(text or ""))
    return _SPLIT.split(t, 1)[0].strip().rstrip(".").lower()


def _c528_bodies(text, session_id):
    if not text:
        return None
    try:
        r = _c528_family("bodies", BODIES_STANDING).reply(text, "core:%s" % session_id)
    except Exception:  # noqa: BLE001 - a family failure never costs the chain's own reply
        return None
    if not r or r.get("status") == "disagree" or (r.get("provenance") or {}).get("per_part"):
        return None
    return r


def _c528_wrap(r, base, prefix, declined, family):
    prov = r.get("provenance") or {}
    new = dict(base) if isinstance(base, dict) else {}
    new.update({"status": "withheld" if declined else "answered", "path": prefix + "specialist_call>" + str(r.get("path")),
                "response": "%s [%s]" % (r["response"], prov.get("specialist")), "references": [],
                "provenance": {"kind": "core_called_specialist", "family": family, "specialist": prov.get("specialist"),
                               "core_status": (base or {}).get("status"), "core_path": (base or {}).get("path")}})
    return new


class _C528Parts(_Base):
    # private helper: its name must NOT start with OracleReleaseRuntime - the gate's loader takes the first such class in
    # alphabetical order, and measured this helper (the head's own chat) instead of W530 twice (2026-10-12)
    def _c528_chat(self, text, session_id):
        # (1) bodies-v2: a verified computation first
        r = _c528_bodies(text, session_id)
        if r and not (r.get("provenance") or {}).get("declined"):
            return _c528_wrap(r, None, "", False, "new_v3")
        out = self._c528_precedence(text, session_id)
        if not isinstance(out, dict):
            return out
        path = str(out.get("path", ""))
        if path.startswith("chat:resolved>"):
            read_as = ((out.get("provenance") or {}).get("chat_resolved") or {}).get("read_as")
            r2 = _c528_bodies(read_as, session_id)
            if r2 and not (r2.get("provenance") or {}).get("declined"):
                new = _c528_wrap(r2, out, "chat:resolved>", False, "new_v3")
                new["provenance"]["chat_resolved"] = (out.get("provenance") or {}).get("chat_resolved")
                return new
            r = r or r2
            path = path[len("chat:resolved>"):]
        # (1) its in-domain decline only over an Earth-gravity computation for a named world
        if r and out.get("status") == "answered" and "physics" in path:
            return _c528_wrap(r, out, "", True, "new_v3")
        return out

    def _c528_precedence(self, text, session_id):
        out = super().chat(text, session_id=session_id)
        if _CC is None or not isinstance(out, dict) or out.get("status") != "answered":
            return out
        path = str(out.get("path", ""))
        resolved = path.startswith("chat:resolved>")
        core_path = path[len("chat:resolved>"):] if resolved else path
        if not core_path.startswith(WEAK):
            return out
        prov = out.get("provenance") or {}
        q = ((prov.get("chat_resolved") or {}).get("read_as") if resolved else None) or text
        try:
            if not _CC.recognised(q):
                return out
            r = _c528_family("rel", REL_STANDING).reply(q, "core:%s" % session_id)
        except Exception:  # noqa: BLE001 - a family failure never costs the chain's own reply
            return out
        rp = (r or {}).get("provenance") or {}
        if not r or r.get("status") != "answered" or rp.get("declined") or rp.get("per_part") or not rp.get("specialist"):
            return out
        if _c528_lead(r.get("response")) == _c528_lead(out.get("response")):
            return out
        new = dict(out)
        new.update({"path": ("chat:resolved>" if resolved else "") + "specialist_precedence>" + str(r.get("path")),
                    "response": "%s [%s]" % (r["response"], rp.get("specialist")), "references": [],
                    "provenance": {"kind": "specialist_precedence", "family": "new_v2", "specialist": rp.get("specialist"),
                                   "core_path": core_path, "core_lead": _c528_lead(out.get("response"))[:200],
                                   "chat_resolved": prov.get("chat_resolved")}})
        return new


FILMTV_STANDING = GATE + "/standing_new_v4.txt"
DELIBERATE = ("does_not_follow", "out_of_fragment", "validity")


def _c530_ask(q, session_id):
    try:
        r = _c528_family("filmtv", FILMTV_STANDING).reply(q, "core:%s" % session_id)
    except Exception:  # noqa: BLE001 - a family failure never costs the chain's own reply
        return None
    if not r or r.get("status") == "disagree" or (r.get("provenance") or {}).get("per_part"):
        return None
    if not (r.get("provenance") or {}).get("specialist"):
        return None
    return r


class OracleReleaseRuntimeW530(_C528Parts):
    def chat(self, text: str, session_id: str = "default") -> dict:
        # (1) + (2): bodies-v2 and verified-relation precedence (w528's measured parts)
        out = self._c528_chat(text, session_id)
        if not isinstance(out, dict):
            return out
        # (3) film / television relations: on a chain decline, or over a weak reading of a question the family reads
        st, path = str(out.get("status", "")), str(out.get("path", ""))
        resolved = path.startswith("chat:resolved>")
        core_path = path[len("chat:resolved>"):] if resolved else path
        prov = out.get("provenance") or {}
        q = ((prov.get("chat_resolved") or {}).get("read_as") if resolved else None) or text
        declined = st in ("withheld", "clarification") and not core_path.endswith(DELIBERATE)
        weak = st == "answered" and core_path.startswith(WEAK)
        if not (declined or weak):
            return out
        r = _c530_ask(q, session_id)
        if not r:
            return out
        rp = r.get("provenance") or {}
        is_decline = bool(rp.get("declined")) or r.get("status") != "answered"
        if weak and (is_decline or _c528_lead(r.get("response")) == _c528_lead(out.get("response"))):
            return out                                   # precedence only for a verified answer that differs
        new = dict(out)
        new.update({"status": "withheld" if is_decline else "answered",
                    "path": ("chat:resolved>" if resolved else "") + ("specialist_precedence>" if weak else "specialist_call>") + str(r.get("path")),
                    "response": "%s [%s]" % (r["response"], rp.get("specialist")), "references": [],
                    "provenance": {"kind": "specialist_precedence" if weak else "core_called_specialist", "family": "new_v4",
                                   "specialist": rp.get("specialist"), "core_status": st, "core_path": core_path,
                                   "chat_resolved": prov.get("chat_resolved")}})
        return new
