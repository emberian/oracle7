"""verify - check this install against the release's published hashes, and those hashes against their Solana anchor.

RELEASE_HASHES.json (beside oracle7.py) lists one SHA-256 per shipped part - every specialist directory, the admitted fold
chain, this workbench, the launcher, the store manifest - and a Merkle root over them. verify_install() recomputes every
part from the files on this computer with the same recipe and rebuilds the root. A changed, missing or extra specialist
shows by name. Stores are checked by oracle7.py --setup against PACK_MANIFEST.json, whose own hash is a part here.

check_anchor() is optional and the only step that uses the network: it asks a public Solana RPC (read-only) for the
anchor transaction named in RELEASE_HASHES.json and confirms its memo carries the same root, so the root you computed is
the one Prometheus7 committed to on-chain at release time."""
from __future__ import annotations

import hashlib
import json
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
INSTALL = HERE.parent
SKIP_DIRS = {"__pycache__", "state", "local"}
RPC = "https://api.mainnet-beta.solana.com"


def part_hash(base):
    base = Path(base)
    h = hashlib.sha256()
    files = sorted((p for p in base.rglob("*") if p.is_file() and not SKIP_DIRS & set(p.relative_to(base).parts) and p.suffix != ".pyc"),
                   key=lambda p: p.relative_to(base).as_posix().encode())
    n = 0
    for p in files:
        rel = p.relative_to(base).as_posix()
        if rel.endswith(".zst"):
            continue
        h.update(rel.encode() + b"\0")
        h.update(hashlib.sha256(p.read_bytes()).digest())
        n += 1
    return h.hexdigest(), n


def leaf(name, hexd):
    return hashlib.sha256(("oracle7-part:%s:%s" % (name, hexd)).encode()).digest()


def merkle(leaves):
    level = list(leaves)
    if not level:
        return hashlib.sha256(b"").digest()
    while len(level) > 1:
        nxt = [hashlib.sha256(level[i] + level[i + 1]).digest() for i in range(0, len(level) - 1, 2)]
        if len(level) % 2:
            nxt.append(level[-1])
        level = nxt
    return level[0]


def published():
    p = INSTALL / "RELEASE_HASHES.json"
    if not p.exists():
        raise ValueError("RELEASE_HASHES.json is not beside oracle7.py, so there is nothing to verify against")
    return json.loads(p.read_text(encoding="utf-8"))


def verify_install(root=None):
    import os
    pub = published()
    R = Path(root or os.environ.get("ORACLE7_ROOT") or (INSTALL / "root"))
    parts = {}
    for d in sorted((R / "specialists").iterdir()):
        if d.is_dir() and d.name not in SKIP_DIRS:
            parts["specialists/" + d.name] = part_hash(d)[0]
    parts["core/admitted"] = part_hash(R / "fable-content/oracle-m-series-2026-08-15/self_loop/admitted")[0]
    parts["workbench"] = part_hash(HERE)[0]
    for f in ("oracle7.py", "PACK_MANIFEST.json"):
        if (INSTALL / f).exists():
            parts[f] = hashlib.sha256((INSTALL / f).read_bytes()).hexdigest()
    want = {k: v["sha256"] for k, v in pub["parts"].items()}
    changed = sorted(k for k in want if k in parts and parts[k] != want[k])
    missing = sorted(k for k in want if k not in parts)
    extra = sorted(k for k in parts if k not in want)
    # the root is rebuilt from the PUBLISHED part list, substituting what this computer holds
    mine = {k: parts.get(k, want[k] if k in missing else parts.get(k)) for k in want}
    root = merkle([leaf(k, mine[k]) for k in sorted(want)]).hex()
    ok_parts = len(want) - len(changed) - len(missing)
    return {"release": pub.get("release"), "head": pub.get("head"), "published_root": pub["merkle_root"], "computed_root": root,
            "root_matches": root == pub["merkle_root"] and not missing, "parts": len(want), "verified": ok_parts,
            "specialists_verified": sum(1 for k in want if k.startswith("specialists/") and k not in changed and k not in missing),
            "changed": changed, "missing": missing, "extra_local": extra, "anchor": pub.get("anchor")}


def check_anchor(signature=None, rpc=RPC):
    pub = published()
    sig = signature or (pub.get("anchor") or {}).get("signature")
    if not sig:
        raise ValueError("this release's anchor transaction is not recorded yet")
    body = {"jsonrpc": "2.0", "id": 1, "method": "getTransaction",
            "params": [sig, {"encoding": "jsonParsed", "maxSupportedTransactionVersion": 1, "commitment": "finalized"}]}
    req = urllib.request.Request(rpc, data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=20) as r:
        tx = json.loads(r.read()).get("result")
    if not tx:
        raise ValueError("the RPC has no finalized transaction %s" % sig)
    memos = []
    for ins in tx["transaction"]["message"]["instructions"]:
        if ins.get("program") == "spl-memo" or ins.get("programId") == (pub.get("anchor") or {}).get("program"):
            memos.append(ins.get("parsed") if isinstance(ins.get("parsed"), str) else json.dumps(ins.get("parsed")))
    logs = " ".join(tx.get("meta", {}).get("logMessages") or [])
    found = any(pub["merkle_root"] in (m or "") for m in memos) or pub["merkle_root"] in logs
    return {"signature": sig, "slot": tx.get("slot"), "block_time": tx.get("blockTime"), "memos": memos,
            "root_on_chain": found, "explorer": "https://explorer.solana.com/tx/%s" % sig}
