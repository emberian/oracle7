"""network_v6 - specialist network v5 + OPERATIONS LEARNED FROM THE SPECIALISTS' OWN EXAMS (fold composition).

Until v5 every operation the network could chain was written by hand: which specialist computes what, from what, in which
phrasing. v6 adds operations learned by specfold_learn.py from each specialist's development exam (never its held-out exam):
a dev item the specialist answers right, whose question carries typed quantities and whose reply states the scored answer as
a typed quantity, becomes a template - the question with its quantities as slots in the question's own units. An operation
was kept only if siblings of the same template cross-checked it (the template filled with a sibling's quantities made the
specialist reproduce the sibling's scored answer) and no slot was a constant.

A learned operation fires only when the question being answered contains every context word of its template (names,
materials, objects and the template's fixed numbers): "the weight of a lander on Mars" is a Mars operation and is never
filled by dimension alone for a question about Io. Learned operations join v5's search; every other rule of the search is
v5's (dimensions as types, all givens used, two checked paths must agree, the search budget). A specialist that declines the
filled template ends that path. v6 loads a PRIVATE copy of v5; the released v5 is untouched.
Operations: specfold_ops_v1.json (beside this file)."""
import json
import os
import re
import sys
import threading

HERE = os.path.dirname(os.path.abspath(__file__))


def _private(name, path):
    import importlib.util
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


if HERE not in sys.path:
    sys.path.insert(0, HERE)
V5 = _private("o7_network_v5_for_v6", os.path.join(HERE, "network_v5.py"))
V4, V2 = V5.V4, V5.V4.V2
OPS_FILE = os.path.join(HERE, "specfold_ops_v1.json")
_Q = threading.local()                                  # the question being solved (learned operations check their context)


def _dim(d):
    return tuple(d) if isinstance(d, list) else d


def _words(text):
    return set(re.findall(r"[a-z][a-z0-9'-]*[a-z0-9]|[a-z]", text.lower())) | set(re.findall(r"(?<![\w.])\d[\d,]*(?:\.\d+)?%?", text.lower()))


def _fill(parts, args):
    s = ""
    for p in parts:
        if isinstance(p, dict):
            s += V2.g(args[p["slot"]].v / p["factor"])
        else:
            s += p
    return s


def learned_ops(reg, hand_ops):
    try:
        data = json.load(open(OPS_FILE, encoding="utf-8"))
    except (OSError, ValueError):
        return []
    hand = {(o.sid, tuple(sorted(str(d) for d, _ in o.slots)), str(o.out_dim)) for o in hand_ops}
    out = []
    for i, o in enumerate(data.get("ops", [])):
        sid = o["sid"]
        if sid not in reg.byte:
            continue
        ins = [_dim(d) for d in o["in"]]
        outd = _dim(o["out_dim"])
        if (sid, tuple(sorted(str(d) for d in ins)), str(outd)) in hand:
            continue                                   # a hand-written operation already does this
        u = V2.unit_lookup(o["out_unit"])
        if not u or u[1] != outd:
            continue
        ctx = set(o.get("context") or [])

        def render(a, f, parts=o["parts"], ctx=ctx):
            q = getattr(_Q, "text", "") or ""
            if not ctx <= _words(q):
                return None                            # the template's context is not this question's
            if any(x.role == "derived" for x in a):
                return None                            # only givens and specialists' outputs fill a learned slot: core
                #                                        arithmetic can build the right UNITS from the wrong physics
                #                                        (speed / length is a frequency; a string's is speed / 2 length)
            return _fill(parts, a)
        out.append(V2.Op("learned:%s:%d" % (sid, i), sid, [(d, (lambda q: q.role not in ("derived", "delta") and not q.temp_point)) for d in ins], outd, render,
                         r"\s*" + re.escape(o["out_unit"]) + r"(?![a-z])", u[0], role_out=""))
    return out


GOAL_RX = re.compile(r"\bwhat(?:'s| is| was| are)\s+(?:the|its|their)\s+([a-z]+(?:\s+(?!(?:of|in|on|at|for|from|to|with|when|if|that|after|before)\b)[a-z]+)?)\b", re.I)
_GOAL_LOCK = threading.Lock()


def learned_goals(ops_data):
    """quantity nouns the specialists' own exams ask for, and the dimension each one is: "What is the wavelength of ..." -> a
    length. A noun is kept only when every template that asks for it gives the same dimension, and it is not a unit name."""
    seen = {}
    for o in ops_data:
        q = "".join(p if isinstance(p, str) else "#" for p in o["parts"])
        m = GOAL_RX.search(q)
        if not m:
            continue
        for noun in {m.group(1).lower(), m.group(1).lower().split()[-1]}:
            if V2.unit_lookup(noun) or noun in ("answer", "value", "result", "number", "amount"):
                continue
            seen.setdefault(noun, set()).add(str(_dim(o["out_dim"])))
    dims = {str(d): d for o in ops_data for d in [_dim(o["out_dim"])]}
    return {n: dims[next(iter(ds))] for n, ds in seen.items() if len(ds) == 1}


def si_unit(dim):
    best = None
    for name, (f, d) in V2.UNITS.items():
        if d == dim and abs(f - 1) < 1e-12 and (best is None or len(name) < len(best)):
            best = name
    return best


class Network(V5.Network):
    def __init__(self, standing, spec_root, combo_code, memory_path=None, allowed=None):
        super().__init__(standing, spec_root, combo_code, memory_path, allowed)
        self.learned = learned_ops(self.reg, self.ops)
        if allowed is not None:
            self.learned = [o for o in self.learned if o.sid in set(allowed)]
        self.ops = list(self.ops) + self.learned
        try:
            self.goal_nouns = learned_goals(json.load(open(OPS_FILE, encoding="utf-8")).get("ops", []))
        except (OSError, ValueError):
            self.goal_nouns = {}

    def _goal_from_nouns(self, text):
        ask = [x for x in re.split(r"(?<=[.?!])\s+", str(text).strip()) if x]
        ask = ask[-1] if ask else str(text)
        m = GOAL_RX.search(ask)
        if not m:
            return None
        for noun in (m.group(1).lower(), m.group(1).lower().split()[-1]):
            d = self.goal_nouns.get(noun)
            u = si_unit(d) if d is not None else None
            if u:
                return ("dim", d, u, 1)
        return None

    def solve(self, text):
        _Q.text = V4.normalise(text)
        with _GOAL_LOCK:
            saved = V4.read_goal_v4
            nouns = self._goal_from_nouns

            def goal(t, counts):
                return saved(t, counts) or nouns(t)            # the learned nouns only where the reader found no goal
            V4.read_goal_v4 = goal
            try:
                out = super().solve(text)
            finally:
                V4.read_goal_v4 = saved
                _Q.text = ""
        if out.get("status") == "answered" and any(str(h.get("op", "")).startswith("learned:") for h in (out.get("trace") or [])):
            out = dict(out, learned=True)
        return out
