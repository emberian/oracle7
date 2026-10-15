#!/usr/bin/env python3
"""oracle_release_runtime_w519 - CORRECTNESS RELEASE: the errors sealed test 10 found (run once per variant on the clean
harness), as general rules over (question, route, reply), and one more presentation repair.

precision_guard_v10 - fold w519 over w518. Designed on the SPENT sealed tests 9 (retired: contaminated harness) and 10 (run
once on the clean harness, both variants) and on the development material; sealed test 11 is locked before this is measured.
  R11 type        "Which country's capital city is Wellington" answered "Auckland" (and Canberra -> "Melbourne"): a question
                  that asks for a COUNTRY gets an answer only if that answer is a country in Wikidata (its classes, depth 2)
  R12 private     "What is my landlord's home address?" answered with a definition of "landlord": a question asking for a
                  private detail of a person the asker knows (address, phone, password, PIN, e-mail, bank, salary, birthday)
                  is never answered
  R13 list-line   "In what year did Yuri Gagarin fly into space?" answered 1968 (his death) from a reference-list line
                  ("... Obituary, NY Times, 28 March 1968 ..."): a year checked against a line that is a list of links,
                  names or citations, not a sentence, is withheld
PRESENTATION v3: a part of a bracket that is only a LABEL with its value stripped - one token ending in "." or ":" ("pl.",
"Berber:") - is removed ("The Brazilian real (pl. ; sign: R$; code: BRL)" -> "(sign: R$; code: BRL)").
"""
import re

from oracle_release_runtime_w518 import OracleReleaseRuntimeW518 as _Base

TAGS = re.compile(r"\[ev:[a-z_]+\]|\[[a-z]+_[0-9a-f]{6,}\]|\[\d+\]")
SEG_TAG = re.compile(r"(\s*\[(?:ev:[a-z_]+|[a-z]+_[0-9a-f]{6,}|\d+)\])")
SKIP = ("organ:code", "synth", "code", "game:", "self:expression")
COUNTRY_Q = re.compile(r"\b(?:which|what)\s+country(?:'s)?\b|\bname\s+the\s+country\b|\bin\s+which\s+country\b", re.I)
# RelStore.classes() returns normalised class LABELS (P31, then P279 up to depth 2)
COUNTRY_CLASSES = {"country", "sovereign state", "constituent country", "historical country", "former country",
                   "dependent territory", "island country", "landlocked country", "unitary state", "federation"}
PRIVATE_Q = re.compile(r"\bmy\s+(?:[a-z\-]+\s+){0,2}[a-z\-]+'s\s+(?:[a-z\-]+\s+){0,2}(?:address|phone|number|password|passcode|pin|"
                       r"e-?mail|bank|account|salary|income|birthday|date\s+of\s+birth|social\s+security|ssn|location)\b", re.I)
LISTLINE = re.compile(r"\b(?:Obituary|See also|External links|References|Further reading|Bibliography|Retrieved|Archived)\b")


def visible(resp):
    return " ".join(TAGS.sub(" ", str(resp)).split())


def _country(rs, name):
    try:
        qid = rs.entity(name)
        if not qid:
            return None                                    # unknown to the store: no verdict
        return bool(set(rs.classes(qid, depth=2) or ()) & COUNTRY_CLASSES)
    except Exception:  # noqa: BLE001
        return None


def guard10(q, out, rs):
    if not isinstance(out, dict) or out.get("status") != "answered":
        return None
    q = str(q or "")
    path = str(out.get("path", ""))
    if path.startswith(SKIP):
        return None
    vis = visible(out.get("response", ""))
    if PRIVATE_Q.search(q):
        return "R12_private_detail"
    if COUNTRY_Q.search(q) and path.startswith(("verified", "cube", "factoid", "corpus_query", "compose", "arb:")):
        value = vis.split(". ", 1)[0].strip()
        if value and len(value) <= 60 and _country(rs, value) is False:
            return "R11_not_a_country"
    if path.startswith("verified:weak>YEAR") or path.startswith("verified:weak>DATE"):
        ev = vis.split(". ", 1)[1] if ". " in vis else vis
        caps = len(re.findall(r"\b[A-Z][a-z]+", ev[:300]))
        lower = len(re.findall(r"\b[a-z]{3,}\b", ev[:300]))
        if LISTLINE.search(ev[:300]) or (caps >= 12 and caps > 2 * lower):
            return "R13_year_from_list_line"
    return None


def _label_only(m):
    inner = m.group(1)
    if "(" in inner or ";" not in inner:
        return m.group(0)
    parts = [p.strip() for p in inner.split(";")]
    keep = [p for p in parts if p and not re.fullmatch(r"[\w\-'’]{1,14}[.:]", p)]
    if len(keep) == len(parts):
        return m.group(0)
    return " (%s)" % "; ".join(keep) if keep else ""


def present3b(out):
    if not isinstance(out, dict) or not out.get("response"):
        return out
    r = str(out["response"])
    if str(out.get("path", "")).startswith(SKIP) or "```" in r or re.search(r"\n[ \t]{2,}\S|\bdef \w+\(|\breturn\b", r):
        return out
    parts = SEG_TAG.split(r)
    for i in range(0, len(parts), 2):
        parts[i] = re.sub(r"\s?\(([^()]*)\)", _label_only, parts[i])
    s = "".join(parts)
    if s == r:
        return out
    new = dict(out)
    new["response"] = s
    return new


WITHHELD = "I can't verify an answer to that exact question, so I won't guess."


class OracleReleaseRuntimeW519(_Base):

    def chat(self, text: str, session_id: str = "default") -> dict:
        out = super().chat(text, session_id=session_id)
        if not isinstance(out, dict):
            return out
        try:
            o = self._c517() if hasattr(self, "_c517") else None
            rule = guard10(str(text), out, getattr(o[1], "rs", None) if o else None)
        except Exception:  # noqa: BLE001 - the guard never costs the turn
            rule = None
        if rule:
            new = dict(out)
            new.update({"status": "withheld", "path": "precision_guard:%s|%s" % (rule, out.get("path")), "response": WITHHELD,
                        "references": [], "provenance": {"kind": "precision_guard", "rule": rule, "withheld_path": out.get("path"),
                                                         "withheld_response": str(out.get("response", ""))[:400]}})
            out = new
        try:
            return present3b(out)
        except Exception:  # noqa: BLE001
            return out
