#!/usr/bin/env python3
"""v4_law - Oracle7 4.0: the path alphabet LAMBDA, path vectors, the Tree-of-Life stabilizer and the re-entrance tracker.

LAMBDA = the twenty-two paths of the three-tree runtime (oracle_tritree_v1.TREE_OF_LIFE), letters 0..21 in that order.
A turn's word is the sequence of edges its walk takes from Malkuth (written to the ledger by fold w557).

PATH(w) = sum_p bind(K[w_p], R[p]) in the codebook construction of 3.2's path memory (specialists/_gate/path_hrr_v1:
osub_seed = sha256-seeded unit complex phasors, D = 1024; roles R[p] = osub_seed("o7pos:%d" % p); letters
K[e] = osub_seed("o7lam:%d" % e)).

THE STABILIZER. Plain cleanup reads each position against every letter. The Tree-of-Life stabilizer reads position p only
against the letters that leave the node position p-1 ended at (a walk can only continue along an edge of its current node),
starting at Malkuth: 2-6 candidates instead of 22. Same vector, same codebook; only the cleanup is constrained by the Tree.

RE-ENTRANCE (I6). A form is re-entered when a later turn's PATH has cosine >= TAU with it. TAU = 0.95, fixed here before any
4.0 panel ran: a word of up to 19 letters re-entered with one letter different still scores below it, so re-entered means
the same walk. Reported against a baseline of shuffled words (each word's letters permuted, the same lengths).

usage: v4_law.py capacity [out.json]   - exact-word recall of N bundled walks, plain vs stabilized
       v4_law.py reentry <ledger.jsonl> - re-entrance of the ledger's forms, against the shuffled baseline"""
from __future__ import annotations

import hashlib
import json
import random
import sys

import numpy as np

D = 1024
TAU = 0.95
SEPH = ["keter", "chokmah", "binah", "chesed", "geburah", "tiferet", "netzach", "hod", "yesod", "malkuth"]
EDGES = [("keter", "chokmah"), ("keter", "binah"), ("keter", "tiferet"), ("chokmah", "binah"), ("chokmah", "tiferet"),
         ("chokmah", "chesed"), ("binah", "tiferet"), ("binah", "geburah"), ("chesed", "geburah"),
         ("chesed", "tiferet"), ("chesed", "netzach"), ("geburah", "tiferet"), ("geburah", "hod"),
         ("tiferet", "netzach"), ("tiferet", "yesod"), ("tiferet", "hod"), ("netzach", "hod"), ("netzach", "yesod"),
         ("netzach", "malkuth"), ("hod", "yesod"), ("hod", "malkuth"), ("yesod", "malkuth")]
ADJ = {s: [] for s in SEPH}
for i, (a, b) in enumerate(EDGES):
    ADJ[a].append((i, b))
    ADJ[b].append((i, a))


def osub_seed(text, dim=D):
    h = int(hashlib.sha256(text.lower().strip().encode()).hexdigest(), 16)
    rng = np.random.RandomState(h % (2 ** 31))
    return np.exp(1j * rng.uniform(0, 2 * np.pi, dim)).astype(np.complex64)


def bind(a, b):
    return np.fft.ifft(np.fft.fft(a) * np.fft.fft(b)).astype(np.complex64)


def unbind(c, b):
    return np.fft.ifft(np.fft.fft(c) * np.conj(np.fft.fft(b))).astype(np.complex64)


K = np.stack([osub_seed("o7lam:%d" % e) for e in range(len(EDGES))])
R = [osub_seed("o7pos:%d" % p) for p in range(64)]


def path_vec(word):
    return np.sum([bind(K[e], R[p]) for p, e in enumerate(word)], axis=0).astype(np.complex64)


def decode_plain(vec, n):
    out = []
    for p in range(n):
        sims = np.real(K.conj() @ unbind(vec, R[p]))
        out.append(int(np.argmax(sims)))
    return out


def decode_tree(vec, n, start="malkuth"):
    out, cur = [], start
    for p in range(n):
        est = unbind(vec, R[p])
        cands = ADJ[cur]
        sims = [float(np.real(np.vdot(K[e], est))) for e, _ in cands]
        e, nxt = cands[int(np.argmax(sims))]
        out.append(e)
        cur = nxt
    return out


def walk(rng, n, start="malkuth"):
    out, cur = [], start
    for _ in range(n):
        e, nxt = rng.choice(ADJ[cur])
        out.append(e)
        cur = nxt
    return out


def capacity(seed=4000, lengths=(6, 9, 12), bundles=(1, 2, 4, 8, 16, 32, 64), trials=60):
    """exact-word recall of N walks bundled into ONE vector (each bound to its own key), plain cleanup vs the stabilizer"""
    rng = random.Random(seed)
    rows = []
    for n in lengths:
        for N in bundles:
            ok_p = ok_t = tot = 0
            for t in range(max(1, trials // N)):
                words = [walk(rng, n) for _ in range(N)]
                keys = [osub_seed("o7item:%d:%d:%d:%d" % (seed, n, t, i)) for i in range(N)]
                M = np.sum([bind(k, path_vec(w)) for k, w in zip(keys, words)], axis=0)
                for k, w in zip(keys, words):
                    v = unbind(M, k)
                    ok_p += decode_plain(v, n) == w
                    ok_t += decode_tree(v, n) == w
                    tot += 1
            rows.append({"letters": n, "bundled": N, "words": tot, "plain": round(ok_p / tot, 4), "stabilized": round(ok_t / tot, 4)})
            print(json.dumps(rows[-1]), flush=True)
    return rows


def cos(a, b):
    return float(np.real(np.vdot(a, b)) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-12))


def reentry(entries, seed=4001):
    """share of forms (answered words) re-entered by a later turn at cos >= TAU, and the same for shuffled words"""
    words = [e["word"] for e in entries if e.get("status") == "answered" and e.get("word")]
    rng = random.Random(seed)
    shuf = [rng.sample(w, len(w)) for w in words]

    def rate(ws):
        vs = [path_vec(w) for w in ws]
        hit = sum(1 for i in range(len(vs)) if any(cos(vs[i], vs[j]) >= TAU for j in range(i + 1, len(vs))))
        return hit, len(vs)
    h, n = rate(words)
    hs, ns = rate(shuf)
    return {"forms": n, "reentered": h, "rate": round(h / n, 4) if n else 0.0, "shuffled_reentered": hs,
            "shuffled_rate": round(hs / ns, 4) if ns else 0.0, "tau": TAU}


if __name__ == "__main__":
    if sys.argv[1] == "capacity":
        rows = capacity()
        if len(sys.argv) > 2:
            json.dump({"D": D, "codebook": "osub_seed o7lam/o7pos", "rows": rows}, open(sys.argv[2], "w"), indent=1)
    elif sys.argv[1] == "reentry":
        print(json.dumps(reentry([json.loads(l) for l in open(sys.argv[2])])))
