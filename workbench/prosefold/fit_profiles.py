#!/usr/bin/env python3
"""fit_profiles - the essay options' profiles, MEASURED from corpora (the "training": no gradient, no language model).

For each corpus it fits:
  - a reading-level profile: the Flesch-Kincaid grade of a large sample of its sentences (median and the 25-75% band);
  - a ProseFold voice profile: ProseFold's nine voice measures of the corpus as running text, and the target ranges
    ProseFold.from_corpus derives from them.
Corpora (all inside the full release): Simple English Wikipedia sentences ("simple"), English Wikipedia lead sentences
("general"), OpenStax textbook paragraphs ("technical"), and Prometheus7's essay The Slow Fire (voice only).
Writes profiles.json beside this file. Deterministic: samples are drawn by a fixed hash order, not at random.
usage: fit_profiles.py <deep wikipedia store .sqlite3> <textbook store .sqlite3> [out.json]"""
from __future__ import annotations

import hashlib
import json
import re
import sqlite3
import statistics
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from prosefold.prose import ProseFoldToy  # noqa: E402

N_SENT = 20000
VOWELS = re.compile(r"[aeiouy]+")


def syllables(word):
    w = word.lower().strip(".,;:!?\"'()")
    if not w:
        return 0
    n = len(VOWELS.findall(w))
    if w.endswith("e") and not w.endswith(("le", "ee")) and n > 1:
        n -= 1
    return max(1, n)


def fk_grade(text):
    """Flesch-Kincaid grade level of one sentence or passage"""
    words = re.findall(r"[A-Za-z][A-Za-z'-]*", text)
    sents = max(1, len(re.findall(r"[.!?](?:\s|$)", text)) or 1)
    if not words:
        return 0.0
    syl = sum(syllables(w) for w in words)
    return round(0.39 * len(words) / sents + 11.8 * syl / len(words) - 15.59, 2)


def sample(rows, n):
    rows = sorted(rows, key=lambda r: hashlib.sha256(r[0].encode()).hexdigest())
    return [r[1] for r in rows[:n]]


def level_profile(sentences):
    g = sorted(fk_grade(s) for s in sentences if len(s.split()) >= 5)
    q = lambda p: g[int(p * (len(g) - 1))]  # noqa: E731
    return {"n": len(g), "median": round(statistics.median(g), 2), "p25": round(q(0.25), 2), "p75": round(q(0.75), 2)}


def voice_profile(text):
    toy = ProseFoldToy.from_corpus(text)
    return {"params": toy.parameterize(text), "ranges": {k: list(v) for k, v in toy.target_ranges.items()}}


def main():
    deep, books = sys.argv[1], sys.argv[2]
    out = Path(sys.argv[3]) if len(sys.argv) > 3 else HERE / "profiles.json"
    c = sqlite3.connect("file:%s?mode=ro" % deep, uri=True)
    simple, general = [], []
    for cid, fact in c.execute("select c0, c1 from source_rows_content where c0 like 'simplewiki%' limit 400000"):
        simple.append((cid, " ".join(str(fact).split())))
    for cid, fact in c.execute("select c0, c1 from source_rows_content where c0 like 'enwiki%' limit 400000"):
        general.append((cid, " ".join(str(fact).split())))
    t = sqlite3.connect("file:%s?mode=ro" % books, uri=True)
    paras = [("openstax_%d" % i, " ".join(str(x).split())) for i, x in t.execute("select id, text from item where kind='para' and length(text) > 200")]
    tech = []
    for pid, p in paras:
        for j, s in enumerate(re.split(r"(?<=[.!?])\s+(?=[A-Z])", p)):
            if len(s.split()) >= 5 and not re.search(r"[=∑∫√]|\$", s):
                tech.append(("%s_%d" % (pid, j), s))
    corpora = {"simple": sample(simple, N_SENT), "general": sample(general, N_SENT), "technical": sample(tech, N_SENT)}
    prof = {"fitted": "2026-10-16", "method": "Flesch-Kincaid grade per sentence; ProseFold voice measures of the running text",
            "levels": {}, "voices": {}, "sizes": {k: len(v) for k, v in corpora.items()}}
    for k, sents in corpora.items():
        prof["levels"][k] = level_profile(sents)
        prof["voices"][k] = voice_profile(" ".join(sents[:4000]))
    slow_fire = (HERE / "voice_default.md").read_text(encoding="utf-8")
    prof["voices"]["prometheus7"] = voice_profile(slow_fire)
    prof["voice_names"] = {"simple": "Plain", "general": "Encyclopedic", "technical": "Textbook", "prometheus7": "Prometheus7 (The Slow Fire)"}
    out.write_text(json.dumps(prof, indent=1), encoding="utf-8")
    print(json.dumps({"levels": prof["levels"], "sizes": prof["sizes"]}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
