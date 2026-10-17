"""options - ProseFold v2: the essay's LENGTH, READING LEVEL, TECHNICAL DEPTH and STYLE, each chosen from measured profiles
(profiles.json, fitted by fit_profiles.py on the release's own corpora: 20,000 sentences each of Simple English Wikipedia,
English Wikipedia leads and OpenStax textbooks). No language model and no rewording: every option works by CHOOSING which
of the record's sentences to use and how ProseFold composes them.

  depth    basic      Simple English Wikipedia (the topic's page, in order)
           standard   + English Wikipedia lead sentences
           technical  English Wikipedia first, + OpenStax textbook sentences that name the topic; sentences carrying
                      numbers, units and longer terms are preferred
  level    young      Flesch-Kincaid grade <= 7      (Simple Wikipedia's easier quarter)
           general    grade 7-12                     (around Simple Wikipedia's median, 9.1)
           advanced   grade >= 11                    (around English Wikipedia's median, 12.8)
           (the essay reports the grade it reached; a level the record cannot reach is reported, not faked)
  length   short 5 sentences, medium 12, long 24, full (every usable sentence)
  style    plain (Simple Wikipedia's voice), encyclopedic (English Wikipedia's), textbook (OpenStax's), prometheus7
           (The Slow Fire), or a file of your own writing
A sentence that points back ("It was made of wood") is only taken with the sentence it points to."""
from __future__ import annotations

import json
import os
import re
import sqlite3
import time
from pathlib import Path

from . import core
from . import speaker as SP
from .fit_profiles import fk_grade, syllables
from .prose import ProseFoldToy

HERE = Path(__file__).resolve().parent
PROFILES = json.loads((HERE / "profiles.json").read_text(encoding="utf-8")) if (HERE / "profiles.json").exists() else {}
LENGTHS = {"short": 5, "medium": 12, "long": 24, "full": 10 ** 6}
LEVELS = {"young": (0.0, 7.0), "general": (7.0, 12.0), "advanced": (11.0, 30.0)}
DEPTHS = ("basic", "standard", "technical")
STYLES = ("plain", "encyclopedic", "textbook", "prometheus7")
STYLE_PROFILE = {"plain": "simple", "encyclopedic": "general", "textbook": "technical", "prometheus7": "prometheus7"}
NUMERIC = re.compile(r"\d|%|°|\b(?:km|kg|m|cm|mm|°C|K|Pa|J|W|V|Hz|mol)\b")


def _deep_store():
    for k in ("ORACLE_DEEP_BUILD", "ORACLE_BENCH_BUILD"):
        p = os.environ.get(k)
        if p and Path(p).exists():
            return Path(p)
    p = Path(os.environ.get("ORACLE_WIKIPEDIA_BUILD", "/nonexistent")) / "wikipedia_specialist.sqlite3"
    return p if p.exists() else None


def _books():
    root = Path(os.environ.get("ORACLE7_ROOT", "/nonexistent"))
    for p in (root / "textbooks" / "textbook_store_v1.sqlite3", Path("/opt/oracle-clm/textbooks/textbook_store_v1.sqlite3")):
        if p.exists() and p.stat().st_size > 1 << 20:
            return p
    return None


def page_records(topic):
    """the topic's page from the deepest store present: Simple English Wikipedia then English Wikipedia sentences, each in
    page order, each with its record id"""
    store = _deep_store()
    if not store:
        return []
    out = []
    try:
        con = sqlite3.connect("file:%s?mode=ro" % store, uri=True)
        key = re.sub(r"[^a-z0-9]+", "_", topic.lower()).strip("_")
        row = con.execute("select page_id from title_alias where normalized_title = ?", (key,)).fetchone()
        if not row:
            return []
        # page_sentence is indexed by page; a WHERE on the FTS content table would scan the whole store (13 GB, ~130 s)
        rows = con.execute("select c.c0, c.c1, ps.sentence_ordinal from page_sentence ps join source_rows_content c "
                           "on c.id = ps.source_rowid where ps.page_id = ? order by ps.sentence_ordinal", (row[0],)).fetchall()
    except Exception:  # noqa: BLE001
        return []

    def order(r):
        return (0 if r[0].startswith("simplewiki") else 1, int(r[2] or 0))
    for i, (cid, fact, ordv) in enumerate(sorted(rows, key=order)):
        t = " ".join(core.html.unescape(str(fact)).replace("\xa0", " ").split())
        if len(t) < 20 or core.WRAPPER.search(t) or core.TIMELINE.match(t):
            continue
        src = "simple" if cid.startswith("simplewiki") else "general"
        out.append({"move": "page", "claim": cid, "layer": src, "ord": int(ordv or 0), "title": topic[:1].upper() + topic[1:],
                    "source": "Simple English Wikipedia (CC BY-SA)" if src == "simple" else "English Wikipedia (CC BY-SA)",
                    "sentence": t if t[-1] in ".!?" else t + "."})
    return out


def textbook_records(topic, limit=12):
    """OpenStax sentences that NAME the topic, from paragraphs whose opening sentence names it (the topic is what the
    paragraph is about, not a passing mention)"""
    books = _books()
    if not books:
        return []
    out, seen = [], set()
    try:
        con = sqlite3.connect("file:%s?mode=ro" % books, uri=True)
        rows = con.execute("select i.id, i.book_title, i.text from item_fts f join item i on i.id = f.rowid "
                           "where item_fts match ? and i.kind = 'para' order by bm25(item_fts) limit 60", ('"%s"' % topic,)).fetchall()
    except Exception:  # noqa: BLE001
        return []
    stem = re.escape(topic.split()[0][:max(4, len(topic.split()[0]) - 2)])
    for pid, book, text in rows:
        sents = re.split(r"(?<=[.!?])\s+(?=[A-Z])", " ".join(str(text or "").split()))
        if not sents or not re.search(r"\b" + stem, " ".join(sents[0].split()[:10]), re.I):
            continue
        for j, s in enumerate(sents):
            if (len(s.split()) < 6 or re.search(r"[=∑∫√]|\$|\\\(| as in \.|\bFigure\b", s) or s in seen
                    or not re.search(r"\b" + stem, " ".join(s.split()[:8]), re.I)):
                continue
            seen.add(s)
            out.append({"move": "textbook", "claim": "openstax_%d_%d" % (pid, j), "layer": "technical", "ord": j, "title": book,
                        "source": "OpenStax, %s (CC BY 4.0)" % book, "sentence": s if s[-1] in ".!?" else s + "."})
            if len(out) >= limit:
                return out
    return out


def technicality(s):
    words = re.findall(r"[A-Za-z][A-Za-z'-]*", s)
    if not words:
        return 0.0
    long_terms = sum(1 for w in words if syllables(w) >= 3) / len(words)
    return round(long_terms + 0.5 * bool(NUMERIC.search(s)), 3)


def _dupe(a, b):
    ka, kb = SP.content_words(a, frozenset()), SP.content_words(b, frozenset())
    return len(ka & kb) >= 0.75 * max(1, min(len(ka), len(kb)))


def select(cands, length, level, depth):
    """choose `length` sentences: the opening definition first, then by fit to the reading level, the depth's preference and
    coverage; an anaphoric sentence only with its predecessor; then back into source order"""
    lo, hi = LEVELS[level]
    n = LENGTHS[length]
    for i, c in enumerate(cands):
        c["grade"] = fk_grade(c["sentence"])
        c["tech"] = technicality(c["sentence"])
        c["idx"] = i
    def fit(c):
        g = c["grade"]
        miss = 0.0 if lo <= g <= hi else min(abs(g - lo), abs(g - hi))
        pref = {"basic": 0.0, "standard": 0.0, "technical": -2.0 * c["tech"]}[depth]
        layer = {"basic": {"simple": 0, "general": 3, "technical": 3}, "standard": {"simple": 0, "general": 0.3, "technical": 2},
                 "technical": {"simple": 0.6, "general": 0, "technical": 0}}[depth][c["layer"]]
        return miss + pref + layer
    pool = [c for c in cands if depth != "basic" or c["layer"] == "simple"]
    if not pool:
        return []
    opening = next((c for c in pool if c["layer"] == ("general" if depth == "technical" else "simple")), pool[0])
    chosen, keys = [opening], [opening]
    taken = {opening["idx"]}
    while len(chosen) < n:
        best, best_need = None, None
        for c in sorted(pool, key=lambda c: fit(c) - (0.9 if (c["idx"] - 1 in taken or c["idx"] + 1 in taken) else 0.0)):
            if c["idx"] in taken or any(_dupe(c["sentence"], k["sentence"]) for k in keys):
                continue
            need = []
            early = " ".join(c["sentence"].split()[:10])
            demo = re.search(r"\b(?:this|these|that|those|such)\s+([a-z][a-z-]{2,})", early, re.I)
            if core.ANAPHOR.match(c["sentence"]) or core.FOLLOWS.match(c["sentence"]) or demo:
                prev = next((p for p in reversed(pool[:pool.index(c)]) if p["layer"] == c["layer"]), None)
                if (prev is None or prev["claim"].split("_")[0] != c["claim"].split("_")[0]
                        or ("ord" in c and prev.get("ord") != c["ord"] - 1)):
                    continue
                m = demo
                if m and m.group(1).lower().rstrip("s") not in prev["sentence"].lower():
                    continue          # "This magma ..." needs a sentence before it that mentions the magma
                if prev["idx"] not in taken:
                    need = [prev]
            if len(chosen) + len(need) + 1 > n and n < 10 ** 6:
                continue
            best, best_need = c, need
            break
        if best is None:
            break
        for x in best_need + [best]:
            chosen.append(x)
            keys.append(x)
            taken.add(x["idx"])
    return sorted(chosen, key=lambda c: c["idx"])


def write(ask, topic, length="medium", level="general", depth="standard", style="plain", voice_path=None):
    """an essay with options -> the same result shape as core.essay, plus the options and the reading grade reached"""
    t0 = time.time()
    if voice_path:
        toy = ProseFoldToy.from_corpus(Path(voice_path).read_text(encoding="utf-8"))
        style_name = "custom"
    else:
        vp = PROFILES.get("voices", {}).get(STYLE_PROFILE.get(style, "simple"))
        toy = ProseFoldToy()
        if vp:
            toy.set_target_ranges({k: tuple(v) for k, v in vp["ranges"].items()})
        style_name = style
    core.TOY = toy
    target = dict(vp["params"]) if not voice_path and vp else toy.parameterize(Path(voice_path).read_text(encoding="utf-8"))
    page = page_records(topic)
    need_plan = ask is not None and len(page) < min(LENGTHS[length], 40)
    plan = core.gather(topic, "prosefold2-%d" % int(t0), ask) if need_plan else []
    for c in plan:
        c["layer"] = "simple" if c["claim"].startswith("simplewiki") else "general"
    books = textbook_records(topic) if depth == "technical" else []
    cands = list(page)
    for c in plan + books:
        if not any(_dupe(c["sentence"], x["sentence"]) for x in cands):
            cands.append(c)
    picked = select(cands, length, level, depth)
    # paragraphs: by layer, then 3-6 sentences, never cut before a sentence that points back
    groups = []
    layers = (("general", ""), ("simple", ""), ("technical", "From the textbooks")) if depth == "technical" else         (("simple", ""), ("general", ""), ("technical", "From the textbooks"))
    for layer, title in layers:
        units = [c for c in picked if c["layer"] == layer]
        cur = []
        for c in units:
            stands = not core.ANAPHOR.match(c["sentence"]) and not core.FOLLOWS.match(c["sentence"])
            if cur and len(cur) >= 3 and stands:
                groups.append(("", cur))
                cur = []
            cur.append(c)
        if cur:
            groups.append((title, cur))
    for c in picked:
        for w in re.findall(r"(?<=\s)([a-z][a-z'-]+)", c["sentence"]):
            core.LOWER_SEEN.add(w)
    paras, titles = [], []
    for title, units in groups:
        best, _, _tr = core.fold_paragraph(units, topic, target, paras)
        paras.append(best)
        titles.append(title)
    faithful, n_sent = 0, 0
    for p in paras:
        for s in p:
            n_sent += 1
            faithful += core.SP.decomposes(s["text"], [x["sentence"] for x in s["parts"]], core.VERBS)[0]
    order = []
    for p in paras:
        for s in p:
            for x in s["parts"]:
                if x["claim"] not in order:
                    order.append(x["claim"])
    num = {c: i + 1 for i, c in enumerate(order)}
    body = []
    for title, p in zip(titles, paras):
        text = " ".join("%s [%s]" % (s["text"], ",".join(str(num[x["claim"]]) for x in s["parts"])) for s in p)
        body.append(("## %s\n\n" % title if title else "") + text)
    ref_of = {c["claim"]: c for c in cands}
    refs = ["%d. %s - %s (%s)" % (num[c], ref_of[c].get("title") or topic, ref_of[c].get("source") or "", c) for c in order]
    plain = core.render(paras)
    grade = fk_grade(plain) if plain else 0.0
    lo, hi = LEVELS[level]
    v = toy.parameterize(plain) if plain else {}
    return {
        "topic": topic, "options": {"length": length, "level": level, "depth": depth, "style": style_name},
        "sentences": n_sent, "faithful": faithful, "claims_seen": len(cands), "records_used": len(order),
        "reading_grade": grade, "level_band": [lo, hi], "level_reached": lo <= grade <= hi,
        "technical_share": round(sum(c["tech"] for c in picked) / max(1, len(picked)), 3),
        "layers": {k: sum(1 for c in picked if c["layer"] == k) for k in ("simple", "general", "technical")},
        "voice_distance": round(core.distance(target, v), 3) if v else None,
        "essay_md": "# %s\n\n%s\n\n### Sources\n\n%s\n" % (topic[:1].upper() + topic[1:], "\n\n".join(body), "\n".join(refs)),
        "seconds": round(time.time() - t0, 1), "lm_calls": 0,
    }
