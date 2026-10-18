"""readback - rewriting a record's sentence, kept only when reading it back gives the same meaning ("read-back writing").

ProseFold's essays use the record's own sentences, arranged; no word changes. This module lets a sentence be reworded, under
one rule: a rewrite is READ BACK into a meaning signature, and it is kept only when that signature is identical to the record
sentence's. Nothing is generated freely; every change is a proposal the check can refuse.

  proposals    synonym: one content word replaced by another lemma of its MOST COMMON WordNet sense, only when that is the
               replacement's most common sense too (symmetric first sense), that sense clearly dominant for both, the
               replacement a common word in that sense (at least half as frequent as the original), uninflected forms only
               fronting: a closing TIME phrase only ("... in 1990.", "... during the 18th century.") moved to the front;
               other closing phrases can belong to a noun ("words in unusual senses") and moving them changes the meaning
               and their combination. Every edit replaces exact characters of the record sentence; the rest is kept byte
               for byte (accents, quotes, brackets).
  read back    the signature of a sentence: every content word as its most common WordNet sense (or itself, if WordNet does
               not know it), every number, every name (capitalised word not opening the sentence), every negation,
               quantifier and modal - as a multiset. Function words and order are not meaning here; roles are kept
               because the only moves are a same-sense swap and moving a whole phrase.
  kept         signature(rewrite) == signature(record) and every swapped pair is symmetric-first-sense.
The check is tested on fakes (planted_fakes): a changed number, a swapped name, an inserted "not", a word replaced by its
more general WordNet parent, a word replaced by an unrelated one. Each must be refused.

WordNet: the release's own store (m13a_wordnet_build_a_v4/wordnet_specialist.sqlite3). Without it, no rewrite is proposed and
the essay is the record's sentences, as before. No language model; no network."""
from __future__ import annotations

import os
import re
import sqlite3
from functools import lru_cache
from pathlib import Path

WORD = re.compile(r"[^\W\d_][\w'-]*|\d[\d,]*(?:\.\d+)?|[^\s\w]")
NUM = re.compile(r"^\d[\d,]*(?:\.\d+)?$")
KEEP = {"not", "no", "never", "none", "nor", "neither", "nothing", "nobody", "nowhere", "without", "cannot", "n't",
        "all", "every", "each", "some", "most", "many", "few", "several", "any", "only", "always", "sometimes", "often",
        "rarely", "usually", "can", "could", "may", "might", "must", "should", "would", "will", "shall"}
FUNCTION = {"a", "an", "the", "of", "in", "on", "at", "to", "for", "from", "by", "with", "as", "and", "or", "but", "is", "are",
            "was", "were", "be", "been", "being", "it", "its", "this", "that", "these", "those", "which", "who", "whom", "whose",
            "there", "their", "they", "he", "she", "his", "her", "him", "them", "we", "our", "you", "your", "i", "has", "have",
            "had", "do", "does", "did", "than", "then", "so", "such", "into", "onto", "over", "under", "about", "after",
            "before", "during", "since", "until", "between", "among", "through", "also", "very", "more", "less", "other"}
MONTH = r"(?:January|February|March|April|May|June|July|August|September|October|November|December)"
TIME = (r"(?:in|during|since|after|before|until|by)\s+(?:the\s+)?(?:(?:early|late|mid)[- ])?(?:\d{3,4}s?|\d{1,2}(?:st|nd|rd|th)\s+century|"
        + MONTH + r"(?:\s+\d{1,2},)?\s+\d{4})")
TAIL = re.compile(r"^(?P<body>[A-Z][^,;:()\"\[\]]+?)\s+(?P<pp>" + TIME + r")\s*\.$")
OPENERS_LOWER = {"The", "A", "An", "It", "Its", "This", "These", "Those", "There", "They", "He", "She", "We", "You", "Many", "Most",
                 "Some", "Several", "Each", "Every", "All", "Both"}


def _wordnet_path():
    here = Path(__file__).resolve().parents
    root = os.environ.get("ORACLE7_ROOT") or (str(here[2] / "root") if len(here) > 2 else "")   # release: workbench/prosefold/ -> root/
    for c in (Path(root) / "fable-content/oracle-m-series-2026-08-15/m13a_wordnet_build_a_v4/wordnet_specialist.sqlite3",
              Path("/opt/oracle-clm/fable-content/oracle-m-series-2026-08-15/m13a_wordnet_build_a_v4/wordnet_specialist.sqlite3"),
              Path("/opt/oracle7/release/root/fable-content/oracle-m-series-2026-08-15/m13a_wordnet_build_a_v4/wordnet_specialist.sqlite3")):
        if c.is_file():
            return str(c)
    return None


_DB = {}


def _db():
    if "c" not in _DB:
        p = _wordnet_path()
        _DB["c"] = sqlite3.connect("file:%s?mode=ro&immutable=1" % p, uri=True, check_same_thread=False) if p else None
    return _DB["c"]


def available():
    return _db() is not None


@lru_cache(maxsize=200000)
def senses(word):
    """[(synset_id, tag_count)] for a word form, most common first (ties: synset id, for a stable order)"""
    c = _db()
    if c is None:
        return ()
    rows = c.execute("SELECT synset_id, MAX(tag_count) FROM alias WHERE normalized_alias=? GROUP BY synset_id", (word.lower(),)).fetchall()
    return tuple(sorted(rows, key=lambda r: (-(r[1] or 0), r[0])))


def first_sense(word):
    s = senses(word)
    return s[0][0] if s and (s[0][1] or 0) > 0 else None


def count_in(word, synset):
    for sid, n in senses(word):
        if sid == synset:
            return n or 0
    return 0


@lru_cache(maxsize=100000)
def lemmas(synset):
    c = _db()
    if c is None:
        return ()
    return tuple(r[0] for r in c.execute("SELECT DISTINCT normalized_alias FROM alias WHERE synset_id=? AND tag_count>0", (synset,)).fetchall())


@lru_cache(maxsize=100000)
def parent(synset):
    c = _db()
    if c is None:
        return None
    r = c.execute("SELECT object_id FROM relation WHERE subject_id=? AND predicate='subclass_of' LIMIT 1", (synset,)).fetchone()
    return r[0] if r else None


def tokens(s):
    return WORD.findall(str(s or ""))


def signature(s):
    """the meaning a sentence is read back into (a sorted multiset)"""
    out = []
    toks = tokens(s)
    for i, t in enumerate(toks):
        lw = t.lower()
        if NUM.match(t):
            out.append("#" + t.replace(",", ""))
        elif not t[:1].isalpha():
            continue
        elif lw in KEEP:
            out.append("!" + lw)
        elif lw in FUNCTION:
            continue
        elif t[:1].isupper() and i > 0 and lw not in FUNCTION:
            out.append("@" + t)                               # a name (not the sentence's first word)
        else:
            out.append("~" + (first_sense(lw) or lw))
    return tuple(sorted(out))


INFLECTED = re.compile(r"(?:ed|ing|er|est|s)$")
# found on the development sample (2026-10-18, 400 Simple Wikipedia sentences, seed 7): a WordNet first sense that is not the
# sense in use ("the chance of dirt" = probability, not opportunity), a word with two common meanings ("presently" = soon or
# now), and a WordNet synset that groups a kind with its kind ("oxen" with "cattle")
BLOCK = {"chance", "presently", "oxen", "cattle"}


def _pos(synset):
    return synset.split(":")[1][:1].replace("s", "a") if synset and synset.count(":") >= 2 else ""


def _dominant(word):
    """the word's most common sense is clearly its sense, and its word class is not in doubt: one sense only, or used at
    least 4x as often as the next; and no other word class (noun / verb / adjective / adverb) has a third of its use.
    WordNet does not read the sentence: "thought" (verb here) and "resident population" (adjective here) are skipped."""
    s = senses(word)
    if not s or (len(s) > 1 and (s[0][1] or 0) < 4 * max(1, s[1][1] or 0)):
        return False
    by = {}
    for sid, n in s:
        by[_pos(sid)] = by.get(_pos(sid), 0) + (n or 0)
    top = by.get(_pos(s[0][0]), 0)
    return all(v * 3 < max(top, 1) for k, v in by.items() if k != _pos(s[0][0]))


def _swap_ok(a, b):
    """b may stand for a: the same most-common sense, both ways, that sense clearly dominant for both, b a plain word.
    Word sense in context is not read; dominance is the guard against "bank" (river) becoming "depository"."""
    if a.lower() == b.lower() or not re.fullmatch(r"[a-z]+", b) or len(b) < 3:
        return False
    if a.lower() in BLOCK or b in BLOCK:
        return False
    if INFLECTED.search(a.lower()) or INFLECTED.search(b) or b.startswith(a.lower()) or a.lower().startswith(b):
        return False                                  # word forms, not synonyms: "older"/"elderly", "profit"/"profits"
    sa, sb = first_sense(a), first_sense(b)
    if sa is None or sa != sb or sa.startswith("wordnet:v") or not (_dominant(a) and _dominant(b)):   # verbs inflect; left alone
        return False
    na, nb = count_in(a.lower(), sa), count_in(b, sa)
    return nb >= max(5, 0.5 * na)                     # a common word in this sense ("big" for "large"; not "metropolis" for "city")


def spans(s):
    return [(m.start(), m.end(), m.group(0)) for m in WORD.finditer(str(s or ""))]


def replace_at(s, start, end, new):
    return s[:start] + new + s[end:]


def synonym_proposals(s, limit=6):
    out = []
    for i, (a, b_, t) in enumerate(spans(s)):
        lw = t.lower()
        if i == 0 or not t.isalpha() or not t.islower() or lw in FUNCTION or lw in KEEP or len(lw) < 4:
            continue
        syn = first_sense(lw)
        if not syn or syn.startswith("wordnet:v"):
            continue
        for b in lemmas(syn):
            if _swap_ok(lw, b):
                out.append((replace_at(s, a, b_, b), [("swap", lw, b)]))
                if len(out) >= limit:
                    return out
    return out


def fronting_proposal(s):
    m = TAIL.match(str(s or "").strip())
    if not m:
        return None
    body, pp = m.group("body").strip(), m.group("pp").strip()
    first = body.split()[0]
    if first in OPENERS_LOWER:
        body = body[:1].lower() + body[1:]
    elif not (first[:1].isupper() and len(first) > 1):
        return None
    return "%s%s, %s." % (pp[:1].upper(), pp[1:], body), [("front", pp)]


def verify(record, rewrite, moves):
    """read the rewrite back: kept only when its meaning signature equals the record's and every swap is symmetric"""
    if signature(record) != signature(rewrite):
        return False
    for mv in moves:
        if mv[0] == "swap" and not _swap_ok(mv[1], mv[2]):
            return False
    return True


def rewrites(record, limit=6):
    """verified rewrites of one record sentence: [(text, moves)], fronted forms first"""
    if not available():
        return []
    props = []
    f = fronting_proposal(record)
    if f:
        props.append(f)
    props += synonym_proposals(record, limit)
    if f:
        for text, mv in synonym_proposals(f[0], 2):
            props.append((text, f[1] + mv))
    seen, out = set(), []
    for text, mv in props:
        if text != record and text not in seen and verify(record, text, mv):
            seen.add(text)
            out.append((text, mv))
    return out[:limit]


# ------------------------------------------------------------------ the check's own test: fakes it must refuse
def planted_fakes(record, rng, other_names=()):
    """meaning-changing edits of a record sentence: [(kind, text, moves)] - each must be refused by verify"""
    sp = spans(record)
    out = []
    nums = [x for x in sp if NUM.match(x[2])]
    if nums:
        a, b, t = rng.choice(nums)
        v = t.replace(",", "")
        nv = str(int(float(v)) + rng.choice([1, 2, 7, 10])) if "." not in v else "%.2f" % (float(v) * 1.5)
        out.append(("number", replace_at(record, a, b, nv), []))
    names = [x for i, x in enumerate(sp) if i > 0 and x[2][:1].isupper() and x[2].isalpha() and x[2].lower() not in FUNCTION]
    if names and other_names:
        a, b, t = rng.choice(names)
        alt = [n for n in other_names if n != t]
        if alt:
            out.append(("name", replace_at(record, a, b, rng.choice(alt)), []))
    for i, (a, b, t) in enumerate(sp):
        if t.lower() in ("is", "are", "was", "were", "can", "has", "have") and i + 1 < len(sp):
            out.append(("negation", replace_at(record, a, b, t + " not"), []))
            break
    content = [x for i, x in enumerate(sp) if i > 0 and x[2].isalpha() and x[2].islower() and x[2] not in FUNCTION and x[2] not in KEEP
               and first_sense(x[2]) and not first_sense(x[2]).startswith("wordnet:v")]
    if content:
        a, b, t = rng.choice(content)
        par = parent(first_sense(t))
        gen = [w for w in (lemmas(par) if par else ()) if re.fullmatch(r"[a-z]+", w) and w != t]
        if gen:
            out.append(("general", replace_at(record, a, b, gen[0]), [("swap", t, gen[0])]))
        unrelated = ["window", "river", "music", "bread", "engine", "doctor", "garden", "storm"]
        w = rng.choice([u for u in unrelated if u != t])
        out.append(("unrelated", replace_at(record, a, b, w), [("swap", t, w)]))
    return out
