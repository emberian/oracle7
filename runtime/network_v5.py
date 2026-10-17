#!/usr/bin/env python3
"""network_v5 - the specialist network, v5 = v4 + the shapes v4 could not read (found by composition test C2,
E-20261016-0008, now spent and used as development with C1). The planner, the pool, the checks and every operation are v4's,
unchanged; only what can ENTER the pool grows:
  - a box given as "5 cm by 4 cm by 3 cm" and a cube given as "5 cm on each side" (or "a 5 cm cube") become ONE volume,
    derived by core arithmetic; the derivation is a hop in the path (node core_math), so the trace says who computed it.
    A derived volume of a solid object becomes its mass through the densities specialist, as v4 does for geometry volumes;
  - "500 cubic centimetres of ice" ties the volume to its material, as "a block of ice with a volume of ..." already did;
  - "the water in it" / "the water in the pond" means the vessel is full, as "full of water" already did;
  - "in a day" (an hour, a week, a year, a minute) with no number is one of that unit - a duration given in words;
  - "already at 0 °C" describes the object's state, not a quantity the chain must use (ice to melt).
It loads a PRIVATE copy of network_v4 (which loads its own private v2/v3), so the released v4 and the w525/w542 networks
are untouched. v5 changes no answer v4 gives on the network development sets (checked before release)."""
from __future__ import annotations

import importlib.util
import os
import re
import sys
import threading

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)


def _private(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


V4 = _private("o7_network_v4_for_v5", os.path.join(HERE, "network_v4.py"))
V2, V3 = V4.V2, V4.V3
Q, D, Registry = V4.Q, V4.D, V4.Registry
NUM = V4.NUM
LEN, VOL, TIME = D(m=1), D(m=3), D(s=1)
UNIT = r"(?:mm|millimetres?|millimeters?|cm|centimetres?|centimeters?|m|metres?|meters?|in|inch(?:es)?|ft|feet|foot)"
RX_BOX = re.compile(r"(?<![\w.])(%s)\s*(%s)?\s*(?:by|x|×)\s*(%s)\s*(%s)?\s*(?:by|x|×)\s*(%s)\s*(%s)\b" % (NUM, UNIT, NUM, UNIT, NUM, UNIT), re.I)
RX_CUBE = re.compile(r"(?<![\w.])(%s)\s*(%s)\s+on\s+(?:each|every|a)\s+side\b|(?<![\w.])(%s)\s*(%s)\s+cube\b" % (NUM, UNIT, NUM, UNIT), re.I)
RX_IN_A = re.compile(r"\b(?:in|over|for|during)\s+(?:a|an|one)\s+(second|minute|hour|day|week|year)\b", re.I)
SECONDS = {"second": 1, "minute": 60, "hour": 3600, "day": 86400, "week": 604800, "year": 31557600}
ALREADY_AT = re.compile(r"\balready\s+(?:at|is)\s+(%s)\s*(?:°\s*|degrees?\s*)?[cfk]\b" % NUM, re.I)
WATER_IN = re.compile(r"\bthe\s+(?:water|liquid|oil|milk|petrol|gasoline|diesel)\s+in\s+(?:it|the\s+\w+)\b", re.I)


def _len(num, unit):
    u = V2.unit_lookup(unit or "m")
    return V2.fnum(num) * (u[0] if u else 1.0)


def read_givens_v5(text):
    """v4's reading, then the shapes it left out. Lengths that form a box or a cube are REPLACED by the one volume they
    describe; returns (givens, flags) with flags["pre_hops"] = the core-math derivations, for the trace."""
    givens, flags = V4.read_givens_v4(text)
    t = str(text)
    hops = []
    m = RX_BOX.search(t)
    if m:
        unit = m.group(6)
        a, b, c = (_len(m.group(i), m.group(i + 1) or unit) for i in (1, 3, 5))
        if min(a, b, c) > 0:
            vol = a * b * c
            span = m.group(0)
            givens = [q for q in givens if not (q.dim == LEN and q.text and q.text in span)]
            givens.append(Q(vol, VOL, span, "volume", src="core_math"))
            hops.append({"node": "core_math", "byte": Registry.CORE_MATH, "op": "box_volume", "formula": "a×b×c", "value": vol})
    m = RX_CUBE.search(t)
    if m and not hops:
        num, unit = (m.group(1), m.group(2)) if m.group(1) else (m.group(3), m.group(4))
        s = _len(num, unit)
        if s > 0:
            span = m.group(0)
            givens = [q for q in givens if not (q.dim == LEN and q.text and (q.text in span or span in q.text))]
            givens.append(Q(s ** 3, VOL, span, "volume", src="core_math"))
            hops.append({"node": "core_math", "byte": Registry.CORE_MATH, "op": "cube_volume", "formula": "s³", "value": s ** 3})
    m = ALREADY_AT.search(t)                                  # "already at 0 °C" describes a state, not a quantity to use
    if m:
        givens = [q for q in givens if not (q.dim == D(K=1) and q.text and q.text in m.group(0))]
    m = RX_IN_A.search(t)
    if m and not any(q.dim == TIME for q in givens):
        givens.append(Q(float(SECONDS[m.group(1).lower()]), TIME, m.group(0), "duration"))
    flags["pre_hops"] = hops
    return givens, flags


_mass_v4 = V4._mass_of_volume_v4


def _mass_of_volume_v5(a, f, base):
    r = _mass_v4(a, f, base)
    if r is not None:
        return r
    mat = f.get("object") or f.get("substance")
    if not mat or f.get("asks_co2"):
        return None
    v, text = a[0], f.get("_text", "")
    alts = [k for k, x in V3.SUBSTANCES.items() if x == mat] + [mat]
    names = "|".join(re.escape(x) for x in alts)
    if v.src == "given" and re.search(r"%s\s+of\s+(?:the\s+)?(?:%s)\b" % (re.escape(v.text), names), text, re.I):
        return "What is the mass of %s of %s in kg?" % (V4._vol_phrase(v.v), mat)          # "500 cubic centimetres of ice"
    if v.src == "core_math" and V4.SOLID.search(text):
        return "What is the mass of %s of %s in kg?" % (V4._vol_phrase(v.v), mat)          # a box or cube of a solid
    if v.src in ("geometry-v4", "geometry") and WATER_IN.search(text):
        return "What is the mass of %s of %s in kg?" % (V4._vol_phrase(v.v), mat)          # "the water in the pond"
    return None


V4._mass_of_volume_v4 = _mass_of_volume_v5            # the PRIVATE copy's mass rule (ops_v4 looks it up at call time)
_SOLVE_LOCK = threading.Lock()                        # solve swaps the private v4 reader for one call


class Network(V4.Network):
    def solve(self, text):
        """v4's solve with v5's reader; the core-math derivations of a box or cube volume lead the trace"""
        text = V4.normalise(text)
        givens, flags = read_givens_v5(text)
        pre = flags.pop("pre_hops", [])
        with _SOLVE_LOCK:
            saved = V4.read_givens_v4
            try:
                V4.read_givens_v4 = lambda _t: (givens, dict(flags))  # v4.solve reads through this name; same answer for this text
                out = super().solve(text)
            finally:
                V4.read_givens_v4 = saved
        if pre and out.get("status") == "answered":
            out = dict(out)
            trace = pre + list(out.get("trace") or [])
            out["trace"] = trace
            out["path_bytes"] = bytes(int(h["byte"]) for h in trace).hex()
            nodes = [h["node"] for h in trace]
            out["response"] = re.sub(r"\(path: [^)]*\)", "(path: %s)" % " → ".join(nodes), str(out.get("response", "")))
        return out
