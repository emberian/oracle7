#!/usr/bin/env python3
"""path_memory_v1 - Oracle7's PATH MEMORY for routing: which route has EARNED trust for which shape of question, credited
only by VERIFIED outcomes (a held-out or dev exam's grade against its gold), stored in the substrate's own algebra.

A PATH is one vector:  P = bind(R_wh, osub(wh)) + bind(R_rel, osub(rel)) + bind(R_num, osub(num)) + bind(R_route, osub(route))
  wh    - the question's lead (who / what / where / when / which / how many / how much / name / other)
  rel   - the relation reader that recognises the question (relation_readers_v1 key), or "none"
  num   - whether the question carries numbers
  route - the normalised route that answered ("organ:relation", "deliberation:where", "compose:bridge", "specialist:rel", ...)
Codebook: osub_seed (sha256-seeded unit phasors, D=1024), the construction path_hrr_v1 validated (4-hop recovery 100%).
Each stored path carries counts (right, wrong) - credit up for a verified right answer, down for a verified wrong one or
a false yes. RECALL: the exact path when stored; otherwise the most RESONANT stored path with the same route (partial cue:
an unseen relation or lead borrows the credit of its nearest neighbour), and only above a resonance floor.
The memory never produces an answer. It only says how far a route's answer to this shape can be trusted.
build: path_memory_v1.py build <credit .jsonl ...> <out.json>"""
from __future__ import annotations

import hashlib
import json
import re
import sys

import numpy as np

D = 1024
LEADS = (("how many", "howmany"), ("how much", "howmuch"), ("who", "who"), ("whom", "who"), ("whose", "who"), ("where", "where"),
         ("when", "when"), ("which", "which"), ("what", "what"), ("in what", "what"), ("in which", "which"), ("name", "name"),
         ("tell me", "name"), ("the ", "the"))


def osub_seed(text: str, dim: int = D) -> np.ndarray:
    h = int(hashlib.sha256(text.lower().strip().encode()).hexdigest(), 16)
    rng = np.random.RandomState(h % (2 ** 31))
    return np.exp(1j * rng.uniform(0, 2 * np.pi, dim)).astype(np.complex64)


def bind(a, b):
    return np.fft.ifft(np.fft.fft(a) * np.fft.fft(b)).astype(np.complex64)


ROLES = {r: osub_seed("o7pm-role:" + r) for r in ("wh", "rel", "num", "route")}


def lead(q):
    t = " ".join(str(q).lower().split())
    for a, b in LEADS:
        if t.startswith(a):
            return b
    return "other"


_READERS = None


def relation_key(q):
    """the relation reader that recognises the question (the readers' own compiled phrasings), else 'none'"""
    global _READERS
    try:
        import relation_readers_v1 as RD
        import relation_spec_v2 as S
    except Exception:  # noqa: BLE001
        return "none"
    if _READERS is None:
        _READERS = [(k, S.compiled(k)) for k in RD.PROPS]
    s, low = S.normalise(q)
    for k, comp in _READERS:
        for d in ("fwd", "inv"):
            if any(rx.match(low) for rx in comp[d]):
                return str(k)
    return "none"


def route_of(path):
    p = str(path or "")
    p = re.sub(r"^(?:chat:resolved>|chat:and_parts>[^>]*>|specialist_precedence>)+", "", p)
    if p.startswith("specialist_call>"):
        m = re.search(r"specialist:([a-z0-9-]+)", p)
        sid = m.group(1) if m else "x"
        return "specialist:rel" if sid.startswith("rel-") else "specialist:" + re.sub(r"-(v\d+|r\d+)$", "", sid)
    if p.startswith("precision_guard:"):
        return "guard"
    return re.split(r"[>|]", p, 1)[0] or "none"


def shape(q):
    return {"wh": lead(q), "rel": relation_key(q), "num": "1" if re.search(r"\d", q) else "0"}


def path_vec(sh, route):
    v = sum(bind(ROLES[r], osub_seed("o7pm:%s:%s" % (r, sh[r]))) for r in ("wh", "rel", "num"))
    v = v + bind(ROLES["route"], osub_seed("o7pm:route:" + route))
    return (v / np.maximum(np.abs(v), 1e-8)).astype(np.complex64)


def key(sh, route):
    return "%s|%s|%s|%s" % (sh["wh"], sh["rel"], sh["num"], route)


class PathMemory:
    def __init__(self, entries=None):
        self.entries = entries or {}          # key -> {"shape": {...}, "route": r, "right": n, "wrong": n}
        self._vec = {}

    def credit(self, sh, route, outcome):
        k = key(sh, route)
        e = self.entries.setdefault(k, {"shape": dict(sh), "route": route, "right": 0, "wrong": 0})
        e["right" if outcome == "right" else "wrong"] += 1

    def _v(self, k):
        if k not in self._vec:
            e = self.entries[k]
            self._vec[k] = path_vec(e["shape"], e["route"])
        return self._vec[k]

    def recall(self, sh, route, floor=0.45):
        """-> (right, wrong, resonance, key used) for this path; exact if stored, else the most resonant stored path with the
        same route above the floor, else None"""
        k = key(sh, route)
        if k in self.entries:
            e = self.entries[k]
            return e["right"], e["wrong"], 1.0, k
        q = path_vec(sh, route)
        best, arg = -1.0, None
        for kk, e in self.entries.items():
            if e["route"] != route:
                continue
            r = float(np.real(np.vdot(self._v(kk), q)) / D)
            if r > best:
                best, arg = r, kk
        if arg is None or best < floor:
            return None
        e = self.entries[arg]
        return e["right"], e["wrong"], best, arg

    def precision(self, sh, route, prior=(1, 1), min_n=6):
        r = self.recall(sh, route)
        if r is None or r[0] + r[1] < min_n:
            return None
        return (r[0] + prior[0]) / (r[0] + r[1] + prior[0] + prior[1]), r[0] + r[1]

    def save(self, path):
        json.dump({"D": D, "entries": self.entries}, open(path, "w"), indent=0)

    @classmethod
    def load(cls, path):
        return cls(json.load(open(path))["entries"])


def build(files, out):
    pm = PathMemory()
    n = 0
    for f in files:
        for line in open(f):
            r = json.loads(line)
            sh = shape(r["q"])
            for arm in ("head", "family"):
                x = r.get(arm)
                if not x or x.get("status") != "answered" or x.get("grade") not in ("right", "wrong"):
                    continue
                pm.credit(sh, route_of(x["path"]), x["grade"])
                n += 1
    pm.save(out)
    return pm, n


if __name__ == "__main__":
    sys.path.insert(0, "/opt/oracle-clm/wander-train")       # the runtime's relation readers - the shape must match the runtime's
    import relation_readers_v1  # noqa: F401,E402 - fail loudly: a memory built without relation keys is a different memory
    if sys.argv[1] == "build":
        pm, n = build(sys.argv[2:-1], sys.argv[-1])
        print("credited outcomes", n, "paths", len(pm.entries))
