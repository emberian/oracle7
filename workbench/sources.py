"""sources - specialists made from things you point the Workbench at, with no programming:

  Scan this computer   reads this machine (system, CPU, memory, disks, uptime, the processes using the most memory)
  Connect a server     reads a server over SSH with your own key: a fixed list of read-only commands, nothing else runs
  Add files            reads your tables (.csv/.tsv) and text (.txt/.md) and answers from them, quoting the place it read

Each becomes a SOURCE READER: it answers only by reading its source at question time, and every answer names where the
value was read (the call, the command, the file and row or line). It never infers past what it read. Like every
specialist it only fills the core's declines. Its check is automatic (exam.run_source): it must stay in its lane on the
core panel, leave identity questions alone, answer within budget, and read its own source back correctly.

Privacy: a scan reads system figures and process NAMES (never file contents, documents or browsing). Server readings come
from commands listed in SERVER_SCRIPT below. Files you add are copied into the specialist's own folder. Nothing is sent
anywhere; the Workbench answers on 127.0.0.1 only."""
from __future__ import annotations

import csv
import os
import platform
import re
import shutil
import socket
import subprocess
import sys
import time
from pathlib import Path

STOP = set("the a an of in on at to is was were are be by for with from and or what which who whom whose where when why how "
           "did does do it its this that these those i you he she they we my your his her their our me him them as than then "
           "there here can could would should will shall may might must much many most more about into over after before "
           "tell give find please say says said any some all have has had".split())


def gb(x):
    return "%.1f GB" % (x / 1e9)


def dur(s):
    d, s = divmod(int(s), 86400)
    h, s = divmod(s, 3600)
    m = s // 60
    return ("%d days " % d if d else "") + "%d h %d min" % (h, m)


# ---------------------------------------------------------------- this computer
def _run(cmd, timeout=8):
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout).stdout
    except Exception:  # noqa: BLE001
        return ""


def scan_local():
    """readings: (entity, signal, value, text, source). Uses psutil when installed, else the platform's own calls."""
    R, now = [], time.strftime("%H:%M:%S")
    add = lambda e, s, v, t, src: R.append({"entity": e, "signal": s, "value": v, "text": t, "source": "%s at %s" % (src, now)})
    add("system", "os", platform.platform(), platform.platform(), "platform.platform()")
    add("system", "hostname", socket.gethostname(), socket.gethostname(), "socket.gethostname()")
    add("cpu", "cores", os.cpu_count(), "%s logical cores" % os.cpu_count(), "os.cpu_count()")
    try:
        import psutil  # optional
    except Exception:  # noqa: BLE001
        psutil = None
    if psutil:
        vm = psutil.virtual_memory()
        add("memory", "used", vm.used, "%s used of %s (%.0f%%), %s available" % (gb(vm.used), gb(vm.total), vm.percent, gb(vm.available)), "psutil.virtual_memory()")
        add("cpu", "load", psutil.cpu_percent(interval=0.5), "CPU %.0f%% busy over half a second" % psutil.cpu_percent(interval=None), "psutil.cpu_percent()")
        add("system", "uptime", time.time() - psutil.boot_time(), "up %s" % dur(time.time() - psutil.boot_time()), "psutil.boot_time()")
    elif sys.platform == "win32":
        import ctypes

        class MS(ctypes.Structure):
            _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong), ("ullTotalPhys", ctypes.c_ulonglong),
                        ("ullAvailPhys", ctypes.c_ulonglong), ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                        ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong), ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
        ms = MS()
        ms.dwLength = ctypes.sizeof(MS)
        if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(ms)):
            used = ms.ullTotalPhys - ms.ullAvailPhys
            add("memory", "used", used, "%s used of %s (%d%%), %s available" % (gb(used), gb(ms.ullTotalPhys), ms.dwMemoryLoad, gb(ms.ullAvailPhys)),
                "GlobalMemoryStatusEx")
        up = ctypes.windll.kernel32.GetTickCount64() / 1000
        add("system", "uptime", up, "up %s" % dur(up), "GetTickCount64")
    else:
        try:
            mi = dict(re.findall(r"^(\w+):\s+(\d+)", Path("/proc/meminfo").read_text(), re.M))
            tot, av = int(mi["MemTotal"]) * 1024, int(mi.get("MemAvailable", mi["MemFree"])) * 1024
            add("memory", "used", tot - av, "%s used of %s (%.0f%%), %s available" % (gb(tot - av), gb(tot), 100 * (tot - av) / tot, gb(av)), "/proc/meminfo")
            up = float(Path("/proc/uptime").read_text().split()[0])
            add("system", "uptime", up, "up %s" % dur(up), "/proc/uptime")
        except Exception:  # noqa: BLE001
            pass
        try:
            l1, l5, l15 = os.getloadavg()
            add("cpu", "load", l1, "load average %.2f, %.2f, %.2f (1, 5, 15 min) on %s cores" % (l1, l5, l15, os.cpu_count()), "os.getloadavg()")
        except Exception:  # noqa: BLE001
            pass
    # disks
    mounts = []
    if sys.platform == "win32":
        mounts = ["%s:\\" % c for c in "CDEFGHIJKLMNOPQRSTUVWXYZ" if os.path.exists("%s:\\" % c)]
    else:
        try:
            for line in Path("/proc/mounts").read_text().splitlines():
                dev, mnt, fs = line.split()[:3]
                if dev.startswith("/dev/") and fs not in ("squashfs", "tmpfs", "overlay") and "/snap/" not in mnt:
                    mounts.append(mnt)
        except Exception:  # noqa: BLE001
            mounts = ["/"]
    for m in dict.fromkeys(mounts):
        try:
            u = shutil.disk_usage(m)
            add("disk " + m, "free", u.free, "%s has %s free of %s (%.0f%% used)" % (m, gb(u.free), gb(u.total), 100 * u.used / u.total),
                "shutil.disk_usage(%r)" % m)
        except Exception:  # noqa: BLE001
            pass
    # processes using the most memory (names only)
    top = []
    if psutil:
        ps = []
        for p in psutil.process_iter(["name", "memory_info"]):
            try:
                ps.append((p.info["memory_info"].rss, p.info["name"]))
            except Exception:  # noqa: BLE001
                pass
        top = sorted(ps, reverse=True)[:6]
        src = "psutil.process_iter()"
    elif sys.platform == "win32":
        agg = {}
        for row in csv.reader(_run(["tasklist", "/fo", "csv", "/nh"]).splitlines()):
            if len(row) >= 5:
                kb = int(re.sub(r"\D", "", row[4]) or 0) * 1024
                agg[row[0]] = agg.get(row[0], 0) + kb
        top = sorted(((v, k) for k, v in agg.items()), reverse=True)[:6]
        src = "tasklist"
    else:
        agg = {}
        for line in _run(["ps", "-eo", "rss=,comm="]).splitlines():
            parts = line.split(None, 1)
            if len(parts) == 2 and parts[0].isdigit():
                agg[parts[1].strip()] = agg.get(parts[1].strip(), 0) + int(parts[0]) * 1024
        top = sorted(((v, k) for k, v in agg.items()), reverse=True)[:6]
        src = "ps -eo rss,comm"
    if top:
        add("processes", "top_memory", top[0][1], "using the most memory: " + ", ".join("%s %s" % (n, gb(b)) for b, n in top), src)
    return R


# ---------------------------------------------------------------- a server over SSH (read-only, fixed commands)
SERVER_SCRIPT = r"""
echo '@@host'; hostname
echo '@@os'; (. /etc/os-release 2>/dev/null && echo "$PRETTY_NAME") ; uname -sr
echo '@@uptime'; cat /proc/uptime
echo '@@cores'; nproc
echo '@@load'; cat /proc/loadavg
echo '@@mem'; grep -E '^(MemTotal|MemAvailable):' /proc/meminfo
echo '@@disk'; df -P -B1 -x tmpfs -x devtmpfs -x squashfs -x overlay 2>/dev/null | tail -n +2
echo '@@top'; ps -eo rss=,comm= --sort=-rss 2>/dev/null | head -6
echo '@@failed'; systemctl --failed --no-legend --plain 2>/dev/null | awk '{print $1}' | head -20
echo '@@end'
"""
HOST = re.compile(r"^[A-Za-z0-9.\-:\[\]]{1,253}$")
USER = re.compile(r"^[a-z_][a-z0-9_\-]{0,31}$")


def scan_server(host, user, port=22, key=""):
    if not HOST.match(host) or not USER.match(user) or not (0 < int(port) < 65536):
        raise ValueError("host, user or port is not valid")
    cmd = ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=8", "-o", "StrictHostKeyChecking=accept-new", "-p", str(int(port))]
    if key:
        k = Path(key).expanduser()
        if not k.is_file():
            raise ValueError("no key file at %s" % k)
        cmd += ["-i", str(k)]
    cmd += ["%s@%s" % (user, host), "sh", "-s"]
    try:
        r = subprocess.run(cmd, input=SERVER_SCRIPT, capture_output=True, text=True, timeout=25)
    except FileNotFoundError:
        raise ValueError("no ssh command on this computer (Windows: Settings > Apps > Optional features > OpenSSH Client)")
    except subprocess.TimeoutExpired:
        raise ValueError("the server did not answer within 25 s")
    if "@@end" not in r.stdout:
        raise ValueError("could not read the server: " + (r.stderr.strip().splitlines() or ["no output"])[-1][:200])
    sec, cur = {}, None
    for line in r.stdout.splitlines():
        if line.startswith("@@"):
            cur = line[2:]
            sec[cur] = []
        elif cur:
            sec[cur].append(line)
    now, R, name = time.strftime("%H:%M:%S"), [], host
    add = lambda e, s, v, t, c: R.append({"entity": e, "signal": s, "value": v, "text": t, "source": "ssh %s: %s at %s" % (name, c, now)})
    if sec.get("host"):
        add("system", "hostname", sec["host"][0], sec["host"][0], "hostname")
    if sec.get("os"):
        add("system", "os", " / ".join(x for x in sec["os"] if x), " / ".join(x for x in sec["os"] if x), "os-release, uname -sr")
    try:
        up = float(sec["uptime"][0].split()[0])
        add("system", "uptime", up, "up %s" % dur(up), "/proc/uptime")
    except Exception:  # noqa: BLE001
        pass
    try:
        l1, l5, l15 = map(float, sec["load"][0].split()[:3])
        cores = int(sec["cores"][0])
        add("cpu", "cores", cores, "%d cores" % cores, "nproc")
        add("cpu", "load", l1, "load average %.2f, %.2f, %.2f (1, 5, 15 min) on %d cores" % (l1, l5, l15, cores), "/proc/loadavg")
    except Exception:  # noqa: BLE001
        pass
    try:
        mi = dict(re.findall(r"^(\w+):\s+(\d+)", "\n".join(sec["mem"]), re.M))
        tot, av = int(mi["MemTotal"]) * 1024, int(mi["MemAvailable"]) * 1024
        add("memory", "used", tot - av, "%s used of %s (%.0f%%), %s available" % (gb(tot - av), gb(tot), 100 * (tot - av) / tot, gb(av)), "/proc/meminfo")
    except Exception:  # noqa: BLE001
        pass
    for line in sec.get("disk", []):
        p = line.split()
        if len(p) >= 6 and p[1].isdigit():
            tot, used, free, mnt = int(p[1]), int(p[2]), int(p[3]), p[5]
            add("disk " + mnt, "free", free, "%s has %s free of %s (%.0f%% used)" % (mnt, gb(free), gb(tot), 100 * used / max(1, tot)), "df -P")
    top = [(int(a.split(None, 1)[0]) * 1024, a.split(None, 1)[1]) for a in sec.get("top", []) if a.strip() and a.split()[0].isdigit()]
    if top:
        add("processes", "top_memory", top[0][1], "using the most memory: " + ", ".join("%s %s" % (n, gb(b)) for b, n in top), "ps --sort=-rss")
    failed = [x for x in sec.get("failed", []) if x.strip()]
    add("services", "failed", len(failed), ("%d failed services: %s" % (len(failed), ", ".join(failed))) if failed else "no failed services",
        "systemctl --failed")
    return R


# ---------------------------------------------------------------- the machine reader (this computer or a server)
ASK = [  # (question words, entity prefix, signal) - the more specific first
    (r"\b(using the most|biggest|heaviest|hogging|top) (?:memory|process|program|app)|\bwhat(?:'s| is) (?:using|eating)\b", "processes", "top_memory"),
    (r"\b(uptime|been (?:up|on|running)|up for|since (?:it|the last) (?:booted|restart)|rebooted|restarted|last boot)\b", "system", "uptime"),
    (r"\b(disk|drive|space|storage|full)\b", "disk", "free"),
    (r"\b(memory|ram)\b", "memory", "used"),
    (r"\b(cpu|processor|load|busy)\b", "cpu", "load"),
    (r"\b(cores?|threads?)\b", "cpu", "cores"),
    (r"\b(operating system|os version|which os|what os|windows version|linux version|distro)\b", "system", "os"),
    (r"\b(hostname|host name|computer name|machine name)\b", "system", "hostname"),
    (r"\bfailed services?\b|\bservices? (?:failed|failing|down)\b", "services", "failed"),
]


class MachineOrgan:
    """answers questions about one machine by reading it live (cached 20 s); names the call or command it read"""

    def __init__(self, target="local", name="this computer", host="", user="", port=22, key=""):
        self.target, self.name, self.host, self.user, self.port, self.key = target, name, host, user, int(port or 22), key
        self.cache, self.t = None, 0
        words = [re.escape(w) for w in re.findall(r"[a-z0-9]+", name.lower()) if w not in STOP]
        self.named = re.compile(r"\b(%s)\b" % r"\W*".join(words), re.I) if words else None

    def readings(self):
        if self.cache is None or time.time() - self.t > 20:
            self.cache = scan_local() if self.target == "local" else scan_server(self.host, self.user, self.port, self.key)
            self.t = time.time()
        return self.cache

    def answer(self, text, session):
        t = str(text or "")
        if self.target == "local":
            if not re.search(r"\b(my|this) (computer|pc|laptop|machine|desktop|mac|system)\b|\bon (my|this) (computer|pc|laptop|machine)\b", t, re.I):
                return None
        elif not (self.named and self.named.search(t)):
            return None
        hits = [(e, s) for pat, e, s in ASK if re.search(pat, t, re.I)]
        if not hits:
            return None
        e, s = hits[0]
        rows = [r for r in self.readings() if r["entity"].startswith(e) and r["signal"] == s]
        if not rows:
            return {"kind": "unreadable", "status": "withheld", "response": "I could not read that on %s." % self.name}
        if e == "disk":
            m = re.search(r"\b([a-z]):", t, re.I) or re.search(r"(/[\w/.-]*)", t)
            if m:
                want = (m.group(1).upper() + ":\\") if len(m.group(1)) == 1 else m.group(1)
                rows = [r for r in rows if r["entity"] == "disk " + want] or rows
        body = "; ".join(r["text"] for r in rows[:8])
        srcs = "; ".join(dict.fromkeys(r["source"] for r in rows[:8]))
        return {"kind": "reading", "status": "answered", "subject": "my computer" if self.target == "local" else self.name,
                "response": "%s: %s. Read from %s." % (self.name[:1].upper() + self.name[1:], body, srcs)}


# ---------------------------------------------------------------- your files
def _words(s):
    return [w for w in re.findall(r"[a-z0-9][a-z0-9'.-]*", s.lower()) if w not in STOP]


class FilesOrgan:
    """answers from files in its folder's files/ directory.
    TABLES: a question that names a row (its first-column value, or any cell that is unique in its column) and a column
    header gets that cell, with file, row and column. TEXT: a question that says "my notes / my files / my documents /
    according to <name>" gets the sentence that shares the most of its words, quoted with file and line."""

    def __init__(self, folder="files", name="your files"):
        base = Path(os.environ.get("ORACLE7_WORKBENCH_LOCAL", str(Path(__file__).resolve().parent / "local"))) / "specialists"
        self.dir = base / folder
        self.name = name
        self.loaded_at, self.tables, self.lines = 0, [], []

    def load(self):
        stamp = max([p.stat().st_mtime for p in self.dir.glob("*")] or [0])
        if stamp == self.loaded_at:
            return
        self.tables, self.lines = [], []
        for p in sorted(self.dir.glob("*")):
            try:
                if p.suffix.lower() in (".csv", ".tsv"):
                    with open(p, encoding="utf-8-sig", errors="replace", newline="") as fh:
                        rows = list(csv.reader(fh, delimiter="\t" if p.suffix.lower() == ".tsv" else ","))
                    if len(rows) >= 2:
                        self.tables.append((p.name, rows[0], rows[1:]))
                elif p.suffix.lower() in (".txt", ".md"):
                    for i, line in enumerate(p.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
                        for sent in re.split(r"(?<=[.!?])\s+", line.strip()):
                            if len(sent) > 12:
                                self.lines.append((p.name, i, sent))
            except Exception:  # noqa: BLE001
                pass
        self.loaded_at = stamp

    def answer(self, text, session):
        self.load()
        t = str(text or "")
        tl = " %s " % " ".join(re.findall(r"[a-z0-9][a-z0-9'.-]*", t.lower()))
        best = None
        for fname, hdr, rows in self.tables:
            cols = [(j, h) for j, h in enumerate(hdr) if j > 0 and h.strip() and " %s " % " ".join(_words(h)) in tl and _words(h)]
            if not cols:
                continue
            for k in range(len(hdr)):
                vals = [r[k].strip() for r in rows if k < len(r)]
                for n, r in enumerate(rows, 2):
                    if k < len(r) and r[k].strip() and vals.count(r[k].strip()) == 1 and len(r[k].strip()) > 1 and \
                            " %s " % " ".join(re.findall(r"[a-z0-9][a-z0-9'.-]*", r[k].lower())) in tl:
                        for j, h in cols:
                            if j != k and j < len(r) and r[j].strip():
                                cand = (len(h) + len(r[k]), fname, n, h, r[k].strip(), r[j].strip())
                                best = max(best, cand) if best else cand
        if best:
            _, fname, n, h, key, val = best
            return {"kind": "from_file", "status": "answered", "subject": key,
                    "response": "%s. From %s, row %d (%s), column \"%s\"." % (val, fname, n, key, h)}
        if self.lines and re.search(r"\b(my|our) (notes|files?|documents?|docs|records|manual|handbook)\b|\baccording to\b", t, re.I):
            q = set(_words(t)) - {"notes", "note", "file", "files", "document", "documents", "docs", "records", "according", "manual", "handbook"}
            scored = sorted(((len(q & set(_words(s))), -len(s), f, i, s) for f, i, s in self.lines), reverse=True)
            if scored and scored[0][0] >= 2:
                k, _, f, i, s = scored[0]
                return {"kind": "from_file", "status": "answered", "response": "\"%s\" (%s, line %d)" % (s, f, i)}
            return {"kind": "not_in_files", "status": "withheld", "response": "Nothing in %s says that." % self.name}
        return None



# ---------------------------------------------------------------- a conversation, kept as a temporary specialist
RECALL = re.compile(r"\b(earlier|before|previously|last time|you (?:said|told me|mentioned|answered)|we (?:talked|discussed|said|covered)|"
                    r"remind me|in (?:this|our|that) (?:conversation|chat)|again|what was (?:the|your) answer)\b", re.I)


RECALL_FILLER = set("discuss discussed talk talked said say tell told mention mentioned earlier before previously remind again "
                    "answer answered conversation chat last time we".split())


class ConversationOrgan:
    """answers from one saved conversation: a question that asks to recall it ("what did you say earlier about the boiler?")
    or that repeats one of its questions gets the earlier answer, quoted with its date and the route that produced it.
    Only answered turns are kept as things it can recall; declines are not facts."""

    def __init__(self, conv="", name="this conversation"):
        base = Path(os.environ.get("ORACLE7_WORKBENCH_LOCAL", str(Path(__file__).resolve().parent / "local")))
        self.path, self.name, self.loaded_at, self.turns = base / "conversations" / ("%s.json" % re.sub(r"[^a-z0-9]", "", conv)), name, 0, []

    def load(self):
        try:
            st = self.path.stat().st_mtime
        except OSError:
            self.turns = []
            return
        if st != self.loaded_at:
            import json
            d = json.loads(self.path.read_text(encoding="utf-8"))
            self.turns = [t for t in d.get("turns", []) if t.get("status") == "answered" and not str(t.get("path", "")).startswith("workbench:")]
            self.loaded_at = st

    def best(self, text):
        q = set(_words(text)) - RECALL_FILLER
        scored = []
        for t in self.turns:
            tq, ta = set(_words(t["q"])), set(_words(t.get("response", "")))
            scored.append((len(q & tq), len(q & (tq | ta)), -t.get("t", 0), t))
        scored.sort(key=lambda x: x[:3], reverse=True)
        return scored[0] if scored else None

    def takes(self, text):
        """only a question that asks to RECALL this conversation, and shares a content word with one of its answered turns;
        a repeated question is not taken - the core answers it fresh, in its own context"""
        if not RECALL.search(str(text or "")):
            return False
        self.load()
        b = self.best(text)
        return bool(b) and b[1] >= 1

    def answer(self, text, session):
        if not self.takes(text):
            return None
        _, _, _, t = self.best(text)
        when = time.strftime("%d %b %Y %H:%M", time.localtime(t.get("t", 0)))
        return {"kind": "recalled", "status": "answered",
                "response": "Earlier in \"%s\" (%s) you asked \"%s\". The answer then was: %s [route: %s]"
                            % (self.name, when, t["q"], str(t.get("response", "")).strip(), str(t.get("path", ""))[:80])}
