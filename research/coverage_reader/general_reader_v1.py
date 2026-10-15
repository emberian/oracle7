#!/usr/bin/env python3
"""general_reader_v1 - a relation reader that does not depend on how a question is phrased (Box C).
For a question the release declines: find the entities it names (exact Wikipedia titles), read every fact one step from them in
the Wikidata relation store, and answer ONLY when all three agree:
  (1) CUE   - the relation is named by the question's own words (property label stems, or a measured router cue pair)
  (2) TYPE  - the answer is the kind of thing asked for (who -> a person; where -> a place; "which comedian" -> a comedian)
  (3) UNIQUE- exactly one candidate survives (two different answers -> decline)
The answer is never an entity the question itself names. Every answer carries its receipt (subject, property, value, ids).
usage (dev measurement): general_reader_v1.py eval <trivia json ...>  |  general_reader_v1.py ask "<question>" """
import json
import re
import sqlite3
import sys
import unicodedata

STORE = "/opt/oracle-clm/relstore/relations_v2.sqlite3"
db = sqlite3.connect("file:%s?mode=ro&immutable=1" % STORE, uri=True, check_same_thread=False)

STOP = set("a an the of in on at to for by with from and or is was were are be been being who whom whose what which when where why how "
           "did does do has have had this that these those it its he she they his her their as into than then there here one".split())
AUX = set("is was were are did does do has have had can could will would should may might".split())
HUMAN_Q = ("who", "whom", "whose")
PLACE_WORDS = set("city town village country state province region county island capital place municipality commune borough "
                  "district settlement port river mountain lake sea ocean continent area".split())
GENERIC_TYPE = set("one name person people thing year type kind part title area word term number".split())
# qualifiers the reader cannot evaluate from one fact: order, extremes, time, fiction or a work's own world
QUALIFIER = re.compile(r"\b(first|last|only|second|third|fourth|fifth|oldest|youngest|largest|smallest|biggest|longest|shortest|"
                       r"highest|lowest|tallest|most|least|best|worst|original|former|current|currently|previous|next|latest|earliest|"
                       r"famous|famously|nicknamed|known as|better known|called|real name|in the (?:bible|film|movie|novel|book|play|"
                       r"series|show|song|opera|musical|game|tv|story|poem|legend)|in (?:greek|roman|norse) mythology|"
                       r"(?:1[0-9]|20)[0-9]{2}|century|decade|year|when|during|at the time|outbreak|battle|war|preceded|succeeded|before|after|"
                       r"between|same|other|also|both|nickname|setting|set in|according to)\b", re.I)

PROP, PROPNAMES = {}, {}
for p, lab in db.execute("SELECT p, label FROM prop_src"):
    if lab:
        PROP[p] = lab
for line in open("/opt/oracle-clm/relstore/prop_labels.tsv", encoding="utf-8"):
    m = re.match(r'<http://www\.wikidata\.org/entity/P(\d+)>\t"(.*)"@en', line.strip())
    if m:
        p = int(m.group(1))
        PROPNAMES.setdefault(p, []).append(m.group(2))      # the file holds the label AND its aliases, one per line
        PROP.setdefault(p, m.group(2))
# everyday words for common relations (question wording differs from Wikidata's label); measured on dev like everything else
ALIASES = {26: "married marry wife husband spouse", 25: "mother", 22: "father", 3373: "sister brother sibling", 40: "son daughter child",
           50: "writer author novelist", 57: "directed director", 86: "composed composer music", 170: "created creator",
           112: "founded founder", 36: "capital", 19: "born birthplace", 20: "died death", 569: "born", 570: "died",
           175: "singer performer", 161: "starred", 69: "studied attended educated", 108: "worked employer",
           54: "played team", 166: "won awarded award", 131: "located situated", 138: "named", 37: "language spoken official",
           38: "currency", 6: "prime minister mayor premier", 35: "president king queen monarch emperor", 27: "nationality citizen",
           800: "known work", 61: "discovered discoverer", 397: "orbits orbit", 30: "continent", 140: "religion", 102: "party",
           127: "owned owner owns", 176: "made built manufactured manufacturer", 84: "designed architect", 674: "characters character",
           1441: "appears appear", 136: "genre", 264: "label", 98: "edited editor", 162: "produced producer", 58: "screenplay screenwriter",
           710: "participant participated", 1346: "won winner", 17: "country", 495: "country", 159: "headquarters based", 740: "formed",
           571: "founded established formed", 576: "dissolved abolished", 1037: "director manager", 488: "chairman chairperson",
           169: "chief executive ceo", 286: "head coach manager", 451: "partner", 1038: "relative", 1327: "partner", 413: "position played",
           118: "league", 641: "sport", 115: "home stadium ground venue", 361: "part", 150: "contains", 206: "located", 1376: "capital"}
ALIAS_STEMS = {}
try:
    ALLOW = set(json.load(open("/opt/oracle-clm/relstore/reader_prop_allowlist.json")))   # relations the admitted relation specialists read
except Exception:  # noqa: BLE001
    ALLOW = set()
ALLOW -= {102, 1082}                      # party membership changes; population is a number
SKIP_PROPS = {21, 971, 735, 734, 1343, 910, 4224, 1889, 31, 279, 373, 646, 214, 227, 244, 213, 268, 269, 349, 434, 435, 436,
              1006, 1015, 1017, 1263, 2671, 3417, 5008, 1424, 1151, 1792, 3876, 361, 527, 5869, 2184, 8402, 1482, 3222}


def norm(s):
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode("ascii")
    return " ".join(re.sub(r"[^a-z0-9 ]+", " ", s.lower()).split())


def stem(w):
    w = w.lower()
    if w.endswith("ied") and len(w) <= 5:              # died -> die, lied -> lie
        return w[:-1]
    for suf in ("ations", "ation", "ings", "ing", "ers", "ors", "er", "or", "ed", "es", "s", "ion"):
        if len(w) > len(suf) + 3 and w.endswith(suf):
            return w[: -len(suf)]
    return w


_lab, _cls = {}, {}


def label(q):
    if q not in _lab:
        r = db.execute("SELECT label, enwiki FROM entity WHERE qid=?", (q,)).fetchone()
        _lab[q] = (r[0] or r[1]) if r else None
    return _lab[q]


def classes(q):
    if q in _cls:
        return _cls[q]
    out, frontier, seen = set(), [o for (o,) in db.execute("SELECT o FROM fact WHERE s=? AND p=31", (q,)) if o], set()
    for d in range(2):                                     # its class and one parent: higher superclasses name things it is not
        nxt = []
        for c in frontier:
            if c in seen:
                continue
            seen.add(c)
            lab = label(c)
            if lab:
                ws = norm(lab).split()
                if ws:
                    out.add(ws[-1])                         # head noun: "town in Finland" is a town, not a Finland
            if d < 1:
                nxt += [o for (o,) in db.execute("SELECT o FROM fact WHERE s=? AND p=279", (c,)) if o]
        frontier = nxt
    _cls[q] = out
    return out


_cls0 = {}
GEO_SYN = {"country": "country state kingdom republic nation monarchy federation empire principality sultanate emirate",
           "city": "city town capital metropolis municipality borough commune", "town": "town city municipality borough commune village",
           "state": "state province", "county": "county shire", "island": "island atoll", "river": "river stream tributary",
           "mountain": "mountain peak volcano massif summit", "lake": "lake reservoir", "sea": "sea", "ocean": "ocean"}
GEO_SYN = {stem(k): set(stem(x) for x in v.split()) for k, v in GEO_SYN.items()}


def classes0(q):
    """head nouns of the thing's own classes (P31 only): a city is a city, not the country its classes sit under"""
    if q not in _cls0:
        out = set()
        for (o,) in db.execute("SELECT o FROM fact WHERE s=? AND p=31", (q,)):
            lab = label(o) if o else None
            ws = norm(lab).split() if lab else []
            if ws:
                out.add(stem(ws[-1]))
        _cls0[q] = out
    return _cls0[q]


def is_human(q):
    return db.execute("SELECT 1 FROM fact WHERE s=? AND p=31 AND o=5 LIMIT 1", (q,)).fetchone() is not None


def ent(title):
    t = title.strip(" .,'\"")
    if not t:
        return None
    for v in dict.fromkeys((t, t[:1].upper() + t[1:], " ".join(w[:1].upper() + w[1:] for w in t.split()))):
        r = db.execute("SELECT qid FROM entity WHERE enwiki=? LIMIT 1", (v,)).fetchone()
        if r:
            return r[0]
    return None


def linked(q):
    words = re.findall(r"[A-Za-z0-9'\-\.&]+", q.replace('"', " "))
    taken, out = set(), []
    for n in (6, 5, 4, 3, 2, 1):
        for i in range(len(words) - n + 1):
            if any(j in taken for j in range(i, i + n)):
                continue
            span = words[i:i + n]
            if span[0].lower() in STOP or span[-1].lower() in STOP:
                continue
            if n == 1 and (not span[0][:1].isupper() or i == 0 or len(span[0]) < 3):
                continue
            if all(w.lower() in STOP for w in span):
                continue
            before = words[i - 1] if i > 0 else ""
            after = words[i + n] if i + n < len(words) else ""
            if (after[:1].isupper() and after.lower() not in STOP) or (i > 1 and before[:1].isupper() and before.lower() not in STOP):
                continue                                   # part of a longer name ("Andrew Bonar" in "Andrew Bonar Law")
            qid = ent(" ".join(span))
            if qid:
                out.append((" ".join(span), qid))
                taken.update(range(i, i + n))
    return out


def asked_type(q):
    ql = q.lower().strip()
    w = re.findall(r"[a-z]+", ql)
    if not w:
        return None, set()
    if w[0] in HUMAN_Q or " who " in " " + ql[:40] or re.search(r"\bto whom\b|\bwhom\b", ql):
        return "human", set()
    m = re.search(r"\b(?:which|what)\s+((?:[a-z\-]+\s+){0,2}?[a-z\-]+)\s*\?\s*$", ql)     # "... the sister of which actor?"
    if m:
        nouns = set(stem(x) for x in m.group(1).split() if x not in STOP and x not in GENERIC_TYPE)
        if nouns:
            return "noun", nouns
    m = re.match(r"(?:in )?(?:which|what) (city|town|country|state|county|island|river|mountain|lake|sea|ocean)\b", ql)
    if m:
        return "noun", {stem(m.group(1))}
    if w[0] == "where":
        return "place", set()
    if w[0] == "when" or re.match(r"(in )?(what|which) year", ql):
        return "time", set()
    if re.match(r"how (many|much|long|old|far|tall|high)", ql):
        return "number", set()
    m = re.match(r"(?:what|which|who) (?:is|was|are|were) the ([a-z\-]+(?: [a-z\-]+)?) of\b", ql)   # "what is the capital of ..."
    if m:
        head = m.group(1).split()[-1]
        if head not in STOP and head not in GENERIC_TYPE:
            return "rel", {stem(head)}
    m = re.search(r"\b(which|what)\s+((?:[a-z\-]+\s+){0,3}?)([a-z\-]+)\s+(?:" + "|".join(AUX) + r"|[a-z]+ed|[a-z]+s)\b", ql)
    if m:
        nouns = set(stem(x) for x in (m.group(2) + " " + m.group(3)).split() if x not in STOP and x not in GENERIC_TYPE)
        if nouns:
            return "noun", nouns
    return None, set()


_pw = {}


def prop_words(p):
    if p not in _pw:
        s = set()
        for name in PROPNAMES.get(p, [PROP.get(p, "")]):
            ws = [stem(x) for x in norm(name).split() if x not in STOP and len(x) > 2]
            if 0 < len(ws) <= 3:                       # long descriptive aliases are not cues
                s.update(ws)
        _pw[p] = s
    return _pw[p]


# words too loose to name a relation on their own (dev 10-14): "wrote" fits author, lyricist and publisher; "song" fits lyricist;
# "found" (in "found in the museum") stems like "founded"
STOPCUE = {stem(x) for x in ("write wrote written writ song songs theme found find make made play played sing sang known book books "
                                "music musical film films movie movies national").split()}


def cued(p, qwords_stem, qwords):
    qwords_stem = qwords_stem - STOPCUE
    if prop_words(p) & qwords_stem:
        return True
    if p not in ALIAS_STEMS:
        ALIAS_STEMS[p] = set(stem(x) for x in ALIASES.get(p, "").split())
    if ALIAS_STEMS[p] & qwords_stem:
        return True
    return False                                        # cue pairs dropped: "which|city" is not a relation (dev 10-14)


FEMININE = {"actress": "actor", "authoress": "author", "poetess": "poet", "comedienne": "comedian", "sculptress": "sculptor",
            "heroine": "hero", "princess": "prince", "duchess": "duke", "empress": "emperor", "songstress": "singer"}


def type_ok(kind, nouns, cand_qid, lit, p=None):
    if kind == "rel":
        # the relation noun itself ("capital") must be the property: named by the property's own label or aliases
        return p is not None and bool(prop_words(p) & nouns) and (cand_qid is not None or lit is not None)
    if kind == "time":
        return lit is not None and bool(re.search(r"\b1?\d{3,4}\b", str(lit)))
    if cand_qid is None:
        return False
    if kind == "human":
        return is_human(cand_qid)
    if kind == "place":
        return bool(classes(cand_qid) & PLACE_WORDS)
    if kind == "noun":
        nouns = set(stem(FEMININE.get(x, x)) for x in nouns) | nouns
        cw = set(stem(x) for x in classes(cand_qid))
        if "person" in nouns or "man" in nouns or "woman" in nouns:
            return is_human(cand_qid)
        geo = [n for n in nouns if n in GEO_SYN]
        if geo:                                            # "which country": Nairobi is a city (held-out 10-14: Peter Hain)
            return any(classes0(cand_qid) & GEO_SYN[n] for n in geo)
        return bool(cw & nouns) or (is_human(cand_qid) and bool(nouns & occupations(cand_qid)))
    return False


_occ = {}


def occupations(q):
    if q not in _occ:
        s = set()
        for (o,) in db.execute("SELECT o FROM fact WHERE s=? AND p IN (106, 39) LIMIT 30", (q,)):
            if o and label(o):
                ws = norm(label(o)).split()
                if ws:
                    s.add(stem(ws[-1]))                    # the head noun only: "film score composer" is a composer
        _occ[q] = s
    return _occ[q]


_gen = {}


def generic(e):
    """a class or concept, not a particular thing: it is a subclass of something, or many things are instances of it"""
    if e not in _gen:
        sub = db.execute("SELECT 1 FROM fact WHERE s=? AND p=279 LIMIT 1", (e,)).fetchone() is not None
        inst = len(db.execute("SELECT s FROM fact WHERE p=31 AND o=? LIMIT 30", (e,)).fetchall()) >= 30
        occ = len(db.execute("SELECT s FROM fact WHERE p=106 AND o=? LIMIT 30", (e,)).fetchall()) >= 30
        _gen[e] = sub or inst or occ
    return _gen[e]


_word_props = None


def inv_props(qwords_stem, qwords):
    """properties whose label/alias words or cue pairs appear in the question (index built once; was a scan of 38k per entity)"""
    global _word_props
    if _word_props is None:
        _word_props = {}
        for p in set(PROPNAMES) | set(PROP):
            if p in SKIP_PROPS:
                continue
            for w in prop_words(p) | set(stem(x) for x in ALIASES.get(p, "").split()):
                _word_props.setdefault(w, set()).add(p)
    ps = set()
    for w in qwords_stem - STOPCUE:
        ps |= _word_props.get(w, set())
    ps = [p for p in ps if db.execute("SELECT 1 FROM fact WHERE p=? LIMIT 1", (p,)).fetchone()]
    return ps[:60]


SHORT_NAMES = {"uk": 145, "u k": 145, "britain": 145, "great britain": 145, "us": 30, "u s": 30, "usa": 30, "u s a": 30,
               "america": 30, "ussr": 15180, "soviet union": 15180, "uae": 878, "eu": 458, "holland": 55}


def echoed(q, val, ans):
    """the answer is already in the question: by its label, or by a common short name (dev-burned held-out 10-14: "Where
    are Akrotiri and Dhekelia, allocated by treaty to the UK" read the holder, the UK, as the place)"""
    qn = " %s " % norm(q)
    words = [w for w in norm(ans).split() if w not in STOP and w not in ("the", "of")]
    if words and all(" %s " % w in qn for w in words):
        return True
    return val is not None and any(" %s " % k in qn and v == val for k, v in SHORT_NAMES.items())


QWORDS = set("who whom whose what which where when why how in on at of the a an is was were are did does do name".split())


def unlinked_name(q, links):
    """a capitalised name or a quoted title in the question that no linked span covers"""
    covered = set()
    for t, _ in links:
        covered.update(w.lower() for w in re.findall(r"[A-Za-z0-9']+", t))
    for quoted in re.findall(r"[\"“]([^\"”]{2,80})[\"”]", q):
        if not any(quoted.lower() in t.lower() or t.lower() in quoted.lower() for t, _ in links):
            return True
    words = re.findall(r"[A-Za-z][A-Za-z0-9'\-]*", q)
    for i, w in enumerate(words):
        if i == 0 or not w[:1].isupper() or w.lower() in QWORDS or w.lower() in STOP:
            continue
        if w.lower() not in covered:
            return True
    return False


def answer(q):
    if QUALIFIER.search(q):
        return None
    kind, nouns = asked_type(q)
    if kind in (None, "number"):
        return None
    ents = [(t, e) for t, e in linked(q) if not generic(e)]
    if not ents:
        return None
    if unlinked_name(q, linked(q)):
        return None                                        # held-out 10-14: Jennings Brewery -> read Cumbria; Dismaland -> Banksy
    if q.count(",") >= 2 or (re.search(r"\band\b", q) and len(ents) >= 2):
        return None                                        # several clues joined: one fact cannot answer it
    if kind == "rel":
        m = re.search(r"\bof (?:the )?(.+?)(?:\?|$| in | on | at )", q)
        if not m:
            return None
        first = [(t, e) for t, e in ents if m.group(1).lower().startswith(t.lower())]
        if not first:
            return None
        ents = first[:1]                                   # "the capital of the Yukon Territory in Canada": the Yukon, not Canada
    named = {qid for _, qid in ents}
    qwords = set(re.findall(r"[a-z]+", q.lower()))
    qwords_stem = set(stem(x) for x in qwords if x not in STOP)
    if kind == "noun":
        qwords_stem -= nouns                               # the answer-type word is not the relation ("which country ... headquarters")
    cands = {}
    for span, e in ents:
        for p, o, lit in db.execute("SELECT p, o, lit FROM fact WHERE s=? LIMIT 4000", (e,)):
            if p in SKIP_PROPS or p not in ALLOW or (o is not None and o in named):
                continue
            if o is not None and (label(o) or "").startswith("Category:"):
                continue
            if not cued(p, qwords_stem, qwords):
                continue
            if type_ok(kind, nouns, o, lit, p):
                key = ("q", o) if o is not None else ("l", str(lit))
                cands.setdefault(key, []).append((e, p, "fwd"))
        for p in [x for x in inv_props(qwords_stem, qwords) if x in ALLOW]:
            # reverse answers only when the relation's MAIN name is in the question: aliases such as "mother of" on the
            # child relation describe the relation backwards (dev 10-14: "mother of Achilles")
            main = set(stem(x) for x in norm(PROP.get(p, "")).split() if x not in STOP and len(x) > 2)
            if not (main & qwords_stem):
                continue
            subs = [s for (s,) in db.execute("SELECT s FROM fact WHERE p=? AND o=? LIMIT 6", (p, e))]
            if len(subs) > 5:                       # a big group (everyone who received an award): no reverse answer
                continue
            for s in subs:
                if s in named:
                    continue
                if type_ok(kind, nouns, s, None, p):
                    cands.setdefault(("q", s), []).append((e, p, "inv"))
    if len(cands) != 1:
        return None
    (kt, val), why = next(iter(cands.items()))
    if len(ents) >= 2 and len({w[0] for w in why}) < 2:      # two or more named things: at least two must agree (held-out
        return None                                          # 10-14: Jennings Brewery -> Cumbria's capital, Dismaland -> Banksy)
    if False:
        return None
    e, p, d = why[0]
    ans = label(val) if kt == "q" else val
    if not ans:
        return None
    if echoed(q, val if kt == "q" else None, ans):
        return None                                        # the question already names it ("allocated to the UK": not where it is)
    if d == "fwd":
        receipt = "%s (Q%d) - %s (P%d) - %s" % (label(e), e, PROP.get(p, ""), p, ("%s (Q%d)" % (ans, val)) if kt == "q" else ans)
    else:
        receipt = "%s (Q%d) - %s (P%d) - %s (Q%d)" % (ans, val, PROP.get(p, ""), p, label(e), e)
    return {"answer": ans, "receipt": receipt, "prop": p, "dir": d, "kind": kind, "agree": len(why)}


def correct(ans, golds):
    """exact match after normalising, or one contains the other as whole words ("Lake Mead" / "Mead", "The Dirham" /
    "United Arab Emirates dirham"); articles dropped"""
    drop = lambda s: " ".join(w for w in norm(s).split() if w not in ("the", "a", "an"))
    a = drop(ans)
    for g in (drop(x) for x in golds if x):
        if not g:
            continue
        if a == g:
            return True
        if len(g) >= 4 and re.search(r"\b%s\b" % re.escape(g), a):
            return True
        if len(a) >= 4 and re.search(r"\b%s\b" % re.escape(a), g):
            return True
    return False


if __name__ == "__main__":
    if sys.argv[1] == "ask":
        print(json.dumps(answer(sys.argv[2]), indent=1))
        sys.exit()
    import multiprocessing as mp

    def one(item):
        q, golds = item
        try:
            r = answer(q)
        except Exception as e:  # noqa: BLE001
            return ("err", q[:80], str(e)[:80])
        if not r:
            return None
        return ("right" if correct(r["answer"], golds) else "wrong", q[:110], r["answer"], golds[:2], r["receipt"][:130], r["kind"])

    items = [it for f in sys.argv[2:] for it in json.load(open(f))]
    cnt = {"right": 0, "wrong": 0, "err": 0}
    rows = []
    with mp.Pool(6) as pool:
        for i, res in enumerate(pool.imap_unordered(one, items, chunksize=4), 1):
            if res:
                cnt[res[0]] += 1
                rows.append(res)
            if i % 250 == 0:
                print("progress %d/%d right %d wrong %d" % (i, len(items), cnt["right"], cnt["wrong"]), flush=True)
    fired = cnt["right"] + cnt["wrong"]
    print("questions %d fired %d right %d wrong %d errors %d precision %.3f" % (len(items), fired, cnt["right"], cnt["wrong"], cnt["err"], cnt["right"] / max(1, fired)))
    for r in rows:
        if r[0] != "right":
            print("  ", r[0].upper(), r[1:])
    json.dump(rows, open("/root/w240/coverage_eval_last.json", "w"), indent=0)
