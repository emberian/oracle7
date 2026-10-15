#!/usr/bin/env python3
"""path_credit_gen_v1 - VERIFIED OUTCOMES for path memory, from DEV pools only (never a sealed item, never a reported
benchmark window): for each labelled question, the head's reply (route, status) graded against the gold, and the relation
family's reply to the same question graded the same way (the counterfactual route). One JSON line per question.
Pools: TriviaQA train (domains/cache_v1.jsonl, gold aliases), Mintaka train (domains/pool_mintaka_train.json), and the DEV
split of every admitted specialist's own panel (graded by that specialist's scorer). Questions whose normalised text equals
any sealed-test item (tests 3-15, conversation tests 1-3) are skipped.
usage: path_credit_gen_v1.py <runtime .py> <out.jsonl> <shard k> <shards n>"""
import glob
import hashlib
import importlib.util
import json
import os
import random
import re
import sys

sys.setrecursionlimit(20000)
sys.path.insert(0, "/root/w240")
sys.path.insert(1, "/opt/oracle-clm/wander-train")
from fy_diff_v1 import load  # noqa: E402
import oracle_benchmark_organ_v1 as B  # noqa: E402

SPEC = "/opt/oracle-clm/specialists"
norm = lambda s: " ".join(re.findall(r"[a-z0-9]+", str(s).lower()))


def sealed_texts():
    seen = set()
    for f in glob.glob("/root/w240/sealed*.json") + glob.glob("/root/w240/chat/conv_sealed_v*.json"):
        try:
            d = json.load(open(f))
        except Exception:  # noqa: BLE001
            continue
        stack = [d]
        while stack:
            x = stack.pop()
            if isinstance(x, dict):
                if x.get("q"):
                    seen.add(norm(x["q"]))
                stack.extend(x.values())
            elif isinstance(x, list):
                stack.extend(x)
    return seen


def pools():
    rng = random.Random(20261013)
    rows = []
    trivia = []
    for i, l in enumerate(open("/root/w240/domains/cache_v1.jsonl")):
        if i % 40 == 0:
            r = json.loads(l)
            if r.get("gold"):
                trivia.append(r)
    rng.shuffle(trivia)
    rows += [{"pool": "triviaqa_train", "q": r["q"], "gold": r["gold"]} for r in trivia[:1500]]
    mk = json.load(open("/root/w240/domains/pool_mintaka_train.json"))
    mk = list(mk)
    rng.shuffle(mk)
    # rows: [question, [answer aliases], [gold QIDs], category]
    rows += [{"pool": "mintaka_train", "q": r[0], "gold": list(r[1] or [])} for r in mk[:500] if r and r[0] and r[1]]
    for d in sorted(glob.glob(SPEC + "/*/manifest.json")):
        m = json.load(open(d))
        pp = m.get("panel", {}).get("path")
        if not pp or not os.path.exists(pp):
            continue
        try:
            items = [it for it in json.load(open(pp)) if it.get("split") == "dev" and it.get("valid", True)]
        except Exception:  # noqa: BLE001
            continue
        rng2 = random.Random(m["id"])
        rng2.shuffle(items)
        for it in items[:8]:
            rows.append({"pool": "spec_dev", "spec": m["id"], "q": it["q"], "item": it})
    return rows


_SCORERS = {}


def spec_grade(spec_id, item, reply):
    if spec_id not in _SCORERS:
        m = json.load(open("%s/%s/manifest.json" % (SPEC, spec_id)))
        d = m["organ"]["dir"]
        f = os.path.join(d, m["panel"]["scorer_module"] + ".py")
        sp = importlib.util.spec_from_file_location("o7score_%s" % spec_id.replace("-", "_"), f)
        mod = importlib.util.module_from_spec(sp)
        sys.path.insert(0, d)
        try:
            sp.loader.exec_module(mod)
        finally:
            sys.path.remove(d)
        _SCORERS[spec_id] = getattr(mod, m["panel"]["scorer_fn"])
    good, asserted = _SCORERS[spec_id](item, reply or {})
    return "right" if good else ("wrong" if asserted else "declined")


def grade(row, reply):
    if not reply or reply.get("status") != "answered":
        return "declined"
    if row["pool"] == "spec_dev":
        return spec_grade(row["spec"], row["item"], reply)
    gold = [str(g) for g in (row["gold"] if isinstance(row["gold"], list) else [row["gold"]]) if g]
    return "right" if B.contains(str(reply.get("response", "")), gold) else "wrong"


def main():
    rt_path, out, k, n = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
    rt = load(rt_path)
    fam_mod = sys.modules.get(type(rt).__module__)
    sealed = sealed_texts()
    fam = None
    for name in ("oracle_release_runtime_w533",):
        mm = sys.modules.get(name)
        if mm and hasattr(mm, "_c533_family"):
            fam = mm._c533_family
    rows = [r for r in pools() if norm(r["q"]) not in sealed
            and int(hashlib.md5(r["q"].encode()).hexdigest(), 16) % n == k]
    with open(out, "w") as fh:
        for i, r in enumerate(rows):
            try:
                h = rt.chat(r["q"], session_id="credit-%d-%d" % (k, i))
            except Exception as e:  # noqa: BLE001
                h = {"status": "error", "path": "error:%s" % type(e).__name__, "response": ""}
            f = None
            if fam is not None:
                try:
                    f = fam().reply(r["q"], "credit-fam-%d-%d" % (k, i))
                except Exception:  # noqa: BLE001
                    f = None
            rec = {"pool": r["pool"], "spec": r.get("spec"), "q": r["q"],
                   "head": {"path": str(h.get("path", ""))[:160], "status": h.get("status"), "grade": grade(r, h),
                            "reply": str(h.get("response", ""))[:200]},
                   "family": None}
            if f and f.get("status") != "disagree":
                fr = {"status": "withheld" if (f.get("provenance") or {}).get("declined") else f.get("status"),
                      "response": f.get("response"), "path": "specialist_call>" + str(f.get("path"))}
                rec["family"] = {"path": fr["path"][:160], "status": fr["status"], "grade": grade(r, fr), "reply": str(fr["response"])[:200]}
            fh.write(json.dumps(rec) + "\n")
            fh.flush()
    print("CREDIT-GEN-DONE", k, len(rows), flush=True)
    _ = fam_mod


if __name__ == "__main__":
    main()
