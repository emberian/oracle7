#!/usr/bin/env python3
"""oracle7 - run Oracle7 on your own machine (CPU only).

  python oracle7.py "Who wrote Leaves of Grass?"      one question
  python oracle7.py --repl                            ask in a loop (one session, so follow-ups work)
  python oracle7.py --serve [port]                    local HTTP: POST /chat {"text": "..."} -> {"response", "path", "status"}
  python oracle7.py --workbench [port]                the Workbench: a local page with the diagram, your specialists,
                                                      scan / connect / files / sensors, exams, code and film (workbench/README.md)

Commands (python oracle7.py help lists them all; add --json for machine-readable output):
  ask "question"        the answer, its status and the path it took      chat                a conversation in the terminal
  specialists [word]    the 267 specialists with held-out scores          card <id>           one specialist's card
  verify [--chain]      check this install against RELEASE_HASHES.json   systems             the five systems
  new <id> / example / exam <id> dev|heldout / mine                       build and examine your own specialists
  scan / sensors / sensor-test <kind> <address>                           read this computer and your sensors
  history [id]          saved conversations                               serve / workbench / setup
  python oracle7.py --setup                           unpack + verify the stores (runs automatically on first use)

Every answer carries its `path`: the route and specialists that produced it. A `withheld` status is Oracle7 declining:
it would rather say it can't answer than guess. ORACLE7_ROOT moves the data root (default ./root); ORACLE7_STATE moves the
conversation state (default ./root/state), e.g. one directory per process."""
import importlib
import json
import os
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

sys.setrecursionlimit(20000)  # the admitted fold chain is >250 modules deep, as on the served harness
HERE = Path(__file__).resolve().parent
ROOT = Path(os.environ.get("ORACLE7_ROOT", str(HERE / "root"))).resolve()
os.environ["ORACLE7_ROOT"] = str(ROOT)
PH = ROOT / "fable-content" / "oracle-m-series-2026-08-15"

# the gate measures the core with a fixed hash seed; run the same way (re-exec once if needed)
if __name__ == "__main__" and os.environ.get("PYTHONHASHSEED") != "0":
    os.environ.update(PYTHONHASHSEED="0", PYTHONIOENCODING="utf-8")
    os.execv(sys.executable, [sys.executable, os.path.abspath(__file__)] + sys.argv[1:])

# the full release carries the deep Wikipedia/DBpedia/OpenStax stores and runs with them exactly as the gate does; slim
# leaves them unset, where each store-reading fold is documented to behave exactly as its parent
_full = {
    "ORACLE_BENCH_BUILD": PH / "m13e7_dbpedia_openstax_full_fable_bench_a_v1" / "wikipedia_specialist.sqlite3",
    "ORACLE_WIKIPEDIA_BUILD": PH / "m13e7_wiki_openstax_full_fable_build_a_v1",
    "ORACLE_DEEP_BUILD": PH / "m13e8_dbpedia_enslot_openstax_full_fable_bench_a_v1" / "wikipedia_specialist.sqlite3",
}
VARIANT = (ROOT / "VARIANT").read_text().strip() if (ROOT / "VARIANT").exists() else "slim"
if VARIANT == "full":
    for k, v in _full.items():
        os.environ.setdefault(k, str(v))
os.environ["NLTK_DATA"] = os.pathsep.join(x for x in (str(ROOT / "nltk_data"), os.environ.get("NLTK_DATA")) if x)
# conversation state (sessions, memory of this install): ORACLE7_STATE puts it elsewhere, e.g. one dir per process
STATE = Path(os.environ.get("ORACLE7_STATE", str(ROOT / "state"))).resolve()
STATE.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(ROOT / "wander-train"))
sys.path.insert(0, str(PH / "self_loop" / "admitted"))


def setup():
    """first run: unpack the zstd-packed stores (PACK_MANIFEST.json) and verify each is byte-identical to what was measured"""
    import hashlib
    import shutil
    import subprocess
    man = HERE / "PACK_MANIFEST.json"
    if not man.exists():
        return
    todo = [e for e in json.load(open(man))["files"] if not (HERE / e["path"]).exists()]
    for i, e in enumerate(todo, 1):
        dst, zst = HERE / e["path"], HERE / (e["path"] + ".zst")
        print("[setup %d/%d] unpacking %s (%.0f MB)" % (i, len(todo), e["path"], e["size"] / 2**20), flush=True)
        tmp = dst.with_name(dst.name + ".part")
        try:
            import zstandard
            with open(zst, "rb") as fi, open(tmp, "wb") as fo:
                zstandard.ZstdDecompressor(max_window_size=2**27).copy_stream(fi, fo)
        except ImportError:
            if not shutil.which("zstd"):
                sys.exit("setup needs zstd: pip install zstandard (or install the zstd command)")
            subprocess.run(["zstd", "-q", "-d", "--long=27", str(zst), "-o", str(tmp)], check=True)
        h = hashlib.sha256()
        with open(tmp, "rb") as fh:
            for b in iter(lambda: fh.read(1 << 24), b""):
                h.update(b)
        if h.hexdigest() != e["sha256"]:
            tmp.unlink()
            sys.exit("setup: %s does not match its published hash; re-download it" % e["path"])
        tmp.rename(dst)
        zst.unlink()
    if todo:
        print("[setup] done: all stores verified", flush=True)


def load():
    setup()
    tip = json.load(open(PH / "self_loop" / "admitted" / "HEAD_MANIFEST.json"))["tip"]
    mod = importlib.import_module(tip)
    cls = getattr(mod, sorted(x for x in dir(mod) if x.startswith("OracleReleaseRuntimeW"))[-1])
    return tip, cls(state_root=STATE / "runtime", wikipedia_build=PH / "m13e5_simplewiki_build_a_v1")


class Engine:
    """thread-safe front door: the runtime's stores are bound to the thread that opened them, so the runtime is built on, and
    every turn runs on, one dedicated thread (servers and UIs call chat() from any thread; turns are answered in order)"""

    def __init__(self):
        from concurrent.futures import ThreadPoolExecutor
        self._ex = ThreadPoolExecutor(max_workers=1, thread_name_prefix="oracle7")
        self.tip, self._rt = self._ex.submit(load).result()

    def chat(self, text: str, session_id: str = "default") -> dict:
        return self._ex.submit(self._rt.chat, text, session_id).result()


def show(r):
    print(str(r.get("response", "")).strip())
    print("  [%s] path: %s" % (r.get("status"), r.get("path")))


def main():
    a = sys.argv[1:]
    if a[:1] == ["--setup"]:
        setup()
        return
    if not a or a[0] in ("-h", "--help"):
        print(__doc__)
        return
    if a and a[0] in ("serve", "workbench", "setup", "repl"):
        a[0] = "--" + a[0]
        if a[0] == "--setup":
            setup()
            return
    sys.path.insert(0, str(HERE / "workbench"))
    try:
        import cli
    except ImportError:
        cli = None
    if cli is not None and a and a[0] in cli.COMMANDS:
        if a[0] not in ("help", "specialists", "card", "systems", "verify", "mine", "new", "example", "scan", "sensor-test", "history"):
            setup()
        sys.exit(cli.main(a, Engine))
    if a[0] == "--workbench":
        sys.path.insert(0, str(HERE / "workbench"))
        import server as workbench
        eng = Engine()
        port = int(a[1]) if len(a) > 1 else 8177
        url = "http://127.0.0.1:%d/" % port
        if os.environ.get("ORACLE7_NO_BROWSER") != "1":
            import threading
            import webbrowser
            threading.Timer(1.5, lambda: webbrowser.open(url)).start()
        workbench.serve(eng, port)
        return
    if a[0] == "--serve":
        eng = Engine()
        tip, rt = eng.tip, eng
    else:
        tip, rt = load()
    if a[0] == "--repl":
        print("Oracle7 (%s). Ask anything; Ctrl+C to quit." % tip)
        while True:
            try:
                q = input("> ").strip()
            except (EOFError, KeyboardInterrupt):
                return
            if q:
                show(rt.chat(q, session_id="repl"))
    elif a[0] == "--serve":
        port = int(a[1]) if len(a) > 1 else 8077

        class H(BaseHTTPRequestHandler):
            def do_POST(self):  # noqa: N802
                if self.path.rstrip("/") != "/chat":
                    self.send_error(404)
                    return
                n = int(self.headers.get("Content-Length", "0"))
                d = json.loads(self.rfile.read(min(n, 20000)) or b"{}")
                r = rt.chat(str(d.get("text", ""))[:4000], session_id=str(self.headers.get("X-Oracle-Session", "http"))[:64])
                b = json.dumps({k: r.get(k) for k in ("response", "path", "status", "references")}, default=str).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(b)))
                self.end_headers()
                self.wfile.write(b)

            def log_message(self, *x):
                pass
        print("Oracle7 (%s) on http://127.0.0.1:%d/chat" % (tip, port))
        ThreadingHTTPServer(("127.0.0.1", port), H).serve_forever()
    else:
        show(rt.chat(" ".join(a), session_id="cli"))


if __name__ == "__main__":
    main()
