#!/usr/bin/env python3
"""adjudicate_v1 - the ONLY correction applied to the scorer for the general reader's held-out runs (written and hashed
before the 2026-10-14 held-out run on TriviaQA train offset 140000, n 6000).

Rule: a reply the scorer marks wrong counts as RIGHT only if the answer is a place that the relation store records as
located inside the expected place: following P131 (located in the administrative territorial entity) and P17 (country)
from the answer, up to 6 steps, reaches an entity whose label equals one of the gold strings (case and accents folded).
Example: Foxrock -> Dublin -> Ireland, gold "Ireland". Nothing else is corrected: a different name for the same thing
(renminbi / Yuan), a disagreement with the source (Kingston / Vancouver), or a newer value (a new capital) stays WRONG.
usage: adjudicate_v1.py <coverage_eval_last.json> -> prints scorer counts, adjudicated counts and each changed item"""
import json
import sys
import unicodedata

sys.path.insert(0, "/root/w240")
import general_reader_v1 as G  # noqa: E402


def fold(s):
    return unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode().lower().strip()


def contained_in(qid, golds, steps=6):
    want = {fold(g) for g in golds if g}
    frontier, seen = [qid], set()
    for _ in range(steps):
        nxt = []
        for q in frontier:
            for (o,) in G.db.execute("SELECT o FROM fact WHERE s=? AND p IN (131, 17)", (q,)):
                if o and o not in seen:
                    seen.add(o)
                    if fold(G.label(o) or "") in want:
                        return True
                    nxt.append(o)
        frontier = nxt
    return False


if __name__ == "__main__":
    rows = json.load(open(sys.argv[1]))                   # [verdict, question, answer, golds, receipt, kind] per answered item
    right = sum(1 for r in rows if r[0] == "right")
    items = [r[1:] for r in rows if r[0] != "right"]
    wrong = len(items)
    changed = []
    for it in items:
        q, ans, golds, receipt = it[0], it[1], it[2], it[3]
        m = __import__("re").search(r"\((Q\d+)\)\s*$", receipt)
        if m and contained_in(int(m.group(1)[1:]), golds):
            changed.append((q, ans, golds[:2]))
    n = right + wrong
    print("scorer: %d right / %d wrong of %d answered (%.1f%%)" % (right, wrong, n, 100.0 * right / max(1, n)))
    print("adjudicated: %d right / %d wrong (%.1f%%); changed by the containment rule: %d" % (
        right + len(changed), wrong - len(changed), 100.0 * (right + len(changed)) / max(1, n), len(changed)))
    for c in changed:
        print("   RIGHT by containment:", c)
