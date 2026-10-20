#!/usr/bin/env python3
"""oracle_release_runtime_w557 - ORACLE7 4.0 THE LAW (built from Ben's invocation; build brief: Claude Doc "Oracle7 V4.0 - Build
Brief"). Submitted as a CORRECTNESS RELEASE: by design it adds no capability the gate's columns can see (its claims are tested
on the two sealed V4 panels), so it is exempt from no_gain only; every measured column must still hold.

Three parts, one fold, so the law is admitted whole:

1. THE INSTRUMENT (I4, and the logs for I3, I5, I6). Every turn, BEFORE its reply is returned, appends one entry to the residue
   ledger: k = the Tree edges its path walks; L = wall-clock ms; word = the path spelled over LAMBDA, the twenty-two paths of
   the three-tree runtime (oracle_tritree_v1.TREE_OF_LIFE) - a logged operator sequence is rejoined by the shortest edge path
   between operator nodes, since the runtime passes through a node whose operator does not apply without logging it (its
   TRANSIT rule); routes that do not walk the Tree are spelled by ROUTE_SPELLING (measured = false, an interpretation recorded
   as such); rho = for a turn that did not answer, the node where formation stopped, the prefix reached and the reason.
   Append-only and hash-chained. PRIVACY: the question is stored as its sha256 only; its text only when the operator sets
   ORACLE7_V4_LEDGER_TEXT=1 (research box, gate panels; never the public demo). Ledger: $ORACLE7_V4_LEDGER, else
   $ORACLE7_STATE/v4_ledger.jsonl, else /tmp/oracle7-v4/v4_ledger.jsonl. A failed write never costs the turn.

2. NON-IDENTITY (I1, from P1: "never has become ... it becomes"). An ANSWERED reply that has nothing under it - no citation,
   no proof, no checked computation, no specialist - does not become conversation state: the session's state (dialogue,
   transitions, pending conversions) is put back as it was before the turn, and the reply is entered in the ledger as a
   discourse record. A later turn can then use it only by re-entering it as cited evidence. Declined and withheld turns keep
   their state (there is no answer in them to carry, and "why not?" must still explain the decline); acts, which are
   conversions over the previous answer, are untouched.

3. WALK RECALL (P3, from "go faster and faster, but slower in states"). The three-tree runtime's answer(q) is a pure function
   of the question and the stores, holding no session state. A walk already made is recalled, not walked again: the same
   result, the same path, the same step count, less wall-clock. Bounded (2,048 walks per instance), per process, on every
   TriTree instance the chain has made (an instance attribute; no module state of any fold is changed). And a specialist's
   own-module test (combo_runtime_v1._Organ._own, about a quarter of a relation turn's time: the family rescans every
   loaded module after a call, one abspath each) is recalled per file on each loaded specialist - the same answer, never
   recomputed. The frozen files are untouched; only instances get the recall.

Every reply is the parent's (w556) except where part 2 restores state; part 1 and part 3 change no reply."""
from __future__ import annotations

import copy
import hashlib
import json
import os
import re
import threading
import time
from collections import OrderedDict, deque

from oracle_release_runtime_w556 import OracleReleaseRuntimeW556 as _Base

SEPH = ["keter", "chokmah", "binah", "chesed", "geburah", "tiferet", "netzach", "hod", "yesod", "malkuth"]
EDGES = [("keter", "chokmah"), ("keter", "binah"), ("keter", "tiferet"), ("chokmah", "binah"), ("chokmah", "tiferet"),
         ("chokmah", "chesed"), ("binah", "tiferet"), ("binah", "geburah"), ("chesed", "geburah"),
         ("chesed", "tiferet"), ("chesed", "netzach"), ("geburah", "tiferet"), ("geburah", "hod"),
         ("tiferet", "netzach"), ("tiferet", "yesod"), ("tiferet", "hod"), ("netzach", "hod"), ("netzach", "yesod"),
         ("netzach", "malkuth"), ("hod", "yesod"), ("hod", "malkuth"), ("yesod", "malkuth")]
NODE_OF = {"READ": "malkuth", "FRAME": "yesod", "LINK": "chokmah", "RELATE": "binah", "EXPAND": "chesed", "CHECK": "geburah",
           "BIND": "tiferet", "COMPARE": "netzach", "COMPUTE": "hod", "VERIFY": "keter"}
OPS = re.compile(r"(?<![A-Za-z])(READ|FRAME|LINK|RELATE|EXPAND|CHECK|BIND|COMPARE|COMPUTE|VERIFY)(?![a-z])|"
                 r"(?<![A-Za-z])(read|frame|link|relate|expand|check|bind|compare|compute|verify)(?=>|$)")
ROUTE_SPELLING = [
    ("precision_guard:Q", ["READ", "FRAME", "CHECK"]), ("precision_guard", ["READ", "FRAME", "LINK", "CHECK"]),
    ("evidence_guard", ["READ", "FRAME", "LINK", "RELATE", "CHECK"]), ("reader_guard", ["READ", "FRAME", "LINK", "CHECK"]),
    ("owner_first", ["READ", "FRAME", "LINK", "COMPUTE", "CHECK", "BIND", "VERIFY"]),
    ("network", ["READ", "FRAME", "COMPUTE", "BIND", "CHECK", "VERIFY"]),
    ("specialist_call", ["READ", "FRAME", "COMPUTE", "BIND", "VERIFY"]), ("specialist_after_guard", ["READ", "FRAME", "COMPUTE", "BIND", "VERIFY"]),
    ("family_precedence", ["READ", "FRAME", "LINK", "COMPUTE", "BIND", "VERIFY"]),
    ("compute:", ["READ", "FRAME", "COMPUTE", "CHECK", "VERIFY"]), ("organ:math", ["READ", "FRAME", "COMPUTE", "CHECK", "VERIFY"]),
    ("op:", ["READ", "FRAME", "COMPUTE", "VERIFY"]), ("verified:", ["READ", "FRAME", "LINK", "RELATE", "CHECK", "VERIFY"]),
    ("factoid", ["READ", "FRAME", "LINK", "RELATE", "CHECK"]), ("unverified", ["READ", "FRAME", "LINK", "RELATE", "CHECK"]),
    ("capability:", ["READ", "FRAME", "LINK", "EXPAND", "BIND", "VERIFY"]), ("arb:", ["READ", "FRAME", "LINK", "EXPAND", "BIND"]),
    ("act:", ["READ", "FRAME", "BIND"]), ("chat:", ["READ", "FRAME"]),
]
# what an answer may stand on and still become state: a citation or source tag, a proof, or a checked route
CITED = re.compile(r"\[[^\]\s]{2,}\]")
CHECKED = ("specialist_call", "specialist_after_guard", "owner_first", "family_precedence", "network", "compute:", "organ:math",
           "op:", "verified:", "algebra:", "deduce:")
SESSION_STORES = ("dialogue", "transitions", "_pending_conversion")
_ADJ = {s: [] for s in SEPH}
for _i, (_a, _b) in enumerate(EDGES):
    _ADJ[_a].append((_b, _i))
    _ADJ[_b].append((_a, _i))
_LOCK = threading.Lock()
_S: dict = {}


def shortest(a, b):
    """the shortest edge path a -> b as [(node, edge index)], ties broken by edge order (deterministic)"""
    if a == b:
        return []
    prev, q = {a: None}, deque([a])
    while q:
        u = q.popleft()
        for v, e in sorted(_ADJ[u], key=lambda x: x[1]):
            if v not in prev:
                prev[v] = (u, e)
                if v == b:
                    q.clear()
                    break
                q.append(v)
    out, n = [], b
    while prev[n] is not None:
        u, e = prev[n]
        out.append((n, e))
        n = u
    return out[::-1]


def ops_of(path):
    """(operators in order, measured) - the Tree operators a path logged, or the route's spelling"""
    p = str(path or "")
    ops = [(m.group(1) or m.group(2)).upper() for m in OPS.finditer(p)]
    if len(ops) >= 2:
        return ops, True
    for prefix, spelled in ROUTE_SPELLING:
        if p.startswith(prefix):
            return list(spelled), False
    return ["READ", "FRAME"], False


def spell(ops):
    """(nodes walked, LAMBDA word as edge indices): from Malkuth through each operator's node by shortest edge paths"""
    nodes, word, cur = ["malkuth"], [], "malkuth"
    for op in ops:
        tgt = NODE_OF.get(op)
        if not tgt or (tgt == cur and op == "READ"):
            continue
        for n, e in shortest(cur, tgt):
            nodes.append(n)
            word.append(e)
        cur = tgt
    return nodes, word


def stands_on_something(r):
    if r.get("proved"):
        return True
    path = str(r.get("path", ""))
    return path.startswith(CHECKED) or bool(CITED.search(str(r.get("response", ""))))


def _ledger_path():
    p = os.environ.get("ORACLE7_V4_LEDGER")
    if p:
        return p
    return os.path.join(os.environ.get("ORACLE7_STATE") or "/tmp/oracle7-v4", "v4_ledger.jsonl")


def ledger_append(entry):
    with _LOCK:
        p = _ledger_path()
        if _S.get("path") != p:
            _S["path"], _S["prev"] = p, "0" * 64
            try:
                with open(p, "rb") as f:
                    f.seek(0, 2)
                    f.seek(max(0, f.tell() - 65536))
                    last = f.read().splitlines()[-1]
                _S["prev"] = json.loads(last)["h"]
            except Exception:  # noqa: BLE001 - a new or unreadable ledger starts a new chain
                pass
        entry["prev"] = _S["prev"]
        entry["h"] = hashlib.sha256(json.dumps(entry, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
        os.makedirs(os.path.dirname(p) or ".", exist_ok=True)
        with open(p, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, sort_keys=True, ensure_ascii=False) + "\n")
        _S["prev"] = entry["h"]


def ledger_entry(text, session_id, r, L, law, extra=None):
    path = str(r.get("path", "")) if isinstance(r, dict) else ""
    status = r.get("status") if isinstance(r, dict) else None
    ops, measured = ops_of(path)
    nodes, word = spell(ops)
    e = {"t": round(time.time(), 3), "law": law, "session": hashlib.sha256(str(session_id).encode()).hexdigest()[:16],
         "input": hashlib.sha256(str(text or "").encode()).hexdigest(), "status": status, "route": path.split(">")[0][:60],
         "measured": measured, "ops": ops, "nodes": nodes, "word": word, "k": len(word), "L_ms": L}
    if os.environ.get("ORACLE7_V4_LEDGER_TEXT") == "1":
        e["text"] = str(text or "")[:500]
    if status != "answered":
        e["rho"] = {"stopped_at": nodes[-1], "prefix": word, "reason": path.split(">")[0][:80] or str(status)}
    if extra:
        e.update(extra)
    return e


class _WalkRecall:
    """a bounded memo over one TriTree instance's answer(q, form_props, only): same result, its why and expanded restored"""

    def __init__(self, tt, size=2048):
        self.tt, self.fn, self.size, self.memo, self.hits, self.lock = tt, tt.answer, size, OrderedDict(), 0, threading.Lock()

    def __call__(self, q, form_props=None, only=False):
        key = (str(q), tuple(sorted(form_props)) if form_props else None, bool(only))
        with self.lock:
            if key in self.memo:
                self.memo.move_to_end(key)
                res, why, expanded = self.memo[key]
                self.hits += 1
                self.tt.why, self.tt.expanded = why, expanded
                return copy.deepcopy(res)
        res = self.fn(q, form_props, only) if only else self.fn(q, form_props)
        with self.lock:
            self.memo[key] = (copy.deepcopy(res), getattr(self.tt, "why", None), getattr(self.tt, "expanded", None))
            if len(self.memo) > self.size:
                self.memo.popitem(last=False)
        return res


class _OwnRecall:
    """a specialist's _own(mod) - does this module's file live in my dir? - recalled per file instead of recomputed: the
    family's _env rescans every loaded module after a call that imported anything, and the answer for a file never changes"""

    def __init__(self, organ):
        self.prefix, self.memo = organ.dir + os.sep, {}

    def __call__(self, mod):
        f = getattr(mod, "__file__", None) or ""
        if not f:
            return False
        r = self.memo.get(f)
        if r is None:
            r = self.memo[f] = os.path.abspath(f).startswith(self.prefix)
        return r


def recall_organs():
    """give every loaded specialist (combo_runtime _Organ) its _own recall, once (an instance attribute; files unchanged)"""
    import gc
    n = 0
    for o in gc.get_objects():
        try:
            if type(o).__name__ == "_Organ" and isinstance(getattr(o, "dir", None), str) and "_own" not in vars(o):
                o._own = _OwnRecall(o)
                n += 1
        except Exception:  # noqa: BLE001
            continue
    return n


class OracleReleaseRuntimeW557(_Base):
    LAW = "4.0"
    SCAN_AT = {1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144}

    def _v4_recall(self):
        """wrap every three-tree instance the chain has made so far (folds build theirs lazily, on first use)"""
        rcs = getattr(self, "_v4_rcs", None)
        if rcs is None:
            rcs = self._v4_rcs = []
        if os.environ.get("ORACLE7_V4_RECALL") == "0":     # the I3 dose-response runs one throughput setting without recall
            return rcs
        try:
            for v in list(vars(self).values()):
                for o in (v if isinstance(v, (tuple, list)) else (v,)):
                    if (hasattr(o, "adj") and hasattr(o, "max_states") and callable(getattr(o, "answer", None))
                            and not isinstance(o.answer, _WalkRecall)):
                        rc = _WalkRecall(o)
                        o.answer = rc
                        rcs.append(rc)
        except Exception:  # noqa: BLE001 - without its recall the fold walks every time
            pass
        return rcs

    def _v4_snapshot(self, session_id):
        snap = {}
        for name in SESSION_STORES:
            store = getattr(self, name, None)
            if isinstance(store, dict):
                snap[name] = (session_id in store, copy.deepcopy(store.get(session_id)))
        return snap

    def _v4_restore(self, session_id, snap):
        for name, (had, val) in snap.items():
            store = getattr(self, name, None)
            if not isinstance(store, dict):
                continue
            if had:
                store[session_id] = val
            else:
                store.pop(session_id, None)

    def chat(self, text: str, session_id: str = "default") -> dict:
        hits0 = sum(rc.hits for rc in self._v4_recall())
        try:
            snap = self._v4_snapshot(session_id)
        except Exception:  # noqa: BLE001
            snap = None
        t0 = time.perf_counter()
        r = super().chat(text, session_id)
        L = round(1000.0 * (time.perf_counter() - t0), 1)
        extra = {}
        try:
            if (isinstance(r, dict) and r.get("status") == "answered" and snap is not None
                    and not str(r.get("path", "")).startswith("act:") and not stands_on_something(r)):
                self._v4_restore(session_id, snap)
                extra["discourse_record"] = True
            hits = sum(rc.hits for rc in self._v4_recall())    # also wraps instances this turn created
            if hits > hits0:
                extra["recalled_walks"] = hits - hits0
            self._v4_n = getattr(self, "_v4_n", 0) + 1
            if os.environ.get("ORACLE7_V4_RECALL") != "0" and (self._v4_n in self.SCAN_AT or self._v4_n % 233 == 0):
                # specialist families load lazily: look again, more rarely
                recall_organs()
            ledger_append(ledger_entry(text, session_id, r, L, self.LAW, extra))
        except Exception:  # noqa: BLE001 - the law's bookkeeping never costs the turn
            pass
        return r
