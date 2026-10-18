#!/usr/bin/env python3
"""oracle_release_runtime_w551 - CORRECTNESS RELEASE (3.2): THE PROVED CROSS-CHECK.

veri7vn (github.com/emberian/veri7vn, CC0, by ember arlynx; our fork github.com/psiloceyeben/veri7vn) re-implements 117 of
Oracle7's released specialists as kernels written and proved in Isabelle/HOL, exported to Standard ML and compiled with
MLton. Each kernel answers by the answerer contract (one JSON line in, one out) and names the theorems its answer rests on.
On the research box, over the released specialists' own held-out exams (6,444 questions), the kernels and the Python
specialists gave the same answer value on every question both answered, apart from display rounding (the kernels round
exact rationals; a Python float can store 0.675 as 0.67499...).

After the parent turn, when the reply came from ONE named specialist (path "specialist:<id>") that has a kernel:
  - the kernel is asked the same question;
  - it agrees (same Yes/No opening, and the first stand-alone number equal within one unit of the reply's last shown
    decimal or 0.5%) -> the reply is UNCHANGED, byte for byte; its path gains ">proved:<session>" and the reply carries
    "proved": {kernel, session, theorems};
  - it gives a different answer -> the reply is withheld, and says a proved check disagreed;
  - it declines, errors, times out, or there is no kernel or no Linux x86-64 to run it on -> the reply is unchanged.
So the fold can only add a mark of proof, or withhold an answer a proved kernel contradicts. Kernels are static Linux
x86-64 binaries under specialists/_proved/bin (SHA256SUMS, PROVED.json: source commit, licence, specialist map)."""
from __future__ import annotations

import json
import os
import platform
import re
import shutil
import subprocess
import threading

from oracle_release_runtime_w548 import OracleReleaseRuntimeW548 as _Base

PROVED = __import__("os").environ.get("ORACLE7_ROOT", "/opt/oracle-clm") + "/specialists/_proved"
NUM = re.compile(r"(?<![A-Za-z_\d.])-?\d[\d,]*(?:\.\d+)?")
YESNO = re.compile(r"^\W*(yes|no)\b", re.I)
SPEC = re.compile(r"\bspecialist:([a-z0-9][a-z0-9-]*)")
TIMEOUT_S = 5.0
_LOCK = threading.Lock()
_PROCS: dict = {}
_MAP: dict = {}


def _load_map():
    if not _MAP:
        try:
            m = json.load(open(os.path.join(PROVED, "PROVED.json"), encoding="utf-8"))
            _MAP.update(m.get("specialists", {}))
            _MAP["__ok__"] = True
        except (OSError, ValueError):
            _MAP["__ok__"] = False
    return _MAP


def _runnable(binary):
    """the kernel binary, made executable in the state folder if the download lost its mode bit"""
    p = os.path.join(PROVED, "bin", binary)
    if not os.path.isfile(p):
        return None
    if os.access(p, os.X_OK):
        return p
    d = os.path.join(os.environ.get("ORACLE7_STATE", os.path.expanduser("~/.oracle7")), "proved_bin")
    os.makedirs(d, exist_ok=True)
    q = os.path.join(d, binary)
    if not os.path.isfile(q) or os.path.getsize(q) != os.path.getsize(p):
        shutil.copyfile(p, q)
    os.chmod(q, 0o755)
    return q


def _ask(sid, text):
    """one question to the kernel standing in for specialist sid; None when there is no answer to compare"""
    if platform.system() != "Linux" or platform.machine() not in ("x86_64", "AMD64"):
        return None
    m = _load_map()
    ent = m.get(sid) if m.get("__ok__") else None
    if not ent:
        return None
    key = (ent["binary"], sid if ent.get("flag", True) else "")
    with _LOCK:
        p = _PROCS.get(key)
        if p is None or p.poll() is not None:
            exe = _runnable(ent["binary"])
            if not exe:
                return None
            argv = [exe] + (["--specialist", sid] if ent.get("flag", True) else [])
            try:
                p = subprocess.Popen(argv, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, bufsize=1)
            except OSError:
                return None
            _PROCS[key] = p
        try:
            p.stdin.write(json.dumps({"id": "w551", "q": text}) + "\n")
            p.stdin.flush()
            out = [None]
            t = threading.Thread(target=lambda: out.__setitem__(0, p.stdout.readline()))
            t.start()
            t.join(TIMEOUT_S)
            if t.is_alive() or not out[0]:
                p.kill()
                _PROCS.pop(key, None)
                return None
            return json.loads(out[0])
        except (OSError, ValueError, BrokenPipeError):
            _PROCS.pop(key, None)
            return None


def _first(text):
    m = NUM.search(str(text or ""))
    if not m:
        return None, None
    s = m.group(0).replace(",", "")
    try:
        return float(s), (len(s.split(".")[1]) if "." in s else 0)
    except ValueError:
        return None, None


def agrees(reply_text, kernel_text):
    """same Yes/No opening (if either opens with one) and the same first stand-alone number within display rounding"""
    a, b = YESNO.match(str(reply_text or "")), YESNO.match(str(kernel_text or ""))
    if (a or b) and not (a and b and a.group(1).lower() == b.group(1).lower()):
        return False
    x, dx = _first(reply_text)
    y, _ = _first(kernel_text)
    if x is None or y is None:
        return (x is None) == (y is None)
    return abs(x - y) <= max(10 ** -dx, 0.005 * max(abs(x), abs(y)), 1e-12)


class OracleReleaseRuntimeW551(_Base):
    def chat(self, text: str, session_id: str = "default") -> dict:
        r = super().chat(text, session_id)
        if not isinstance(r, dict) or r.get("status") != "answered":
            return r
        path = str(r.get("path", ""))
        ids = SPEC.findall(path)
        if len(set(ids)) != 1 or path.startswith("network"):
            return r                                     # one named specialist only; chained network answers are not checked here
        k = _ask(ids[0], text)
        if not k or k.get("status") != "answered" or not k.get("response"):
            return r
        prov = k.get("provenance") or {}
        if agrees(r.get("response", ""), k.get("response", "")):
            out = dict(r)
            out["path"] = path + ">proved:" + str(prov.get("session", "veri7vn"))
            out["proved"] = {"kernel": prov.get("kernel"), "session": prov.get("session"), "theorems": prov.get("theorems", []),
                             "source": "veri7vn (Isabelle/HOL, CC0, ember arlynx)"}
            return out
        out = dict(r)
        out.update(status="withheld", path="proved_check:disagree>" + path,
                   response="A proved check (a veri7vn kernel, verified in Isabelle/HOL) gave a different answer to this question, so I won't give either as the answer.")
        return out
