"""exam - the specialist exam, run on your machine. The same idea as the gate that admitted the 267 specialists in this
release, made portable: a specialist joins your model only if ALL of these hold on its HELD-OUT items (used once).

  1. DOMAIN   your model with the specialist gets more right than without it: gain >= max(3, 2% of n)
  2. NO FALSE YES   it asserts on no more must-decline items than the core alone
  3. FEW WRONG      answered-but-wrong on valid items <= max(1, 2% of n)
  4. STAYS IN LANE  on the core panel (924 general questions already published in the release, with the core's own replies) it takes at most max(5, 1%)
  5. SELF     identity questions ("Who are you?") stay the core's
  6. BUDGET   the specialist's median reply time is within its manifest budget (default 200 ms)

The composition measured is the one the workbench runs: the core first; the specialist only where the core declined for
lack of a reading (never where it answered, never where a check stopped it). A held-out verdict is bound to the SHA-256
of every file in the folder: change a file and the specialist leaves your model until it passes a NEW held-out set (a
held-out set is used once - its hash is logged and refused the second time). Dev exams are free and repeatable.

Panel (panel.json): {"dev": [items], "heldout": [items]}, item = {"q": question, "a": answer, "valid": true|false, "kind": ...}
valid=false marks a must-decline item (false premise, unknowable, out of scope): answering it is a false yes."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import re
import sys
import threading
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
READING_DECLINES = ("act:clarify", "unverified:", "corpus_query", "factoid", "deliberation", "capability:", "arb:", "compose",
                    "family_precedence:low_credit", "verified:", "cube:")
CHECK_DECLINES = ("precision_guard", "same_name_guard", "weight:", "chat:unresolved")
IDENTITY_Q = ["Who are you?", "What are you?", "Are you a human?", "What do you value?", "Are you conscious?"]
MIN_HELDOUT, MIN_DECLINE = 10, 2
_PROGRESS = {}
_LOCK = threading.Lock()


def read_manifest(d):
    try:
        return json.loads((Path(d) / "manifest.json").read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return None


def files_sha(d):
    h = hashlib.sha256()
    for p in sorted(Path(d).rglob("*")):
        if p.is_file() and "__pycache__" not in p.parts and not p.name.startswith(("verdict_", "shared_verdict_", "exam_log"))                 and "files" not in p.relative_to(d).parts[:1] and p.name not in ("credit.json", "probes.json", "registry.json"):
            h.update(p.relative_to(d).as_posix().encode())
            h.update(hashlib.sha256(p.read_bytes()).digest())
    return h.hexdigest()


CHECK = re.compile(r"(^|[>|])(precision_guard:[GQ]\d|same_name_guard|weight:|chat:unresolved)")


def fillable(path):
    """a decline your specialists may fill: the core lacked a reading (did not parse, no admitted record, could not verify
    the reply: precision_guard P-codes). Never a CHECK: a false premise, a private question, a changed sign (G/Q codes),
    a same-name clash, a weight question, an unresolved reference."""
    p = str(path or "")
    return not CHECK.search(p) and (any(k in p for k in READING_DECLINES) or "precision_guard:P" in p)


class Loaded:
    """a local specialist: its organ plus its acceptance rule (the same contract as the release's spec_runtime_v1)"""

    def __init__(self, d):
        d = Path(d)
        m = read_manifest(d)
        if not m:
            raise ValueError("no manifest.json")
        self.id, self.m = m["id"], m
        if str(d) not in sys.path:
            sys.path.insert(0, str(d))
        name = "o7local_%s_%s" % (re.sub(r"\W", "_", m["id"]), files_sha(d)[:8])
        spec = importlib.util.spec_from_file_location(name, d / (m["organ"]["module"] + ".py"))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        self.organ = getattr(mod, m["organ"]["class"])(**dict(m["organ"].get("init", {})))
        self.kinds = set(m["accept"]["kinds"])
        self.declines = set(m["accept"].get("declines_in_domain", []))
        self.ctx = re.compile(m["accept"].get("context_regex", r"(?!x)x"), re.I)

    def reply(self, text, session_id="default"):
        try:
            a = self.organ.answer(text, "%s:%s" % (self.id, session_id))
        except Exception:  # noqa: BLE001 - a crashing organ never costs the turn
            return None
        if not a:
            return None
        k = a.get("kind")
        if k in self.kinds or (k in self.declines and self.ctx.search(str(text))):
            return {"status": a.get("status", "answered"), "path": "specialist:%s>%s" % (self.id, k), "subject": a.get("subject"),
                    "response": a.get("response", ""), "references": [], "provenance": {"kind": "specialist", "specialist": self.id, "move": k}}
        return None


def load_specialist(d):
    return Loaded(d)


def status(d):
    d = Path(d)
    v = d / "verdict_heldout.json"
    if not read_manifest(d):
        return {"state": "broken", "note": "manifest.json is missing or not valid JSON"}
    exp = (read_manifest(d) or {}).get("expires")
    if exp and time.time() > float(exp):
        return {"state": "expired", "note": "a temporary specialist; it expired %s" % time.strftime("%d %b %H:%M", time.localtime(float(exp)))}
    if v.exists():
        verdict = json.loads(v.read_text(encoding="utf-8"))
        if verdict.get("decision") == "ADMIT":
            if verdict.get("files_sha") == files_sha(d):
                return {"state": "admitted", "verdict": verdict}
            return {"state": "changed", "verdict": verdict,
                    "note": "a file changed after its held-out exam, so it is out of your model until it passes a new held-out set"}
        return {"state": "failed", "verdict": verdict, "note": "; ".join(verdict.get("reasons", []))}
    dv = d / "verdict_dev.json"
    return {"state": "draft", "verdict": json.loads(dv.read_text(encoding="utf-8")) if dv.exists() else None}


def progress(sid):
    with _LOCK:
        return dict(_PROGRESS.get(sid, {"state": "idle"}))


def _set(sid, **kw):
    with _LOCK:
        _PROGRESS.setdefault(sid, {}).update(kw)


def _scorer(d, m):
    pm = m.get("panel", {})
    mod_name = pm.get("scorer_module", "scorer")
    spec = importlib.util.spec_from_file_location("o7score_%s_%d" % (re.sub(r"\W", "_", m["id"]), time.time_ns()), Path(d) / (mod_name + ".py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return getattr(mod, pm.get("scorer_fn", "ok"))


def run(d, split, eng):
    d = Path(d)
    m = read_manifest(d)
    sid = m["id"]
    panel = json.loads((d / m.get("panel", {}).get("path", "panel.json")).read_text(encoding="utf-8"))
    items = panel.get(split) or []
    reasons = []
    log = d / "exam_log.jsonl"
    psha = hashlib.sha256(json.dumps(items, sort_keys=True).encode()).hexdigest()
    if split == "heldout":
        used = [json.loads(x) for x in log.read_text(encoding="utf-8").splitlines()] if log.exists() else []
        if any(u.get("heldout_sha") == psha for u in used):
            raise ValueError("this held-out set was already used once; write new held-out items for a new exam")
        if len(items) < MIN_HELDOUT or sum(1 for it in items if not it.get("valid", True)) < MIN_DECLINE:
            raise ValueError("a held-out set needs at least %d items, %d of them must-decline (valid: false)" % (MIN_HELDOUT, MIN_DECLINE))
        with open(log, "a", encoding="utf-8") as fh:            # logged BEFORE it runs: a crash still spends it
            fh.write(json.dumps({"t": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "heldout_sha": psha, "files_sha": files_sha(d)}) + "\n")
    sp = Loaded(d)
    scorer = _scorer(d, m)
    core = json.loads((HERE / "data" / "core_panel.json").read_text(encoding="utf-8"))["items"]
    total = len(items) + len(core) + len(IDENTITY_Q)
    _set(sid, state="running", split=split, phase="domain", done=0, total=total, result=None, error=None)
    head = {"ok": 0, "fy": 0, "wrong": 0}
    comp = {"ok": 0, "fy": 0, "wrong": 0}
    fails, lat = [], []
    for i, it in enumerate(items):
        r = eng.chat(it["q"], session_id="exam-%s-%s-%d-%d" % (sid, split, int(time.time()), i))
        c = r
        if r.get("status") != "answered" and fillable(r.get("path")):
            t0 = time.perf_counter()
            a = sp.reply(it["q"], "exam-%d" % i)
            lat.append(1000 * (time.perf_counter() - t0))
            if a is not None:
                c = a
        for tag, rep, acc in (("head", r, head), ("comp", c, comp)):
            good, asserted = scorer(it, rep)
            acc["ok"] += int(bool(good))
            if not it.get("valid", True) and asserted:
                acc["fy"] += 1
            if it.get("valid", True) and asserted and not good:
                acc["wrong"] += 1
            if tag == "comp" and not good and len(fails) < 12:
                fails.append({"q": it["q"][:160], "expected": str(it.get("a", "(decline)"))[:80], "got": str(rep.get("response", ""))[:160],
                              "status": rep.get("status"), "by": "yours" if rep is not r else "core"})
        _set(sid, done=i + 1)
    n = len(items)
    need = max(3, math.ceil(0.02 * n))
    if comp["ok"] - head["ok"] < need:
        reasons.append("DOMAIN: gain %d, needs %d" % (comp["ok"] - head["ok"], need))
    if comp["fy"] > head["fy"]:
        reasons.append("FALSE YES: %d with it vs %d without" % (comp["fy"], head["fy"]))
    if comp["wrong"] > max(1, math.floor(0.02 * n)):
        reasons.append("WRONG: %d answered wrong, cap %d" % (comp["wrong"], max(1, math.floor(0.02 * n))))
    _set(sid, phase="core panel")
    taken = []
    for j, c in enumerate(core):
        t0 = time.perf_counter()
        a = sp.reply(c["q"], "core-%d" % j)
        lat.append(1000 * (time.perf_counter() - t0))
        if a is not None and (c.get("status") != "answered" and fillable(c.get("path"))):
            taken.append(c["q"][:140])
        _set(sid, done=n + j + 1)
    cap = max(5, len(core) // 100)
    if len(taken) > cap:
        reasons.append("LANE: takes %d general questions, cap %d" % (len(taken), cap))
    _set(sid, phase="self")
    selfs = [q for q in IDENTITY_Q if sp.reply(q, "self") is not None]
    if selfs:
        reasons.append("SELF: it answers identity questions (%s)" % ", ".join(selfs))
    lat.sort()
    p50 = round(lat[len(lat) // 2], 2) if lat else 0.0
    budget = float(m.get("budgets", {}).get("latency_p50_ms", 200))
    if p50 > budget:
        reasons.append("BUDGET: median %.1f ms, budget %.0f ms" % (p50, budget))
    verdict = {"id": sid, "split": split, "decision": "ADMIT" if not reasons else ("PASS" if split == "dev" else "NEGATIVE"),
               "reasons": reasons, "n": n, "head": head, "with_specialist": comp, "gain_needed": need,
               "core": {"n": len(core), "taken": len(taken), "cap": cap, "examples": taken[:8]}, "self_ok": not selfs,
               "p50_ms": p50, "budget_ms": budget, "fails": fails, "files_sha": files_sha(d), "panel_sha": psha,
               "time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "core_head": eng.tip}
    if split == "dev":                                   # a dev exam never admits; it says how the held-out exam would go
        verdict["decision"] = "WOULD FAIL" if reasons else "WOULD PASS"
    if split == "heldout":
        old = d / "verdict_heldout.json"
        if old.exists():
            old.rename(d / ("verdict_heldout_%s.json" % time.strftime("%Y%m%dT%H%M%S")))
    (d / ("verdict_%s.json" % split)).write_text(json.dumps(verdict, indent=1), encoding="utf-8")
    return verdict


def start(d, split, eng, on_done=None):
    sid = Path(d).name
    if progress(sid).get("state") == "running":
        return

    def go():
        try:
            v = run(d, split, eng)
            _set(sid, state="done", result=v)
        except Exception as e:  # noqa: BLE001
            _set(sid, state="error", error="%s: %s" % (type(e).__name__, e))
        if on_done:
            on_done()
    _set(sid, state="running", split=split, phase="loading", done=0, total=1, result=None, error=None)
    threading.Thread(target=go, daemon=True).start()


# ---------------------------------------------------------------- source readers (made by Scan / Connect / Add files)
def make_source(specs_dir, sid, name, organ_class, init, words):
    """write a source reader's folder: manifest + a one-line organ module that uses the Workbench's sources.py"""
    d = Path(specs_dir) / sid
    d.mkdir(parents=True, exist_ok=True)
    (d / "files").mkdir(exist_ok=True) if organ_class == "FilesOrgan" else None
    mod = "organ_" + sid.replace("-", "_")
    pkg, cls = organ_class.split(".") if "." in organ_class else ("sources", organ_class)
    (d / (mod + ".py")).write_text('"""%s - a source reader made by the Workbench. It reads its source at question time and names '
                                   'where every value came from."""\nfrom %s import %s as Organ  # noqa: F401\n' % (name, pkg, cls),
                                   encoding="utf-8")
    m = {"id": sid, "name": name, "source": True, "sources": [{"name": name, "licence": "yours", "url": ""}],
         "organ": {"module": mod, "class": "Organ", "init": init},
         "accept": {"kinds": ["reading", "from_file", "tool_result", "recalled"], "declines_in_domain": ["unreadable", "not_in_files", "underspecified"],
                    "context_regex": r"\b(?:%s)\b" % "|".join(re.escape(w) for w in words)},
         "budgets": {"latency_p50_ms": 15000 if pkg == "mcp" else 3000 if init.get("target") == "server" else 300}}
    (d / "manifest.json").write_text(json.dumps(m, indent=1), encoding="utf-8")
    return d


def run_source(d, probes):
    """the automatic check of a source reader. probes = [(question, expected substring or None)] made from the source:
    it must answer each with the value its source holds (or decline cleanly when expected is None), stay in its lane on the
    core panel, leave identity questions alone and answer within budget. Repeatable: the source changes, so it re-checks."""
    d = Path(d)
    m = read_manifest(d)
    sid = m["id"]
    sp = Loaded(d)
    core = json.loads((HERE / "data" / "core_panel.json").read_text(encoding="utf-8"))["items"]
    _set(sid, state="running", split="source", phase="reading its source", done=0, total=len(probes) + len(core), result=None, error=None)
    reasons, fails, lat, right = [], [], [], 0
    for i, (q, want) in enumerate(probes):
        t0 = time.perf_counter()
        a = sp.reply(q, "probe-%d" % i)
        lat.append(1000 * (time.perf_counter() - t0))
        ok = (a is not None and a.get("status") == "answered" and want is not None and want.lower() in str(a.get("response", "")).lower()) or \
             (want is None and (a is None or a.get("status") != "answered"))
        right += ok
        if not ok and len(fails) < 12:
            fails.append({"q": q, "expected": want or "(no answer)", "got": str((a or {}).get("response", "(not taken)"))[:160], "status": (a or {}).get("status"), "by": "yours"})
        _set(sid, done=i + 1)
    if probes and right < len(probes):
        reasons.append("SOURCE: read %d of %d probes back correctly" % (right, len(probes)))
    _set(sid, phase="core panel")
    taken = []
    takes = getattr(sp.organ, "takes", None)                  # routing only: no tool is called for the lane check
    for j, c in enumerate(core):
        took = takes(c["q"]) if takes else sp.reply(c["q"], "core-%d" % j) is not None
        if took:
            taken.append(c["q"][:140])
        _set(sid, done=len(probes) + j + 1)
    cap = max(5, len(core) // 100)
    if len(taken) > cap:
        reasons.append("LANE: takes %d general questions, cap %d" % (len(taken), cap))
    selfs = [q for q in IDENTITY_Q if (takes(q) if takes else sp.reply(q, "self") is not None)]
    if selfs:
        reasons.append("SELF: it answers identity questions")
    lat.sort()
    p50 = round(lat[len(lat) // 2], 2) if lat else 0.0
    budget = float(m.get("budgets", {}).get("latency_p50_ms", 300))
    if p50 > budget:
        reasons.append("BUDGET: median %.1f ms, budget %.0f ms" % (p50, budget))
    n = len(probes)
    verdict = {"id": sid, "split": "source", "decision": "ADMIT" if not reasons else "NEGATIVE", "reasons": reasons, "n": n,
               "head": {"ok": 0, "fy": 0, "wrong": 0}, "with_specialist": {"ok": right, "fy": 0, "wrong": n - right}, "gain_needed": 0,
               "core": {"n": len(core), "taken": len(taken), "cap": cap, "examples": taken[:8]}, "self_ok": not selfs,
               "p50_ms": p50, "budget_ms": budget, "fails": fails, "files_sha": files_sha(d), "panel_sha": "",
               "time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "core_head": "", "source_reader": True}
    (d / "verdict_heldout.json").write_text(json.dumps(verdict, indent=1), encoding="utf-8")
    return verdict


def start_source(d, probes=None, on_done=None):
    sid = Path(d).name
    pf = Path(d) / "probes.json"
    if probes is None:                                   # a re-check (after you mark answers) uses the probes it was made with
        probes = [tuple(x) for x in json.loads(pf.read_text(encoding="utf-8"))] if pf.exists() else []
    else:
        pf.write_text(json.dumps(probes), encoding="utf-8")

    def go():
        try:
            _set(sid, state="done", result=run_source(d, probes))
        except Exception as e:  # noqa: BLE001
            _set(sid, state="error", error="%s: %s" % (type(e).__name__, e))
        if on_done:
            on_done()
    _set(sid, state="running", split="source", phase="loading", done=0, total=1, result=None, error=None)
    threading.Thread(target=go, daemon=True).start()
