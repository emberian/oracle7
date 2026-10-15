#!/usr/bin/env python3
"""oracle_release_runtime_w538 - CORRECTNESS RELEASE: three conversation defects found by the sealed dialogue tests (2026-10-13,
listed in the release card's Limits) and reproduced on fresh dev examples (never the spent items):

  1. WEIGHT IN NEWTONS. "What does that weigh in newtons?" after a mass answer was rewritten to "What does 5 litres of sea
     water in kg weigh in newtons?" and the densities specialist answered the MASS again; "What is the weight of 2 kg in
     newtons?" was not handled at all. RULE: a question that asks for a weight in newtons gets W = m * g (standard gravity
     9.80665 m/s^2) when one mass is known exactly - a mass given in the question, else the mass the chain's own answer
     states, else the conversation's last result in kilograms. Another planet or moon named without a gravity, or a
     negative mass, is not computed (the turn is left to the chain).
  2. SAME NAME, DIFFERENT THING. After "Which planet does the moon Titania orbit?", "Who discovered Titania?" was answered for
     the ASTEROID 593 Titania. RULE: when a specialist's receipt names an entity whose name (catalogue numbers and
     disambiguating brackets aside) equals the entity the conversation is about but whose id differs, the same property is read for the conversation's own entity from the
     relation store; one value -> that answer with its receipt; several -> withheld (never about the wrong one); none (the
     conversation's entity does not have that property - a novel has no director) -> the specialist's answer stands.
  3. A SUPPORTING SENTENCE WITH A HOLE. "Santiago. The center of Chile ... has a Mediterranean climate with an average
     temperature of in January and in July." - numbers stripped from the quoted sentence. RULE (short knowledge answers from the
     knowledge routes only; never code, essays, composed programs, games or conversation acts): after the answer sentence, a
     quoted sentence with a hole (a preposition followed directly by another, or by punctuation, where a value was lost;
     empty brackets) is dropped; the answer and its source stay.
None of the three invents an answer: (1) computes from a stated mass, (2) reads the store for the entity already in play,
(3) only removes text. The fold imports no runtime other than its parent; the conversation engine is read through its own
state() and updated through update()."""
from __future__ import annotations

import re

from oracle_release_runtime_w409 import OracleReleaseRuntimeW409 as _Base

try:
    import chat_context_v2 as _CC
    import relation_spec_v1 as _RV
except Exception:  # noqa: BLE001
    _CC = _RV = None

G0 = 9.80665
ASKS_NEWTONS = re.compile(r"\b(?:weigh\w*|weight)\b[^?]*\bin\s+(?:newtons?|N)\b|\bhow\s+many\s+newtons\b", re.I)
OTHER_BODY = re.compile(r"\b(?:on|at)\s+(?:the\s+)?(?:moon|mars|venus|jupiter|saturn|mercury|neptune|uranus|pluto|titan|"
                        r"europa|ganymede|io|callisto|planet|asteroid)\b|\bearth\s+masses\b", re.I)
MASS_IN_Q = re.compile(r"(?<![\w.-])(\d+(?:\.\d+)?)\s*(kg|kilograms?|g|grams?|tonnes?|t)\b", re.I)
MASS_IN_A = re.compile(r"\bmass is (?:about |approximately )?(-?\d+(?:\.\d+)?)\s*(kg|g|tonnes?)\b", re.I)
TO_KG = {"kg": 1.0, "kilogram": 1.0, "kilograms": 1.0, "g": 1e-3, "gram": 1e-3, "grams": 1e-3, "tonne": 1e3, "tonnes": 1e3, "t": 1e3}
FWD = re.compile(r"From the Wikidata relation store: (.+?) \(Q(\d+)\) - ([^()]*?) \(P(\d+)\) - ")
HOLE = re.compile(r"\b(?:of|between|from|about|around|approximately|roughly|averaging|reaching|measuring|to)\s+(?:in|and|to|or|with)\s+"
                  r"(?:January|February|March|April|May|June|July|August|September|October|November|December|the|a)\b|"
                  r"\b(?:of|between|from|about|around|approximately|averaging|reaching|measuring)\s*[,.;)]|\(\s*\)|\[\s*\]|"
                  r"\bbetween\s+and\b|\bfrom\s+to\b|\bof\s+in\b|\bof\s+and\b", re.I)


KNOWLEDGE_ROUTES = ("organ:relation", "cube:read", "verified:", "factoid:", "deliberation:", "capability:when_did", "exact_router",
                    "corpus_query:", "compose:bridge")


def core_name(label):
    """'593 Titania' / 'Titania (moon)' / 'Titania' -> 'titania': catalogue numbers and disambiguating brackets are not the name"""
    t = re.sub(r"^\(?\d+\)?\s+", "", str(label or "").strip())
    return re.sub(r"\s*\([^)]*\)\s*$", "", t).strip().lower()


def _fmt(x):
    return ("%.4g" % x) if abs(x) < 1e4 else "{:,.0f}".format(x)


def mass_known(q, chain_reply, session_id):
    m = MASS_IN_Q.findall(q)
    if len(m) == 1:
        return float(m[0][0]) * TO_KG[m[0][1].lower()], "given"
    a = MASS_IN_A.search(chain_reply or "")
    if a:
        return float(a.group(1)) * TO_KG[a.group(2).lower()], "computed"
    if _CC is not None:
        try:
            r = _CC.state(session_id).result
            if r and str(r[1]).lower() == "kg":
                return float(r[0]), "earlier"
        except Exception:  # noqa: BLE001
            pass
    return None, None


def without_holes(response):
    t = str(response or "")
    lead = re.match(r"^\s*(\[ev:[a-z_]+\]\s*)?(.+?[.!?])(\s|$)", t)
    if not lead or "From the Wikidata relation store" in t:
        return None
    head = t[:lead.end(2)]
    rest = t[lead.end(2):]
    tail = ""
    mt = re.search(r"(\s*\[[^\]]+\]\s*(?:\(typed relations:[^)]*\))?\s*)$", rest)
    if mt:
        tail, rest = mt.group(1), rest[:mt.start(1)]
    sents = re.split(r"(?<=[.!?])\s+(?=[A-Z])", rest.strip())
    keep = [s for s in sents if s and not HOLE.search(s)]
    if len(keep) == len([s for s in sents if s]):
        return None
    return (head + (" " + " ".join(keep) if keep else "") + (" " + tail.strip() if tail.strip() else "")).strip()


class OracleReleaseRuntimeW538(_Base):
    def chat(self, text: str, session_id: str = "default") -> dict:
        q0 = str(text or "")
        prev = None
        if _CC is not None:
            try:
                st = _CC.state(session_id)
                prev = [e for e in (st.subj, st.topic, st.ans) if e]
            except Exception:  # noqa: BLE001
                prev = None
        out = super().chat(q0, session_id=session_id)
        if not isinstance(out, dict):
            return out
        q = ((out.get("provenance") or {}).get("chat_resolved") or {}).get("read_as") or q0
        # 1. WEIGHT IN NEWTONS
        if ASKS_NEWTONS.search(q0) and not OTHER_BODY.search(q0) and not OTHER_BODY.search(q):
            m, src = mass_known(q0, str(out.get("response", "")) if out.get("status") == "answered" else "", session_id)
            if m is None and q != q0:
                m, src = mass_known(q, str(out.get("response", "")) if out.get("status") == "answered" else "", session_id)
            if m is not None and m > 0:
                w = m * G0
                new = dict(out)
                new.update({"status": "answered", "path": "weight:m_g>%s" % src,
                            "response": "The weight is about %s N (W = m·g = %s kg × 9.80665 m/s², standard Earth gravity)." % (_fmt(w), _fmt(m)),
                            "references": [], "provenance": {"kind": "weight_m_g", "mass_kg": m, "mass_source": src,
                                                             "chain_path": out.get("path"), "chain_response": str(out.get("response", ""))[:300]}})
                if _CC is not None:
                    try:
                        _CC.update(session_id, q, new)
                    except Exception:  # noqa: BLE001
                        pass
                return new
        if out.get("status") != "answered":
            return out
        resp = str(out.get("response", ""))
        # 2. SAME NAME, DIFFERENT THING
        m = FWD.search(resp)
        if m and prev and _RV is not None:
            label, qid, prop = m.group(1).strip(), int(m.group(2)), int(m.group(4))
            same = [e for e in prev if e and core_name(e[1]) == core_name(label) and int(e[0]) != qid]
            if same:
                mine, mine_label = int(same[0][0]), str(same[0][1])
                try:
                    rs = _RV._rs()
                    objs = [o for (o,) in rs.db.execute("SELECT o FROM fact WHERE s=? AND p=?", (mine, prop)).fetchall() if o]
                    vals = sorted(_RV.values(mine, prop))
                except Exception:  # noqa: BLE001
                    objs, vals = [], []
                # the conversation's own entity does not HAVE this property (a novel has no director): the specialist reading
                # the same-name entity that does (the film) is the plausible reading - its answer stands (panel 2026-10-13)
                if not vals:
                    return out
                new = dict(out)
                if len(vals) == 1:
                    plab = m.group(3).strip()
                    shown = "%s (Q%d)" % (vals[0], objs[0]) if len(objs) == 1 and (rs.label(objs[0]) or "") == vals[0] else vals[0]
                    new.update({"response": "%s. From the Wikidata relation store: %s (Q%d) - %s (P%d) - %s." % (vals[0], mine_label, mine, plab, prop, shown),
                                "path": "same_name_guard>%s" % out.get("path"), "references": [],
                                "provenance": {"kind": "same_name_guard", "conversation_entity": mine, "replaced_entity": qid,
                                               "replaced_response": resp[:300]}})
                else:
                    new.update({"status": "withheld", "path": "same_name_guard:withheld|%s" % out.get("path"),
                                "response": "I found that for a different %s than the one we were talking about, and I can't verify it for "
                                            "this one, so I won't guess." % label, "references": [],
                                "provenance": {"kind": "same_name_guard", "conversation_entity": mine, "replaced_entity": qid,
                                               "withheld_response": resp[:300]}})
                if _CC is not None:
                    try:
                        _CC.update(session_id, q, new)
                    except Exception:  # noqa: BLE001
                        pass
                return new
        # 3. A SUPPORTING SENTENCE WITH A HOLE - only on short knowledge answers from the knowledge routes: code, essays,
        # composed programs, games and conversation acts carry brackets and fragments by design (panel 2026-10-13)
        route = re.sub(r"^(?:chat:resolved>|family_precedence>|path_memory>)+", "", str(out.get("path", "")))
        if not route.startswith(KNOWLEDGE_ROUTES) or len(resp) > 700 or "\n" in resp or "```" in resp:
            return out
        fixed = without_holes(resp)
        if fixed:
            new = dict(out)
            new["response"] = fixed
            prov = dict(out.get("provenance") or {})
            prov["dropped_broken_sentence"] = True
            new["provenance"] = prov
            return new
        return out
