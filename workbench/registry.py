"""registry - the $ORACLE7 specialist registry on Solana: who vouches for a specialist, on-chain, checkable by anyone.

  REGISTER  the creator of an ADMITTED specialist signs, with their own wallet, ONE Solana transaction that BURNS exactly
            1 $ORACLE7 from their wallet and carries the specialist's fingerprint in a memo: the SHA-256 of its files, of its
            held-out exam verdict and of its held-out set, and the Merkle root of the Oracle7 release it was examined on.
            One specialist, one $ORACLE7, verifiable by anyone: a registration counts only if the chain shows the burn and
            the memo in the same transaction, signed by the same wallet.
  ATTEST    anyone who imports a shared specialist and sees it pass its held-out exam on their own machine signs the same
            fingerprint as an attestation.
  CHECK     reads those transactions back (read-only), confirms each memo matches the specialist's CURRENT files, and shows
            each signer's wallet, the time, and how much $ORACLE7 the wallet holds now.

The Workbench never sees or stores a key: signing happens in the person's wallet (Phantom) in their browser. Nothing here
moves tokens except that one burn, which the creator approves in their own wallet. Attesting is free.
The records (transaction signatures) live in the specialist's own folder (registry.json) and travel with it when shared.
Network: a public Solana RPC, read-only, only when a person checks; set ORACLE7_SOLANA_RPC to use another."""
from __future__ import annotations

import hashlib
import json
import os
import re
import time
import urllib.request
from pathlib import Path

ORACLE7_MINT = "DU7Lhe2QtcRBJdor7KbpjfUDmLyA2kdhR49Li3czpump"        # $ORACLE7 (Token-2022), public
MEMO_PROGRAM = "MemoSq4gqABAXKb96qnH8TysNcWxMyWCqXgDLGmfcHr"
TOKEN_2022 = "TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb"
DECIMALS = 6
BURN_RAW = 1 * 10 ** DECIMALS                                            # exactly 1 $ORACLE7 per registered specialist
TAG = "oracle7-registry/1"
RPC = os.environ.get("ORACLE7_SOLANA_RPC", "https://api.mainnet-beta.solana.com")
SIG = re.compile(r"^[1-9A-HJ-NP-Za-km-z]{64,90}$")
HERE = Path(__file__).resolve().parent


def _sha_file(p):
    p = Path(p)
    return hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else "none"


def fingerprint(d):
    """the four hashes that identify an examined specialist"""
    import exam
    d = Path(d)
    v = d / "verdict_heldout.json"
    verdict = json.loads(v.read_text(encoding="utf-8")) if v.exists() else {}
    release = "none"
    try:
        release = json.loads((HERE.parent / "RELEASE_HASHES.json").read_text(encoding="utf-8"))["merkle_root"]
    except Exception:  # noqa: BLE001
        pass
    return {"id": d.name, "files": exam.files_sha(d), "verdict": _sha_file(v), "heldout": verdict.get("panel_sha") or "none",
            "decision": verdict.get("decision", "none"), "release": release}


def memo_for(d, kind):
    f = fingerprint(d)
    if kind not in ("register", "attest"):
        raise ValueError("kind is register or attest")
    if f["decision"] != "ADMIT":
        raise ValueError("only a specialist that passed its held-out exam on this machine can be %sed" % kind)
    m = "%s %s id=%s files=%s verdict=%s heldout=%s release=%s" % (TAG, kind, f["id"][:40], f["files"], f["verdict"], f["heldout"][:64],
                                                                 f["release"][:16])
    assert len(m.encode()) <= 560
    return m


RELAYED = {"getLatestBlockhash", "getTokenAccountsByOwner", "getSignatureStatuses", "getBlockHeight", "simulateTransaction"}


def relay(body):
    """the page's few Solana calls, made from this computer (the public RPC refuses browser pages): read-only methods and a
    simulation; sending is done by the person's wallet, never here"""
    msg = json.loads(body)
    calls = msg if isinstance(msg, list) else [msg]
    if not calls or not all(isinstance(c, dict) and c.get("method") in RELAYED for c in calls):
        raise ValueError("that Solana method is not relayed")
    for i in range(4):
        try:
            req = urllib.request.Request(RPC, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code != 429:
                raise ValueError("Solana RPC HTTP %d" % e.code)
            time.sleep(1.5 * (i + 1))
    raise ValueError("Solana RPC busy; try again in a minute")


def _rpc(method, params, tries=4):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(RPC, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=20) as r:
                out = json.loads(r.read())
            if "error" in out:
                last = out["error"].get("message", str(out["error"]))
                if "429" in str(out["error"]) or "Too many" in last:
                    time.sleep(1.5 * (i + 1))
                    continue
                raise ValueError("Solana RPC: %s" % last)
            return out.get("result")
        except urllib.error.HTTPError as e:
            last = "HTTP %d" % e.code
            time.sleep(1.5 * (i + 1))
    raise ValueError("Solana RPC busy (%s); try again, or set ORACLE7_SOLANA_RPC" % last)


def read_tx(signature):
    if not SIG.match(signature or ""):
        raise ValueError("that is not a Solana transaction signature")
    tx = _rpc("getTransaction", [signature, {"encoding": "jsonParsed", "maxSupportedTransactionVersion": 1, "commitment": "confirmed"}])
    if not tx:
        raise ValueError("no confirmed transaction %s" % signature)
    keys = tx["transaction"]["message"]["accountKeys"]
    signer = next((k["pubkey"] for k in keys if k.get("signer")), keys[0]["pubkey"] if keys else None)
    ins_all = tx["transaction"]["message"]["instructions"]
    memos = [ins.get("parsed") for ins in ins_all if ins.get("program") == "spl-memo" or ins.get("programId") == MEMO_PROGRAM]
    burned = 0
    for ins in ins_all:                                   # BurnChecked/Burn of the $ORACLE7 mint, authorised by the signer
        pr = ins.get("parsed") if isinstance(ins.get("parsed"), dict) else {}
        info = pr.get("info") or {}
        if pr.get("type") in ("burn", "burnChecked") and info.get("mint") == ORACLE7_MINT and info.get("authority") == signer:
            amt = (info.get("tokenAmount") or {}).get("amount") or info.get("amount") or "0"
            burned += int(amt)
    return {"signature": signature, "signer": signer, "slot": tx.get("slot"), "time": tx.get("blockTime"), "burned_raw": burned,
            "memo": next((m for m in memos if isinstance(m, str) and m.startswith(TAG)), None), "ok": tx.get("meta", {}).get("err") is None}


def oracle7_balance(owner):
    res = _rpc("getTokenAccountsByOwner", [owner, {"mint": ORACLE7_MINT}, {"encoding": "jsonParsed"}])
    total = 0.0
    for a in (res or {}).get("value", []):
        total += float(a["account"]["data"]["parsed"]["info"]["tokenAmount"].get("uiAmount") or 0)
    return total


def parse_memo(m):
    p = (m or "").split()
    if len(p) < 3 or p[0] != TAG:
        return None
    out = {"kind": p[1]}
    for kv in p[2:]:
        k, _, v = kv.partition("=")
        out[k] = v
    return out


def records(d):
    try:
        return json.loads((Path(d) / "registry.json").read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return []


def record(d, kind, signature):
    """keep a signature only after reading it back: confirmed, ours, and matching this specialist's files now"""
    t = read_tx(signature)
    f = fingerprint(d)
    m = parse_memo(t["memo"])
    if not t["ok"] or not m or m.get("kind") != kind or m.get("files") != f["files"] or m.get("verdict") != f["verdict"]:
        raise ValueError("that transaction does not carry this specialist's %s memo" % kind)
    if kind == "register" and t["burned_raw"] < BURN_RAW:
        raise ValueError("a registration must burn 1 $ORACLE7 in the same transaction; this one burned %s" % (t["burned_raw"] / 10 ** DECIMALS))
    recs = [r for r in records(d) if r["signature"] != signature]
    recs.append({"kind": kind, "signature": signature, "signer": t["signer"], "time": t["time"]})
    (Path(d) / "registry.json").write_text(json.dumps(recs, indent=1), encoding="utf-8")
    return recs


def check(d):
    """every recorded registration and attestation, read back from the chain against the specialist's files now"""
    f = fingerprint(d)
    out = []
    for r in records(d):
        try:
            t = read_tx(r["signature"])
            m = parse_memo(t["memo"]) or {}
            match = t["ok"] and m.get("files") == f["files"] and m.get("verdict") == f["verdict"]
            if m.get("kind") == "register":
                match = match and t["burned_raw"] >= BURN_RAW      # no burn, no registration
            bal = oracle7_balance(t["signer"]) if t["signer"] else 0.0
            out.append({"kind": m.get("kind", r["kind"]), "signer": t["signer"], "time": t["time"], "matches_files": match,
                        "burned": t["burned_raw"] / 10 ** DECIMALS,
                        "oracle7": bal, "signature": r["signature"], "explorer": "https://explorer.solana.com/tx/%s" % r["signature"]})
        except Exception as e:  # noqa: BLE001
            out.append({"kind": r.get("kind"), "signature": r.get("signature"), "error": str(e)})
    reg = [x for x in out if x.get("kind") == "register" and x.get("matches_files")]
    att = [x for x in out if x.get("kind") == "attest" and x.get("matches_files")]
    return {"id": f["id"], "files": f["files"], "registered": bool(reg), "attestations": len(att), "oracle7_burned": sum(x["burned"] for x in reg),
            "vouching_oracle7": round(sum(x["oracle7"] for x in reg + att), 6), "records": out, "mint": ORACLE7_MINT}
