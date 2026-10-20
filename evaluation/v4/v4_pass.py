"""v4_pass.py <pass 1-4> <out.json> - one INDUCTION PASS of Oracle7 4.0 (build brief: I5, F2; phase 4).
A pass = development questions (a fixed quarter of the 2,249 questions sealed tests 10-24 asked - all spent; never PI4-A/B)
through the admitted 4.0 head with the ledger's text on; every turn that did not answer becomes residue, which is handed to
3.2's own improvement loop through the input it already reads (/opt/oracle-clm/residue_turns.jsonl: {ts, s, text, path,
status}; s = "v4pass<p>"), grouped by the Tree node where each stopped (the residue's type). Then one hour of the loop's
normal work: the worker authors candidates (fold_authored), the gate admits or rejects them. Counted in that window:
proposals, admissions, rejections. Nothing in the loop is changed by the pass."""
import calendar
import json
import os
import re
import sys
import time

P, OUT = int(sys.argv[1]), sys.argv[2]
WINDOW = int(os.environ.get("V4_PASS_WINDOW_S", "3600"))
LOOP = "/opt/oracle-clm/fable-content/oracle-m-series-2026-08-15/self_loop"
RESIDUE = "/opt/oracle-clm/residue_turns.jsonl"
os.environ["ORACLE7_V4_LEDGER"] = OUT + ".ledger.jsonl"
os.environ["ORACLE7_V4_LEDGER_TEXT"] = "1"
sys.path.insert(0, LOOP + "/admitted")
sys.path.insert(0, "/opt/oracle-clm/wander-train")
import importlib  # noqa: E402

tip = json.load(open(LOOP + "/admitted/HEAD_MANIFEST.json"))["tip"]
chain = json.load(open(LOOP + "/admitted/HEAD_MANIFEST.json"))["chain_tip_to_base"]
assert "oracle_release_runtime_w557" in chain, "4.0 (w557) is not admitted"
mod = importlib.import_module(tip)
R = [getattr(mod, n) for n in dir(mod) if n.startswith("OracleReleaseRuntime")][-1]()
qs = sorted(json.load(open("/root/w240/sealed_prior_questions_24.json")))
qs = [q for i, q in enumerate(qs) if i % 4 == P - 1][:150]
t0 = time.time()
for i, q in enumerate(qs):
    R.chat(q, "v4pass%d-%d" % (P, i))
led = [json.loads(l) for l in open(OUT + ".ledger.jsonl", encoding="utf-8")]
res_rows = sorted((e for e in led if e.get("rho")), key=lambda e: (e["rho"]["stopped_at"], e["k"]))
with open(RESIDUE, "a", encoding="utf-8") as f:
    for e in res_rows:
        f.write(json.dumps({"ts": int(time.time()), "s": "v4pass%d" % P, "text": e.get("text", ""), "path": e["route"],
                            "status": e["status"], "v4": {"stopped_at": e["rho"]["stopped_at"], "prefix": e["rho"]["prefix"]}}) + "\n")

# MUNDANE RULE PROPOSALS (Ben 2026-10-19: "make sure new rule proposal is mundane" - routine every pass, each one small).
# The typed residue is clustered by (where on the Tree it stopped, why, the question's form with numbers and names masked).
# A cluster of 3 or more is ONE proposal: one form, one gap - never a sweeping change. Declines that are right (the question is
# the problem: a precision-guard Q rule; a private question) propose nothing. Each proposal's members go to the loop's own
# human-gap queue, which the worker already reads; the worker authors (or not) and the gate decides, as for any gap.
CURRIC = "/opt/oracle-clm/fable-content/oracle-m-series-2026-08-15/harness_curriculum_queue_v1.jsonl"
NAME = re.compile(r"(?<!^)(?<![.?!]\s)\b[A-Z][\w'’.-]*(?:\s+(?:of|the|de|la|von|van|and)?\s*[A-Z][\w'’.-]*)*")


def form_of(text):
    t = NAME.sub("NAME", " ".join(str(text).split()))
    t = re.sub(r"-?\d[\d,]*(?:\.\d+)?", "#", t)
    return t.lower().replace("name", "NAME")


def right_decline(reason):
    r = str(reason)
    return r.startswith("precision_guard:Q") or "P7_private" in r or r.startswith("chat:")


clusters = {}
for e in res_rows:
    if right_decline(e["rho"]["reason"]) or not e.get("text"):
        continue
    key = (e["rho"]["stopped_at"], e["rho"]["reason"].split(">")[0].split("|")[0][:60], form_of(e["text"]))
    clusters.setdefault(key, []).append(e["text"])
proposals = []
with open(CURRIC, "a", encoding="utf-8") as f:
    for (node, reason, form), members in sorted(clusters.items(), key=lambda kv: -len(kv[1])):
        if len(set(members)) < 3:
            continue
        pid = "v4p%d-%d" % (P, len(proposals) + 1)
        proposals.append({"id": pid, "form": form, "stopped_at": node, "reason": reason, "members": len(set(members)),
                          "proposal": "questions of the form '%s' stop at %s (%s); answer this one form, nothing wider" % (form, node, reason)})
        for m in sorted(set(members))[:8]:
            f.write(json.dumps({"ts": int(time.time()), "who": "v4ledger:%s" % pid, "kind": "typed_residue", "label": m[:160]}) + "\n")
handed = time.time()
time.sleep(WINDOW)


def window(path, ev):
    out = []
    for l in open(path, encoding="utf-8"):
        try:
            e = json.loads(l)
        except Exception:  # noqa: BLE001
            continue
        if e.get("event") != ev:
            continue
        ts = e.get("ts")
        try:
            t = calendar.timegm(time.strptime(ts, "%Y-%m-%dT%H:%M:%SZ")) if isinstance(ts, str) else float(ts)
        except Exception:  # noqa: BLE001
            continue
        if handed <= t <= handed + WINDOW + 600:
            out.append(e)
    return out


authored = window(LOOP + "/worker_ledger.jsonl", "fold_authored")
gates = window(LOOP + "/ledger.jsonl", "gate")
mine = {"oracle_release_runtime_w556.py", "oracle_release_runtime_w557.py"}
gates = [g for g in gates if str(g.get("candidate", "")) not in mine]
by_node = {}
for e in res_rows:
    by_node[e["rho"]["stopped_at"]] = by_node.get(e["rho"]["stopped_at"], 0) + 1
res = {"pass": P, "head": tip, "questions": len(qs), "residue_handed": len(res_rows), "residue_by_node": by_node,
       "typed_proposals": len(proposals), "proposals": proposals,
       "window_s": WINDOW, "proposed": len(authored), "admitted": sum(1 for g in gates if g.get("decision") == "ADMIT"),
       "rejected": sum(1 for g in gates if g.get("decision") == "REJECT"),
       "admitted_names": [g.get("candidate") for g in gates if g.get("decision") == "ADMIT"], "run_s": round(handed - t0)}
json.dump(res, open(OUT, "w"), indent=1)
print(json.dumps(res))
