"""mcp - connect the Workbench to MCP servers and turn their tools into an ADAPTIVE specialist.

Connect a server by command (stdio: the Workbench starts it, e.g. `npx -y @modelcontextprotocol/server-filesystem ~/Documents`)
or by URL (streamable HTTP, with an optional bearer token). The Workbench lists its tools; you pick the ones the specialist may
use and, optionally, give example questions. The specialist (McpOrgan):

  ROUTES   a question to the tool whose name, description and learned words it shares the most distinctive words with
           (at least two, or the server's own name plus one), and declines otherwise;
  FILLS    the tool's required arguments from the question (quoted text, a number, a name, the phrase after for/about/in/of);
           if a required argument is missing it says which one instead of guessing;
  ANSWERS  with the tool's own result and a receipt: server, tool and the exact arguments it sent;
  ADAPTS   from your marks: a right answer adds the question's words to that tool's learned words; a wrong one counts against
           them, and a tool with 3+ wrongs and more wrongs than rights stops being used until you reset it.

Like every specialist it only fills the core's declines, and its automatic check (lane, self, budget, your examples) runs
again after you mark answers, so learning can never quietly widen it past the lane cap. The check of the lane asks only
WHETHER it would take each of the 924 general questions (takes()), so no tool is called for it.
Questions you route to a server are sent to that server: connect only servers you trust."""
from __future__ import annotations

import json
import os
import queue
import re
import shlex
import shutil
import subprocess
import threading
import time
import urllib.request
from pathlib import Path

LOCAL = Path(os.environ.get("ORACLE7_WORKBENCH_LOCAL", str(Path(__file__).resolve().parent / "local")))
CONF = LOCAL / "mcp.json"
STOP = set("the a an of in on at to is was were are be by for with from and or what which who whom whose where when why how "
           "did does do it its this that these those i you he she they we my your his her their our me him them as than then "
           "there here can could would should will shall may might must much many most more about into over after before "
           "tell give find please get show list use using any some all have has had want need".split())
_LIVE = {}
_LOCK = threading.Lock()


def words(s):
    out = []
    for w in re.findall(r"[A-Za-z][A-Za-z0-9]*", re.sub(r"([a-z])([A-Z])", r"\1 \2", str(s or ""))):
        w = w.lower()
        if w not in STOP and len(w) > 2:
            out.append(w[:-1] if w.endswith("s") and len(w) > 4 else w)
    return out


def servers():
    try:
        return json.loads(CONF.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return {}


def save_server(name, cfg):
    s = servers()
    s[name] = cfg
    CONF.write_text(json.dumps(s, indent=1), encoding="utf-8")


class Client:
    """one MCP connection (stdio or streamable HTTP), JSON-RPC 2.0"""

    def __init__(self, cfg):
        self.cfg, self.n, self.proc, self.sid, self.q = cfg, 0, None, None, queue.Queue()
        if cfg.get("command"):
            parts = shlex.split(cfg["command"], posix=os.name != "nt")
            exe = shutil.which(parts[0]) or parts[0]
            self.proc = subprocess.Popen([exe] + parts[1:], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                                         text=True, encoding="utf-8", bufsize=1)
            threading.Thread(target=self._reader, daemon=True).start()
        self.call("initialize", {"protocolVersion": "2025-03-26", "capabilities": {},
                                 "clientInfo": {"name": "oracle7-workbench", "version": "1.0"}})
        self.notify("notifications/initialized")

    def _reader(self):
        for line in self.proc.stdout:
            line = line.strip()
            if line.startswith("{"):
                try:
                    self.q.put(json.loads(line))
                except Exception:  # noqa: BLE001
                    pass

    def _http(self, msg):
        h = {"Content-Type": "application/json", "Accept": "application/json, text/event-stream"}
        if self.cfg.get("token"):
            h["Authorization"] = "Bearer " + self.cfg["token"]
        if self.sid:
            h["Mcp-Session-Id"] = self.sid
        req = urllib.request.Request(self.cfg["url"], data=json.dumps(msg).encode(), headers=h, method="POST")
        with urllib.request.urlopen(req, timeout=60) as r:
            self.sid = r.headers.get("Mcp-Session-Id") or self.sid
            body = r.read().decode("utf-8", "replace")
            if "text/event-stream" in (r.headers.get("Content-Type") or ""):
                out = [json.loads(l[5:].strip()) for l in body.splitlines() if l.startswith("data:") and l[5:].strip().startswith("{")]
                return [m for m in out if m.get("id") == msg.get("id")] or out
            return [json.loads(body)] if body.strip() else []

    def notify(self, method, params=None):
        msg = {"jsonrpc": "2.0", "method": method, **({"params": params} if params else {})}
        if self.proc:
            self.proc.stdin.write(json.dumps(msg) + "\n")
            self.proc.stdin.flush()
        else:
            try:
                self._http(msg)
            except Exception:  # noqa: BLE001
                pass

    def call(self, method, params=None, timeout=60):
        self.n += 1
        msg = {"jsonrpc": "2.0", "id": self.n, "method": method, "params": params or {}}
        if self.proc:
            self.proc.stdin.write(json.dumps(msg) + "\n")
            self.proc.stdin.flush()
            t0 = time.time()
            while time.time() - t0 < timeout:
                try:
                    m = self.q.get(timeout=1)
                except queue.Empty:
                    if self.proc.poll() is not None:
                        raise ValueError("the MCP server stopped")
                    continue
                if m.get("id") == self.n:
                    return self._result(m)
            raise ValueError("the MCP server did not answer within %d s" % timeout)
        for m in self._http(msg):
            if m.get("id") == self.n:
                return self._result(m)
        raise ValueError("no reply from the MCP server")

    @staticmethod
    def _result(m):
        if "error" in m:
            raise ValueError("MCP error: %s" % (m["error"].get("message") if isinstance(m["error"], dict) else m["error"]))
        return m.get("result", {})

    def tools(self):
        return self.call("tools/list").get("tools", [])

    def close(self):
        if self.proc:
            self.proc.kill()


def client(name):
    with _LOCK:
        c = _LIVE.get(name)
        if c is None or (c.proc and c.proc.poll() is not None):
            cfg = servers().get(name)
            if not cfg:
                raise ValueError("no MCP server named %s" % name)
            c = _LIVE[name] = Client(cfg)
        return c


def connect(name, command="", url="", token=""):
    if not re.match(r"^[A-Za-z0-9 ._-]{1,40}$", name):
        raise ValueError("name the server with letters, digits, spaces, dots or hyphens")
    if bool(command) == bool(url):
        raise ValueError("give a command to start the server, or its URL - one of the two")
    if url and not re.match(r"^https?://", url):
        raise ValueError("the URL must start with http:// or https://")
    cfg = {"command": command} if command else {"url": url, **({"token": token} if token else {})}
    with _LOCK:
        old = _LIVE.pop(name, None)
    if old:
        old.close()
    save_server(name, cfg)
    tools = client(name).tools()
    return [{"name": t.get("name"), "description": (t.get("description") or "")[:300],
             "required": (t.get("inputSchema") or {}).get("required", []),
             "properties": list(((t.get("inputSchema") or {}).get("properties") or {}).keys())} for t in tools]


# ---------------------------------------------------------------- the adaptive specialist
class McpOrgan:
    def __init__(self, server, tools, name="", folder=""):
        self.server, self.allowed, self.name = server, list(tools), name or server
        base = LOCAL / "specialists"
        self.credit_path = base / folder / "credit.json" if folder else None
        self._schema = None
        self.server_words = set(words(server))

    def credit(self):
        try:
            return json.loads(self.credit_path.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            return {}

    def schema(self):
        if self._schema is None:
            self._schema = {t["name"]: t for t in client(self.server).tools() if t.get("name") in self.allowed}
        return self._schema

    def route(self, text):
        q = set(words(text))
        cr = self.credit()
        best = None
        for tname in self.allowed:
            c = cr.get(tname, {})
            if c.get("wrong", 0) >= 3 and c.get("wrong", 0) > c.get("right", 0):
                continue                                       # learned: this tool keeps being wrong
            t = (self._schema or {}).get(tname, {})
            vocab = set(words(tname)) | set(words(t.get("description", ""))[:40]) | set(c.get("learned", []))
            score = len(q & vocab) + (2 if q & self.server_words else 0)
            if score >= 2 and (best is None or score > best[0]):
                best = (score, tname)
        return best[1] if best else None

    def takes(self, text):
        try:
            self.schema()
        except Exception:  # noqa: BLE001
            pass
        return self.route(text) is not None

    @staticmethod
    def fill(text, schema):
        props = (schema.get("inputSchema") or {}).get("properties") or {}
        req = (schema.get("inputSchema") or {}).get("required") or []
        quoted = re.findall(r"[\"“']([^\"”']{1,200})[\"”']", text)
        nums = re.findall(r"-?\d+(?:\.\d+)?", text)
        names = re.findall(r"\b(?:[A-Z][\w.-]*(?:\s+[A-Z][\w.-]*)*)", text[1:])
        tail = re.search(r"\b(?:for|about|of|in|on|named|called|at)\s+(.+?)[?.!]*$", text, re.I)
        paths = re.findall(r"(?:[A-Za-z]:\\|~?/)[^\s\"']+", text)
        args, missing = {}, []
        for k in req:
            typ = (props.get(k) or {}).get("type", "string")
            kl = k.lower()
            if typ in ("number", "integer"):
                v = nums.pop(0) if nums else None
                v = (int(float(v)) if typ == "integer" else float(v)) if v is not None else None
            elif typ == "boolean":
                v = not re.search(r"\b(no|not|false|without)\b", text, re.I)
            elif "path" in kl or "file" in kl or "dir" in kl:
                v = paths.pop(0) if paths else (quoted.pop(0) if quoted else None)
            else:
                v = quoted.pop(0) if quoted else (tail.group(1).strip() if tail and kl in ("query", "q", "text", "search", "topic", "term", "keyword", "location", "city", "place", "name") else
                                                  (names.pop(0) if names else (tail.group(1).strip() if tail else None)))
            if v is None or v == "":
                missing.append(k)
            else:
                args[k] = v
        return args, missing

    def answer(self, text, session):
        t = str(text or "")
        try:
            sch = self.schema()
        except Exception as e:  # noqa: BLE001
            return {"kind": "underspecified", "status": "withheld", "response": "The MCP server %s is not reachable: %s" % (self.server, e)}
        tname = self.route(t)
        if not tname:
            return None
        args, missing = self.fill(t, sch[tname])
        if missing:
            return {"kind": "underspecified", "status": "withheld",
                    "response": "To use %s on %s I need: %s." % (tname, self.server, ", ".join(missing))}
        res = client(self.server).call("tools/call", {"name": tname, "arguments": args}, timeout=60)
        parts = [c.get("text", "") for c in res.get("content", []) if c.get("type") == "text"]
        body = ("\n".join(parts) or json.dumps(res.get("structuredContent") or res)[:1500]).strip()[:1500]
        if res.get("isError"):
            return {"kind": "underspecified", "status": "withheld", "response": "%s said: %s" % (tname, body[:300])}
        return {"kind": "tool_result", "status": "answered",
                "response": "%s\nFrom MCP server %s, tool %s(%s)." % (body, self.server, tname, json.dumps(args, ensure_ascii=False))}


def learn(credit_path, tool, question, right):
    try:
        c = json.loads(Path(credit_path).read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        c = {}
    e = c.setdefault(tool, {"right": 0, "wrong": 0, "learned": []})
    if right:
        e["right"] += 1
        e["learned"] = sorted(set(e["learned"]) | set(words(question)))[:200]
    else:
        e["wrong"] += 1
        e["learned"] = [w for w in e["learned"] if w not in set(words(question))]
    Path(credit_path).write_text(json.dumps(c, indent=1), encoding="utf-8")
    return e
