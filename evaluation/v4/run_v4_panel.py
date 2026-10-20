"""run_v4_panel - run ONE arm on ONE sealed V4 panel, once (build brief: "Panels and statistics").
usage: run_v4_panel.py <pi4a|pi4b> <arm> <out.json>
  arm = "3.2"            full 3.2 head + the 4.0 instrument, no law (v4_arm32.OracleV32Instrumented), on Box C's runtime
        "4.0"            the 4.0 law fold (w557) on Box C's runtime
        "release"        the relocated release in the current directory (oracle7.load(), as the sealed tests run it)
For the release arm it runs from /root/rc_harness (a clean folder: a script's own folder is first on sys.path, and /root/w240
holds working copies of folds). The panel must match its sealed hash (pi4.sha256) and the output must not exist: a panel runs once per arm. Scoring = the
sealed tests' rules (run_sealed24.py), unchanged; follow-up pairs share a session. The arm's ledger (k, L, word, rho) is
written to <out>.ledger.jsonl and summarised: mean/median k and L, residue by stopping node, re-entrance against the shuffled
baseline (v4_law.reentry), and for each recurring pair whether both turns spelled the same word."""
import hashlib
import json
import os
import re
import statistics
import sys
import time

PANEL, ARM, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
W240 = "/root/w240"
SHAS = dict(reversed(l.split()) for l in open(os.path.join(W240, "pi4.sha256")))
src = os.path.join(W240, PANEL + ".json")
if hashlib.sha256(open(src, "rb").read()).hexdigest() != SHAS[PANEL + ".json"]:
    sys.exit("%s does not match its sealed hash; refusing" % src)
if os.path.exists(OUT):
    sys.exit("%s exists: a V4 panel runs once per arm" % OUT)
LEDGER = OUT + ".ledger.jsonl"
os.environ["ORACLE7_V4_LEDGER"] = LEDGER
os.environ["ORACLE7_V4_LEDGER_TEXT"] = "1"
import importlib.util  # noqa: E402

_spec = importlib.util.spec_from_file_location("v4_law_runner", os.path.join(os.path.dirname(os.path.abspath(__file__)), "v4_law.py"))
_v4 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_v4)
reentry = _v4.reentry
# /root/w240 holds working copies of folds: it goes on sys.path only for the runtime arms, never ahead of a release

if ARM in ("3.2", "4.0"):
    sys.path.insert(0, W240)
    sys.path.insert(0, "/opt/oracle-clm/fable-content/oracle-m-series-2026-08-15/self_loop/admitted")
    sys.path.insert(0, "/opt/oracle-clm/wander-train")
    if ARM == "3.2":
        from v4_arm32 import OracleV32Instrumented as C
    else:
        from oracle_release_runtime_w557 import OracleReleaseRuntimeW557 as C
    rt, tip = C(), ARM
else:
    sys.path.insert(0, os.getcwd())                # the release folder, as run_sealed24 loads it
    import oracle7  # noqa: E402
    tip, rt = oracle7.load()

NUM = re.compile(r"(?<![\w.])[-+]?(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?(?:[eE][-+]?\d+|\s*[×x]\s*10\^?\s*[-+]?\d+)?")
NO_ENTRY = re.compile(r"^\s*(?:\[ev:[a-z_]+\]\s*)?I have no admitted (?:entry|record)", re.I)
RESTATE = re.compile(r"^\s*(?:\[ev:[a-z_]+\]\s*)?(?:a |one )?1 [a-zA-Z][a-zA-Z .]{0,30}? (?:is|are|=|equals)\s", re.I)


def _num(tok):
    s = tok.replace(",", "").replace(" ", "")
    mm = re.match(r"([-+]?[\d.]+)[×x]10\^?([-+]?\d+)$", s)
    return float(mm.group(1)) * 10 ** int(mm.group(2)) if mm else float(s)


def first_number(text, givens=()):
    text = RESTATE.sub("", text, count=1)
    for m in NUM.finditer(text):
        x = _num(m.group(0))
        if not any(abs(x - g) <= 1e-9 * max(abs(g), 1) for g in givens):
            return x
    return None


items = json.load(open(src, encoding="utf-8"))
w = rt.chat("What is the capital of Peru?", session_id="v4-preflight")
print("preflight:", str(w.get("path"))[:60], flush=True)
open(LEDGER, "w").close()                                 # the preflight turn is not part of the run
res = {"panel": PANEL, "arm": ARM, "tip": tip, "sha256": SHAS[PANEL + ".json"], "started": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "items": []}
tot, by = {"right": 0, "wrong": 0, "declined": 0, "false_yes": 0}, {}
def session_of(it):
    """follow-up pairs share ONE session, as the panels' pre-registered design says (v4_panels.py: "a follow-up pair shares one").
    The generator wrote "<panel>-followup1-<pair>" and "<panel>-followup2-<pair>" - two sessions, so on PI4-A every follow-up
    arrived with no conversation before it (both arms; found 2026-10-19 after PI4-A ran). Fixed here in the runner, before
    PI4-B ran on any arm; the sealed panel file and its hash are unchanged."""
    if str(it.get("group", "")).startswith("followup"):
        return "%s-followup-%s" % (PANEL, it.get("pair"))
    return it["session"]


for it in items:
    r = rt.chat(it["q"], session_id=session_of(it))
    reply = " ".join(str(r.get("response", "")).split())
    answered = r.get("status") == "answered" and not NO_ENTRY.match(reply)
    if it["kind"] == "decline":
        v = "false_yes" if answered else "right"
    elif not answered:
        v = "declined"
    elif it["kind"] == "number":
        givens = [_num(t.group(0)) for t in NUM.finditer(it["q"]) if not re.match(r"[a-zA-Z]", it["q"][t.end():t.end() + 1])]
        x = first_number(reply, givens)
        v = "right" if x is not None and abs(x - it["expect"]) <= it["tol"] * max(abs(it["expect"]), 1e-12) else "wrong"
    else:
        v = "right" if any(a.lower() in reply.lower() for a in it["expect"]) else "wrong"
    tot[v] += 1
    if v == "false_yes":
        tot["wrong"] += 1
    g = by.setdefault(it["group"], {"right": 0, "wrong": 0, "declined": 0, "false_yes": 0})
    g[v] += 1
    res["items"].append({"q": it["q"], "group": it["group"], "session": session_of(it), "pair": it.get("pair"), "turn": it.get("turn"),
                         "verdict": v, "status": r.get("status"), "path": str(r.get("path"))[:160], "reply": reply[:300]})
ledger = [json.loads(l) for l in open(LEDGER, encoding="utf-8")]
assert len(ledger) == len(items), "ledger has %d entries for %d turns" % (len(ledger), len(items))
for x, e in zip(res["items"], ledger):
    x.update(k=e["k"], L_ms=e["L_ms"], word=e["word"], measured=e["measured"], discourse_record=bool(e.get("discourse_record")),
             recalled=e.get("recalled_walks", 0))
ks, Ls = [e["k"] for e in ledger], [e["L_ms"] for e in ledger]
rho = {}
for e in ledger:
    if e.get("rho"):
        rho[e["rho"]["stopped_at"]] = rho.get(e["rho"]["stopped_at"], 0) + 1
rec = {}
for x in res["items"]:
    if x["group"] == "recurring":
        rec.setdefault(x["pair"], []).append(x["word"])
valid = [x for x in res["items"] if x["group"] != "decline"]
va = [x for x in valid if x["verdict"] in ("right", "wrong")]
res.update({
    "totals": tot, "by_group": by,
    "precision_on_answered": round(sum(x["verdict"] == "right" for x in va) / max(1, len(va)), 4),
    "followup2_right": by.get("followup2", {}).get("right", 0), "followup2_wrong": by.get("followup2", {}).get("wrong", 0),
    "k_mean": round(statistics.mean(ks), 3), "k_median": statistics.median(ks), "L_mean_ms": round(statistics.mean(Ls), 1),
    "L_median_ms": statistics.median(Ls), "residue": {"entries": sum(1 for e in ledger if e.get("rho")), "by_stopping_node": rho},
    "discourse_records": sum(1 for e in ledger if e.get("discourse_record")), "recalled_walks": sum(e.get("recalled_walks", 0) for e in ledger),
    "recurring_same_word": sum(1 for v in rec.values() if len(v) == 2 and v[0] == v[1]), "recurring_pairs": len(rec),
    "reentry": reentry(ledger), "ledger_chain_ok": all(ledger[i]["prev"] == ledger[i - 1]["h"] for i in range(1, len(ledger))),
    "bars": {"precision>=0.90": None, "false_yes": tot["false_yes"]},
})
res["bars"]["precision>=0.90"] = res["precision_on_answered"] >= 0.90
json.dump(res, open(OUT, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print(PANEL, ARM, json.dumps(tot), "precision", res["precision_on_answered"], "k_mean", res["k_mean"], "L_median", res["L_median_ms"],
      "residue", res["residue"]["entries"], "reentry", res["reentry"]["rate"], "vs shuffled", res["reentry"]["shuffled_rate"], flush=True)
