#!/usr/bin/env python3
"""specfold_learn.py - learn typed operations from the specialists' own development exams (the fold-composition prototype).

For every standing specialist, each valid dev item whose question carries typed quantities (network_v2's reader: a number with
a unit) and whose reply from the specialist is right (its own scorer) and carries one typed quantity becomes a candidate
operation: a template (the question with its quantities turned into slots in the question's own units), the input dimensions,
the output dimension and unit. Candidates that share a template skeleton cross-check each other: the template of item A,
filled with item B's quantities, must make the specialist reproduce item B's scored answer. An operation is kept only when
it took part in at least one cross-check and every cross-check passed. No held-out item is read.
usage: specfold_learn.py <out.json> [specialist ...]"""
import importlib.util
import json
import os
import re
import sys
from collections import defaultdict

SPEC = __import__("os").environ.get("ORACLE7_ROOT", "/opt/oracle-clm") + "/specialists"
GATE = SPEC + "/_gate"
sys.path.insert(0, GATE)
import network_v2 as V2  # noqa: E402
from combo_runtime_v1 import _Organ  # noqa: E402

STANDING = ["standing_v2", "standing_new_v1", "standing_new_v2", "standing_new_v3", "standing_new_v4", "standing_new_v5"]


def members():
    ids = []
    for f in STANDING:
        for s in open("%s/%s.txt" % (GATE, f)).read().split():
            ids += s.split("+")
    return sorted(set(ids))


def panel_and_scorer(sid):
    m = json.load(open(os.path.join(SPEC, sid, "manifest.json")))
    pp = m.get("panel", {}).get("path", "").replace(__import__("os").environ.get("ORACLE7_ROOT", "/opt/oracle-clm") + "", __import__("os").environ.get("ORACLE7_ROOT", "/opt/oracle-clm") + "")
    if not os.path.exists(pp):
        return None, None
    d = os.path.dirname(pp)
    spec = importlib.util.spec_from_file_location("sc_%s" % sid.replace("-", "_"), os.path.join(d, m["panel"].get("scorer_module", "scorer") + ".py"))
    mod = importlib.util.module_from_spec(spec)
    sys.path.insert(0, d)
    spec.loader.exec_module(mod)
    return json.load(open(pp, encoding="utf-8")), getattr(mod, m["panel"].get("scorer_fn", "ok"))


def quantities(text):
    out = []
    for m in V2.RX_QTY.finditer(text):
        u = V2.unit_lookup(m.group(2))
        if not u:
            continue
        try:
            v = V2.fnum(m.group(1))
        except ValueError:
            continue
        out.append({"span": [m.start(), m.end()], "num": m.group(1), "unit": m.group(2), "si": v * u[0], "factor": u[0], "dim": u[1]})
    return out


def template(q, qs):
    """the question with each quantity's number replaced by a slot, its unit kept: [text, slot, text, slot, ...]"""
    parts, last = [], 0
    for i, x in enumerate(qs):
        a, b = x["span"]
        num_end = a + len(x["num"])
        parts.append(q[last:a])
        parts.append({"slot": i, "factor": x["factor"], "dim": x["dim"]})
        last = num_end
    parts.append(q[last:])
    return parts


def fill(parts, si_values):
    s = ""
    for p in parts:
        if isinstance(p, dict):
            s += V2.g(si_values[p["slot"]] / p["factor"])
        else:
            s += p
    return s


def skeleton(parts):
    return "".join("#" + str(p["dim"]) if isinstance(p, dict) else re.sub(r"\s+", " ", p.lower()) for p in parts)


STOP = set("""what whats how many much is are was were the a an of in on at to for from by with and or does do did it its it's
this that these those there their his her be been being will would can could should into per each every than then as if when
which who whom whose your you my me i we our us use uses used take takes taking get gets give gives make makes long far fast
big large small value amount number total answer about after before during over under up down out off away toward towards
s""".split())


def context_words(parts):
    """the template's constant words that carry meaning (names, materials, objects): a learned operation fires only when all of
    them appear in the question being answered"""
    text = " ".join(p for p in parts if isinstance(p, str)).lower()
    words = re.findall(r"[a-z][a-z0-9'-]*[a-z0-9]|[a-z]", text)
    return sorted({w for w in words if w not in STOP and not V2.unit_lookup(w) and len(w) > 1} |
                  set(re.findall(r"(?<![\w.])\d[\d,]*(?:\.\d+)?%?", text)))      # numbers in the fixed text are context too


def numeric_answer(it):
    for k in ("a", "expect", "answer"):
        v = it.get(k)
        if isinstance(v, (int, float)):
            return float(v)
        if isinstance(v, str):
            m = re.fullmatch(r"\s*(-?\d[\d,]*(?:\.\d+)?)\s*", v)
            if m:
                return float(m.group(1).replace(",", ""))
    return None


def main():
    out_path = sys.argv[1]
    sids = sys.argv[2:] or members()
    learned, stats, seen = [], defaultdict(int), set()
    for sid in sids:
        try:
            panel, sc = panel_and_scorer(sid)
            if not panel:
                stats["no panel"] += 1
                continue
            org = _Organ(os.path.join(SPEC, sid, "manifest.json"), os.path.join(SPEC, sid))
        except Exception as e:  # noqa: BLE001
            stats["load error"] += 1
            continue
        cands = []
        for it in panel:
            if it.get("split") != "dev" or not it.get("valid", True):
                continue
            qs = quantities(it["q"])
            if not qs or len({x["dim"] for x in qs}) != len(qs):     # each slot must be told apart by its dimension
                continue
            r = org.reply(it["q"], "specfold") or {}
            rep = {"status": "declined" if r.get("declined") else r.get("status", "answered"), "response": r.get("response", "")}
            good, _ = sc(it, rep)
            if not good:
                continue
            want = numeric_answer(it)
            if want is None:
                continue                                        # only items whose scored answer is a number
            outq = [x for x in quantities(re.split(r"\s\(|\[", rep["response"], 1)[0])
                    if abs(x["si"] / x["factor"] - want) <= 0.011 * max(abs(want), 1e-9)]
            if len(outq) != 1:
                continue                                        # the reply's quantity must BE the scored answer, in its unit
            o = outq[0]
            if o["dim"] in {x["dim"] for x in qs} and len(outq) == 1 and abs(o["si"] - qs[[x["dim"] for x in qs].index(o["dim"])]["si"]) < 1e-12:
                continue                                        # the reply only repeats a given
            parts = template(it["q"], qs)
            cands.append({"sid": sid, "q": it["q"], "parts": parts, "in": [x["dim"] for x in qs], "si": [x["si"] for x in qs],
                          "out_dim": o["dim"], "out_unit": o["unit"], "out_si": o["si"], "skeleton": skeleton(parts), "item": it})
        stats["candidates"] += len(cands)
        groups = defaultdict(list)
        for c in cands:
            groups[(c["skeleton"], c["out_dim"])].append(c)
        for key, grp in groups.items():
            if len(grp) < 2:
                stats["single (no cross-check)"] += 1
                continue
            a = grp[0]
            if any(len({round(c["si"][i], 12) for c in grp}) == 1 for i in range(len(a["si"]))):
                stats["constant slot"] += 1                     # a slot that never varies is part of the phrasing, not an input
                continue
            checks = ok = 0
            for b in grp[1:]:
                qtext = fill(a["parts"], b["si"])
                r = org.reply(qtext, "specfold") or {}
                rep = {"status": "declined" if r.get("declined") else r.get("status", "answered"), "response": r.get("response", "")}
                good, _ = sc(b["item"], rep)
                checks += 1
                ok += bool(good)
            if checks >= 1 and ok == checks:
                sig = (a["sid"], tuple(map(str, a["in"])), str(a["out_dim"]), tuple(context_words(a["parts"])))
                if sig in seen:
                    stats["duplicate"] += 1
                    continue
                seen.add(sig)
                learned.append({k: a[k] for k in ("sid", "q", "parts", "in", "out_dim", "out_unit", "skeleton")} |
                               {"checks": checks, "context": context_words(a["parts"])})
                stats["learned"] += 1
            else:
                stats["failed cross-check"] += 1
    json.dump({"ops": learned, "stats": dict(stats)}, open(out_path, "w"), indent=1, default=str)
    print(dict(stats))
    for o in learned[:40]:
        print(o["sid"], o["in"], "->", o["out_dim"], o["out_unit"], "|", o["q"][:80], "| ctx", o["context"][:6], "| checks", o["checks"])


if __name__ == "__main__":
    main()
