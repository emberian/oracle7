"""v4_dose.py <out.json> - the I3 dose-response (build brief, I3): 4.0 at three throughput settings on development questions
(sealed test 23's, spent): (1) recall off, (2) recall on, first pass, (3) recall on, the same questions again (recalled walks).
Each setting's mean k and mean L; the slope of mean k on mean L across settings, with a bootstrap interval over items.
Settings 1 and 2-3 run in separate processes (no warm cache crosses from 1 to 2)."""
import json
import os
import random
import subprocess
import sys

if len(sys.argv) > 2 and sys.argv[1] == "--arm":
    setting, out = sys.argv[2], sys.argv[3]
    os.environ["ORACLE7_V4_RECALL"] = "0" if setting == "off" else "1"
    os.environ["ORACLE7_V4_LEDGER"] = out + ".ledger.jsonl"
    sys.path.insert(0, "/root/w240")
    sys.path.insert(0, "/opt/oracle-clm/fable-content/oracle-m-series-2026-08-15/self_loop/admitted")
    sys.path.insert(0, "/opt/oracle-clm/wander-train")
    from oracle_release_runtime_w557 import OracleReleaseRuntimeW557
    R = OracleReleaseRuntimeW557()
    qs = [x["q"] for x in json.load(open("/root/w240/sealed23.json"))]
    R.chat("What is the capital of Peru?", "dose-warm")
    open(out + ".ledger.jsonl", "w").close()
    for rep in range(1 if setting == "off" else 2):
        for i, q in enumerate(qs):
            R.chat(q, "dose-%s-%d-%d" % (setting, rep, i))
    sys.exit(0)

OUT = sys.argv[1]
for s in ("off", "on"):
    subprocess.run([sys.executable, __file__, "--arm", s, OUT + "." + s], check=True)
rows = {}
off = [json.loads(l) for l in open(OUT + ".off.ledger.jsonl")]
on = [json.loads(l) for l in open(OUT + ".on.ledger.jsonl")]
n = len(off)
rows["off"], rows["on_first"], rows["on_recalled"] = off, on[:n], on[n:2 * n]
same = sum(1 for a, b, c in zip(rows["off"], rows["on_first"], rows["on_recalled"]) if a["word"] == b["word"] == c["word"])


def means(sample):
    return {k: (sum(rows[k][i]["k"] for i in sample) / len(sample), sum(rows[k][i]["L_ms"] for i in sample) / len(sample)) for k in rows}


def slope(m):
    xs, ys = [v[1] for v in m.values()], [v[0] for v in m.values()]
    mx, my = sum(xs) / 3, sum(ys) / 3
    den = sum((x - mx) ** 2 for x in xs)
    return 0.0 if den == 0 else sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / den


m = means(range(n))
b = slope(m)
rng = random.Random(4002)
boots = sorted(slope(means([rng.randrange(n) for _ in range(n)])) for _ in range(2000))
res = {"questions": n, "settings": {k: {"k_mean": round(v[0], 3), "L_mean_ms": round(v[1], 1)} for k, v in m.items()},
       "same_word_all_settings": same, "slope_k_per_ms": b, "slope_k_per_100ms": round(100 * b, 5),
       "ci95_k_per_100ms": [round(100 * boots[50], 5), round(100 * boots[1949], 5)],
       "recalled_walks": sum(e.get("recalled_walks", 0) for e in rows["on_recalled"]),
       "F1_fires": boots[1949] < 0, "equivalent_to_zero": abs(100 * boots[50]) < 0.05 and abs(100 * boots[1949]) < 0.05}
json.dump(res, open(OUT, "w"), indent=1)
print(json.dumps(res))
