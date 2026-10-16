#!/usr/bin/env python3
"""network_v4 - what may ENTER the specialist network's pool (2026-10-16). The expansion, the checks and the agreement rule
of network_v3 are unchanged; v4 changes only how a question becomes typed quantities, and where gravity comes from.

Found by composition test C1 (experiment E-20261016-0006, now spent and used here as development material):
  PLACE      a named body ("on Mars", "on the Moon") becomes a typed quantity: its surface gravity, taken from the bodies
             specialist (the weight of 1 kg there) or standard gravity for Earth. Weight is then mass x gravity and lifting
             energy mass x gravity x height, by core math; the physics node's lifting-energy operation (which uses Earth's
             gravity) is not used when another body is named. A body the question names as a planet or moon that no
             specialist knows ("the planet Zorbon") is a VALIDITY decline.
  UNITS      cubic centimetres (cm3, cc), kilonewtons, "cm/mm/in across", "thick".
  MATERIAL   "an aluminium block with a volume of 500 cm3", "a lead brick has a volume of ...": the volume is OF the material;
             a solid object's geometric volume ("a solid iron cylinder 10 cm across and 20 cm tall", "a gold coin") is too.
  CHANGE     "heated by 40 C" is a temperature DIFFERENCE; thermo heats a mass through it.
  DERIVE     an operation's input may be derived by core math from up to THREE givens ("450 km at 7 litres per 100 km").
  RATES      "18 pages per minute", "42 km in 1.5 hours", "40 litres every 5 minutes", "3 dollars per metre",
             "250 g of flour for 10 cookies", "120 bolts in 8 hours": one rate quantity (a counted noun is dimensionless),
             and "how many pages" asks for that count.
usage: network_v4.py <standing.txt> <spec_root> <combo_code_dir> "question" ..."""
import itertools
import json
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)


def _private(name, path):
    import importlib.util
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# PRIVATE copies of v2 and v3: v4 adds units and replaces readers at module level, and the chain's own network_v3 (fold w525)
# must keep exactly the modules it was admitted with (lesson of w505: never change another fold's module state)
V2 = _private("o7_network_v2_for_v4", os.path.join(HERE, "network_v2.py"))
_saved = sys.modules.get("network_v2")
sys.modules["network_v2"] = V2                    # v3's "import network_v2" binds the private copy while it loads
try:
    V3 = _private("o7_network_v3_for_v4", os.path.join(HERE, "network_v3.py"))
finally:
    if _saved is not None:
        sys.modules["network_v2"] = _saved
    else:
        sys.modules.pop("network_v2", None)
Q, Registry, core_math, g, normalise, read_goal, valid_given = V2.Q, V2.Registry, V2.core_math, V2.g, V2.normalise, V2.read_goal, V2.valid_given

D = V2.D
MASS, VOL, LEN, ENERGY, TEMP, TIME, ACC, DIMLESS = V2.MASS, V2.VOL, V2.LEN, V2.ENERGY, V2.TEMP, V2.TIME, V2.ACC, V2.DIMLESS
FORCE = D(kg=1, m=1, s=-2)
STD_G = 9.80665

# ---------------------------------------------------------------- units
V2._u("cm3|cm^3|cm³|cc|cubic centimetre|cubic centimetres|cubic centimeter|cubic centimeters", 1e-6, VOL)
V2._u("kn|kilonewton|kilonewtons", 1000, FORCE)
V2.UNIT_ALT = "|".join(sorted((re.escape(k) for k in V2.UNITS), key=len, reverse=True))
V2.RX_QTY = re.compile(r"(?<![\w.])(%s)\s*[- ]?\s*(%s)(?![a-z])" % (V2.NUM, V2.UNIT_ALT), re.I)
V2.RX_GOAL_UNIT = re.compile(r"\b(?:how many|in|into|as|to)\s+(?:us\s+)?(%s)(?![a-z])" % V2.UNIT_ALT, re.I)
V2.RX_ACROSS = re.compile(r"(%s)\s*(m|metres?|meters?|cm|centimetres?|centimeters?|mm|millimetres?|millimeters?|ft|feet|in|inch|inches)\s+(?:across|in diameter|wide)\b" % V2.NUM, re.I)
V2.RX_TALL = re.compile(r"(%s)\s*(m|metres?|meters?|ft|feet|cm|centimetres?|centimeters?|mm|millimetres?|millimeters?)\s+(?:tall|high|deep|long|thick)\b" % V2.NUM, re.I)
V2.RX_BOOL_ASK = re.compile(r"\b(?:is|are)\b[^?]*\b(?:compliant|safe|okay|ok|acceptable|allowed|within|enough)\b|\b(?:compliant|safe|okay|acceptable)\b[^?]*\?", re.I)

# ---------------------------------------------------------------- places
BODIES = {"moon": "the Moon", "mars": "Mars", "mercury": "Mercury", "venus": "Venus", "jupiter": "Jupiter", "saturn": "Saturn",
          "uranus": "Uranus", "neptune": "Neptune", "pluto": "Pluto", "io": "Io", "europa": "Europa", "ganymede": "Ganymede",
          "callisto": "Callisto", "titan": "Titan", "enceladus": "Enceladus", "triton": "Triton", "ceres": "Ceres", "earth": "Earth"}
RX_BODY = re.compile(r"\b(?:on|at|to)\s+(?:the\s+)?(Moon|moon|Mars|Mercury|Venus|Jupiter|Saturn|Uranus|Neptune|Pluto|Io|Europa|Ganymede|"
                     r"Callisto|Titan|Enceladus|Triton|Ceres|Earth)\b")
RX_NAMED_BODY = re.compile(r"\b(?:planet|moon|dwarf planet|asteroid|world)\s+(?:called\s+|named\s+)?([A-Z][a-z]+)\b")
LIFT = re.compile(r"\b(?:lift\w*|rais\w*|climb\w*|gains?|gained|height|potential energy|hoist\w*)\b", re.I)


def body_of(text):
    m = RX_BODY.search(text)
    return BODIES[m.group(1).lower()] if m else ""


def unknown_body(text):
    m = RX_NAMED_BODY.search(text)
    if m and m.group(1).lower() not in BODIES:
        return m.group(1)
    return ""


# ---------------------------------------------------------------- givens: a temperature change and rates are read first
NUM = V2.NUM
RX_DELTA = re.compile(r"\bby\s+(%s)\s*(?:°\s*|degrees?\s*)?(c|f|k|celsius|fahrenheit|kelvin)\b" % NUM, re.I)
UNIT_OR_WORD = r"(?:%s|[a-z]+)" % V2.UNIT_ALT
RX_RATE_PER = re.compile(r"(?<![\w.])(%s)\s*(%s)(?:\s+of\s+[a-z]+)?\s+(?:per|a|an|each|every)\s+(%s)\b" % (NUM, UNIT_OR_WORD, UNIT_OR_WORD), re.I)
RX_RATE_IN = re.compile(r"(?<![\w.])(%s)\s*(%s)(?:\s+of\s+[a-z]+)?\s+(?:in|every|for|per)\s+(%s)\s*(%s)\b" % (NUM, UNIT_OR_WORD, NUM, UNIT_OR_WORD), re.I)
NOT_COUNT = {"a", "an", "the", "of", "and", "or", "per", "in", "for", "every", "each", "to", "at", "on", "by", "with", "times", "time",
             "percent", "years", "year", "days", "day", "hours", "hour", "minutes", "minute", "seconds", "second", "weeks", "week"}


def _unit_or_count(word):
    """-> (factor, dim, noun) for a unit, or (1, DIMLESS, noun) for a counted noun ("pages", "bolts", "cookies")"""
    u = V2.unit_lookup(word)
    if u:
        return u[0], u[1], ""
    w = word.lower()
    if w in NOT_COUNT or len(w) < 3:
        return None
    return 1.0, DIMLESS, re.sub(r"s$", "", w)


def _another_of(t, m, dim):
    """the question names another quantity of this kind outside the matched span ("... in 4 hours")"""
    rest = t[:m.start()] + " " * (m.end() - m.start()) + t[m.end():]
    for q in V2.RX_QTY.finditer(rest):
        u = V2.unit_lookup(q.group(2))
        if u and u[1] == dim:
            return True
    return False


def read_givens_v4(text):
    """-> (givens, flags). Rates and a temperature change are read first and masked, then v2's reader takes the rest."""
    t = str(text)
    pre, spans, counts = [], [], set()
    for m in RX_DELTA.finditer(t):
        v = V2.fnum(m.group(1)) * (5 / 9 if m.group(2).lower().startswith("f") else 1)
        pre.append(Q(v, TEMP, m.group(0), "delta"))
        spans.append(m.span())
    ranges = [m.span() for m in V2.RX_RANGE.finditer(t)]
    for rx, has_den_num in ((RX_RATE_IN, True), (RX_RATE_PER, False)):
        for m in rx.finditer(t):
            if any(a < m.end() and m.start() < b for a, b in spans + ranges):
                continue
            num = _unit_or_count(m.group(2))
            den = _unit_or_count(m.group(4) if has_den_num else m.group(3))
            if not num or not den or (num[1] == DIMLESS and den[1] == DIMLESS):
                continue
            if num[1] == den[1]:
                continue                               # "litres per 100 litres" is a ratio, not a rate
            if has_den_num:
                word = (re.findall(r"\b(in|every|for|per)\b", t[m.end(2):m.start(3)], re.I) or ["per"])[-1].lower()
                counted = bool(num[2] or den[2])
                if word == "for" and not counted:
                    continue                           # "15 A for 2 hours" is a current and a duration
                if word == "in" and not counted and not _another_of(t, m, den[1]):
                    continue                           # "20 m in 40 seconds" (a lift) is two givens, not a rate
            dv = V2.fnum(m.group(3)) if has_den_num else 1.0
            if dv <= 0:
                pre.append(Q(0.0, D(m=1), m.group(0), "rate"))   # a zero divisor: validity declines it
                spans.append(m.span())
                continue
            v = V2.fnum(m.group(1)) * num[0] / (dv * den[0])
            pre.append(Q(v, V2.dmul(num[1], den[1], -1), m.group(0), "rate"))
            for c in (num[2], den[2]):
                if c:
                    counts.add(c)
            spans.append(m.span())
    masked = list(t)
    for a, b in spans:                    # blank only the NUMBERS of what was read here; the words stay for v2's flags
        for i in range(a, b):
            if t[i].isdigit() or t[i] in ".,-":
                masked[i] = " "
    masked = "".join(masked)
    givens, flags = V2.read_givens(masked)
    # counted nouns elsewhere in the question ("24 cookies", "30 hours" is a unit already)
    if counts:
        for m in re.finditer(r"(?<![\w.])(%s)\s+([a-z]+)\b" % NUM, masked, re.I):
            noun = re.sub(r"s$", "", m.group(2).lower())
            if noun in counts and not V2.unit_lookup(m.group(2)):
                givens.append(Q(V2.fnum(m.group(1)), DIMLESS, m.group(0), "count_" + noun))
                flags["unread_numbers"] = [x for x in flags.get("unread_numbers", []) if x not in m.group(1)]
    flags["counts"] = sorted(counts)
    return pre + givens, flags


def read_goal_v4(text, counts):
    t = str(text)
    q = [s for s in re.split(r"(?<=[.?!])\s+", t.strip()) if s]
    ask = q[-1] if q else t
    m = re.search(r"\bhow many\s+(?:more\s+)?([a-z]+)\b", ask, re.I)
    if m and re.sub(r"s$", "", m.group(1).lower()) in counts and not V2.unit_lookup(m.group(1)):
        return ("dim", DIMLESS, m.group(1).lower(), 1)
    return read_goal(text)


# ---------------------------------------------------------------- operations
def ops_v4(reg, base_ops):
    O = []
    for op in base_ops:
        if op.name == "potential_energy":                 # the physics node lifts with Earth's gravity
            r0 = op.render
            op.render = (lambda r0: lambda a, f: None if f.get("body") not in ("", "Earth") else r0(a, f))(r0)
        if op.name in ("mass_of_volume",):
            r0 = op.render
            op.render = (lambda r0: lambda a, f: _mass_of_volume_v4(a, f, r0))(r0)
        O.append(op)
    if reg.byte.__contains__("thermo"):
        def _heat_delta(a, f):
            mat = f.get("material") or ""
            if not mat or mat == "ice" or a[1].role != "delta" or a[1].v <= 0:
                return None
            return "How much heat is needed to raise %s kg of %s from 20 C to %s C?" % (g(a[0].v), mat, g(round(20 + a[1].v, 4)))
        O.append(V2.Op("sensible_heat_by", "thermo", [(MASS, lambda q: True), (TEMP, lambda q: q.role == "delta")], ENERGY, _heat_delta,
                       r"J\b", 1, role_out="heat"))
    return O


SOLID = re.compile(r"\bsolid\b|\b(?:%s)\s+(?:cylinder|coin|disc|disk|rod|bar|block|brick|cube|plate|pipe|can)\b" % "|".join(
    sorted((re.escape(k) for k in V3.SUBSTANCES), key=len, reverse=True)), re.I)
VOLUME_OF = r"\b(?:%s)\b(?:\s+[a-z]+){0,3}\s+(?:with|has|of)\s+a\s+volume\s+of\s+%s"
FULL = re.compile(r"\bfull\s+(?:\w+\s+)?of\b|\bfilled with\b|\bholds?\b|\bholding\b|\bcontains?\b", re.I)


def _vol_phrase(v):
    return ("%s cm3" % g(v * 1e6)) if v < 1e-3 else ("%s m3" % g(v))


def _mass_of_volume_v4(a, f, base):
    r = base(a, f)
    if r is not None:
        return re.sub(r"of ([-\d.e+]+) m3 of", lambda m: "of %s of" % _vol_phrase(float(m.group(1))), r)
    mat = f.get("object") or f.get("substance")
    if not mat or f.get("asks_co2"):
        return None
    v, text = a[0], f.get("_text", "")
    alts = [k for k, x in V3.SUBSTANCES.items() if x == mat] + [mat]
    if v.src == "given" and re.search(VOLUME_OF % ("|".join(re.escape(x) for x in alts), re.escape(v.text)), text, re.I):
        return "What is the mass of %s of %s in kg?" % (_vol_phrase(v.v), mat)
    if v.src in ("geometry-v4", "geometry") and (SOLID.search(text) or FULL.search(text)):
        return "What is the mass of %s of %s in kg?" % (_vol_phrase(v.v), mat)
    return None


class Network(V3.Network):
    def __init__(self, standing, spec_root, combo_code, memory_path=None, allowed=None):
        super().__init__(standing, spec_root, combo_code, memory_path, allowed)
        self.ops = ops_v4(self.reg, self.ops)
        self.gravity_cache = {}

    def _fillers(self, pool, avail, dim, pred):
        out = super()._fillers(pool, avail, dim, pred)
        gv = [k for k in avail if k.startswith("g") and not pool[k].temp_point]
        for i, j, k in itertools.combinations(gv, 3):        # DERIVE from three givens
            cm = core_math([pool[i], pool[j], pool[k]], dim)
            if cm and pred(Q(cm[0], dim, "derived", "")):
                out.append(("d3", i, j, k))
        return out

    def gravity(self, body):
        """-> (value m/s2, trace hop) for a named body: standard gravity for Earth, else the bodies specialist's weight of 1 kg"""
        if body == "Earth":
            return STD_G, {"node": "core_math", "byte": Registry.CORE_MATH, "op": "standard_gravity", "value": STD_G, "unit": "m/s²"}
        if body not in self.gravity_cache:
            sid = next((x for x in ("bodies-v2", "bodies") if os.path.isdir(os.path.join(self.reg.root, x))), "")
            val, hop = None, None
            if sid and sid not in self.reg.byte:              # not in the standing order: next free byte, before CORE_MATH
                self.reg.byte[sid] = len(self.reg.ids)
                self.reg.ids.append(sid)
            if sid:
                ask = "What is the weight of a 1 kg lander on %s?" % body
                r = self.reg.ask(sid, ask)
                v = V2.parse_value((r or {}).get("response", ""), r"N\b|newtons?") if r and not r.get("declined") else None
                if v and v > 0:
                    val = v
                    hop = {"node": sid, "byte": self.reg.byte.get(sid), "op": "surface_gravity", "asked": ask, "value": v, "unit": "m/s²"}
            self.gravity_cache[body] = (val, hop)
        return self.gravity_cache[body]

    def solve(self, text):
        text = normalise(text)
        givens, flags = read_givens_v4(text)
        goal = read_goal_v4(text, flags.get("counts", []))
        base = {"question": text, "givens": [repr(q) for q in givens], "goal": str(goal)}
        ub = unknown_body(text)
        if ub:
            return dict(base, status="declined", check="validity", reason="I have no record of a body called %s, so I can't use its gravity" % ub)
        for q in givens:
            if q.role == "rate" and q.v <= 0:
                return dict(base, status="declined", check="validity", reason="%s is not a physical rate" % q.text)
            bad = valid_given(q) if q.role != "delta" else (None if q.v > 0 else "%s is not a temperature change" % q.text)
            if bad:
                return dict(base, status="declined", reason=bad, check="validity")
        if goal is None:
            return dict(base, status="declined", reason="no answerable goal in the question")
        if not givens:
            return dict(base, status="declined", reason="no quantities to work from")
        if flags.get("unread_numbers"):
            return dict(base, status="declined", reason="numbers I could not read: %s" % ", ".join(flags["unread_numbers"][:4]),
                        check="all numbers read")
        flags = V3.read_flags_v3(text, {k: v for k, v in flags.items() if k not in ("unread_numbers", "counts")})
        body = body_of(text)
        flags["body"] = body
        extra_trace, pool0 = [], {"g%d" % i: q for i, q in enumerate(givens)}
        wants_g = goal[0] == "dim" and (goal[1] == FORCE and re.search(r"\bweigh", text, re.I) or goal[1] == ENERGY and LIFT.search(text) or goal[1] == ACC)
        own_body = any(q.role in ("earth_mass", "earth_radius") or q.dim == ACC for q in givens)
        if wants_g and not own_body and (body or (goal[1] == FORCE and re.search(r"\bweigh", text, re.I))):
            gv, hop = self.gravity(body or "Earth")
            if gv is None:
                return dict(base, status="declined", reason="no specialist gave the surface gravity of %s" % body)
            pool0["b0"] = Q(gv, ACC, "gravity on %s" % (body or "Earth"), "gravity", src=hop["node"])
            extra_trace.append(hop)
        return self._solve_pool(text, givens, goal, flags, pool0, extra_trace, base)

    def _solve_pool(self, text, givens, goal, flags, pool0, extra_trace, base):
        """network_v3.solve's search, starting from a pool that may carry a place's gravity"""
        self._cache = {}
        self._last_tokens = self._shape_tokens(goal, givens, flags)
        shape = self.shape(goal, givens, flags)
        remembered = self.memory.get(shape)
        frontier = [(pool0, frozenset(pool0), [], list(extra_trace), None, 0)]
        seen, states = set(), 0
        for depth in range(V3.MAX_OPS + 1):
            done = []
            for st in frontier:
                f = self._finish(st[0], st[1], goal, st[4], depth if "b0" not in pool0 else max(depth, 1), givens)
                if f == "single":
                    return dict(base, status="declined", reason="single conversion (the core's own operator)", check="multi-step only")
                if f:
                    done.append((f, st))
            if done:
                vals = [f[0] for f, _ in done]
                if not all(V3._same(vals[0], v) for v in vals[1:]):
                    alts = sorted({f[1] for f, _ in done})
                    return dict(base, status="declined", check="paths disagree",
                                reason="two checked paths give different answers (%s)" % " / ".join(alts[:3]))
                done.sort(key=lambda x: [n for n, _ in x[1][2]] != (remembered or {}).get("ops"))
                (val, say, sentence, extra), st = done[0]
                plan = [(next(o for o in self.ops if o.name == n), c) for n, c in st[2]]
                return self._done(base, shape, plan, st[3] + extra, say, sentence, goal, remembered)
            if depth == V3.MAX_OPS:
                break
            nxt = []
            for st in frontier:
                for ns in self._expand(st, flags):
                    key = (tuple(sorted((k, round(ns[0][k].v, 9), str(ns[0][k].dim)) for k in ns[1])), ns[4] is not None)
                    if key in seen:
                        continue
                    seen.add(key)
                    nxt.append(ns)
                    states += 1
                    if states > V3.MAX_STATES:
                        return dict(base, status="declined", reason="search budget reached before a checked path", check="budget")
            frontier = nxt
            if not frontier:
                break
        return dict(base, status="declined", reason="no checked path from the givens to what is asked")

    def _expand(self, state, flags):
        """v3's expansion, with three-given derived inputs ("d3") rendered by core math"""
        pool, avail, plan, trace, final_bool, nres = state
        if final_bool is not None:
            return
        for op in self.ops:
            fill = [self._fillers(pool, avail, d, pred) for d, pred in op.slots]
            for combo in itertools.product(*fill):
                used = []
                for sp in combo:
                    used += list(sp[1:]) if isinstance(sp, tuple) else [sp]
                if len(set(used)) != len(used):
                    continue
                temps = [sp for sp, (d, _p) in zip(combo, op.slots) if d == TEMP and not (isinstance(sp, str) and pool[sp].role == "delta")]
                if len(temps) >= 2 and any(not isinstance(a, str) or not isinstance(b, str) or not (a.startswith("g") and b.startswith("g"))
                                           or int(a[1:]) > int(b[1:]) for a, b in zip(temps, temps[1:])):
                    continue
                args, pre = [], []
                for sp, (d, _p) in zip(combo, op.slots):
                    if isinstance(sp, tuple):
                        qs = [pool[x] for x in sp[1:]]
                        cm = core_math(qs, d)
                        pre.append({"node": "core_math", "byte": Registry.CORE_MATH, "op": "derive", "formula": cm[1], "value": cm[0]})
                        args.append(Q(cm[0], d, "(%s)" % cm[1], "derived"))
                    else:
                        args.append(pool[sp])
                res, tr = self._apply(op, args, flags)
                if res is None or res == "declined":
                    continue
                navail = frozenset(avail - set(used))
                npool, nplan = dict(pool), plan + [(op.name, tuple(map(str, combo)))]
                if isinstance(res, tuple) and res[0] == "bool":
                    yield (npool, navail, nplan, trace + pre + tr, res, nres)
                else:
                    k = "r%d" % (nres + 1)
                    npool[k] = res
                    yield (npool, navail | {k}, nplan, trace + pre + tr, None, nres + 1)


if __name__ == "__main__":
    net = Network(open(sys.argv[1]).read().split(), sys.argv[2], sys.argv[3])
    for q in sys.argv[4:]:
        r = net.solve(q)
        print(json.dumps({k: r.get(k) for k in ("status", "answer", "response", "reason", "check", "goal")}, ensure_ascii=False)[:600])
