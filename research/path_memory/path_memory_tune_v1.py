#!/usr/bin/env python3
"""path_memory_tune_v1 - choose w535's thresholds on 80% of the credit data and REPORT the held-back 20% (md5(q) % 5 == 0),
before sealed test 15 is run. For each graded question the fixed routing's outcome is the head's grade; path memory's outcome
is simulated from the same record: the head's answer stands unless its route has lost credit for the question's shape; then
the recorded family answer is used if the family's route has earned credit, else the turn is withheld (declined).
Objective (fixed here): right - 3 x wrong (a wrong answer costs three right ones). Reported for both arms on the held-back
fifth: right, wrong, declined, precision on answered.
usage: path_memory_tune_v1.py <credit .jsonl ...>"""
import hashlib
import itertools
import json
import sys

sys.path.insert(0, "/root/w240")
sys.path.insert(1, "/opt/oracle-clm/wander-train")
import path_memory_v1 as P  # noqa: E402


def load(files):
    rows = []
    for f in files:
        for line in open(f):
            r = json.loads(line)
            r["_hold"] = int(hashlib.md5(r["q"].encode()).hexdigest(), 16) % 5 == 0
            r["_shape"] = P.shape(r["q"])
            rows.append(r)
    return rows


def memory(rows):
    pm = P.PathMemory()
    for r in rows:
        for arm in ("head", "family"):
            x = r.get(arm)
            if x and x.get("status") == "answered" and x.get("grade") in ("right", "wrong"):
                pm.credit(r["_shape"], P.route_of(x["path"]), x["grade"])
    return pm


def simulate(rows, pm, p_low, p_high, min_n, mode="swap_or_withhold"):
    fixed, mem = {"right": 0, "wrong": 0, "declined": 0}, {"right": 0, "wrong": 0, "declined": 0}
    swaps = withholds = 0
    for r in rows:
        h = r["head"]
        g = h["grade"] if h.get("status") == "answered" else "declined"
        fixed[g] += 1
        if g == "declined":
            mem["declined"] += 1
            continue
        r0 = P.route_of(h["path"])
        p0 = None if r0 in ("guard", "none") else pm.precision(r["_shape"], r0, min_n=min_n)
        if p0 is None or p0[0] >= p_low:
            mem[g] += 1
            continue
        f = r.get("family")
        p1 = pm.precision(r["_shape"], "specialist:rel", min_n=min_n)
        if r0 != "specialist:rel" and f and f.get("status") == "answered" and p1 and p1[0] >= p_high and p1[0] > p0[0]:
            mem[f["grade"] if f["grade"] in ("right", "wrong") else "declined"] += 1
            swaps += 1
        elif mode == "swap_only" or (mode.startswith("hybrid") and not (p0[0] < float(mode.split(":")[1]) and p0[1] >= 20)):
            mem[g] += 1
        else:
            mem["declined"] += 1
            withholds += 1
    return fixed, mem, swaps, withholds


def score(c):
    return c["right"] - 3 * c["wrong"]


def prec(c):
    a = c["right"] + c["wrong"]
    return round(c["right"] / a, 4) if a else None


def main():
    rows = load(sys.argv[1:])
    train = [r for r in rows if not r["_hold"]]
    hold = [r for r in rows if r["_hold"]]
    pm_train = memory(train)
    # v1.1 (after the first held-back report, disclosed): choose on TRAIN by the SEALED TEST 15 rule itself - more right, no
    # more wrong, precision not lower - over two policy families; ties go to fewer wrong answers
    best = None
    for mode in ("swap_or_withhold", "swap_only", "hybrid:0.2", "hybrid:0.3", "hybrid:0.4"):
        for p_low, p_high, min_n in itertools.product((0.3, 0.4, 0.5, 0.6, 0.7, 0.8), (0.6, 0.7, 0.8, 0.9), (4, 6, 10, 20)):
            fixed, mem, s, w = simulate(train, pm_train, p_low, p_high, min_n, mode)
            ok = mem["wrong"] <= fixed["wrong"] and (prec(mem) or 0) >= (prec(fixed) or 0)
            key = (ok, mem["right"] - fixed["right"], -(mem["wrong"]))
            if best is None or key > best[0]:
                best = (key, mode, p_low, p_high, min_n)
    key, mode, p_low, p_high, min_n = best
    gain = key[1]
    print("rows %d (train %d, held back %d) | paths in train memory %d" % (len(rows), len(train), len(hold), len(pm_train.entries)))
    print("CHOSEN on train: mode %s P_LOW %.2f P_HIGH %.2f MIN_N %d (train right gain %+d, rule met %s)" % (mode, p_low, p_high, min_n, gain, key[0]))
    fixed, mem, s, w = simulate(hold, pm_train, p_low, p_high, min_n, mode)
    print("HELD-BACK fixed routing: %s precision %s objective %d" % (fixed, prec(fixed), score(fixed)))
    print("HELD-BACK path memory:   %s precision %s objective %d | swaps to a specialist %d, withheld %d" % (mem, prec(mem), score(mem), s, w))
    json.dump({"MODE": mode, "P_LOW": p_low, "P_HIGH": p_high, "MIN_N": min_n, "train_rows": len(train), "held_rows": len(hold),
               "held_fixed": fixed, "held_memory": mem, "swaps": s, "withheld": w},
              open("/root/w240/path_memory_tuning_v1.json", "w"), indent=1)


if __name__ == "__main__":
    main()
