"""sensors - connect a sensor and ask about it. Every reading keeps its time, unit and source, and is tagged MEASURED or
SIMULATED. A reading outside the physical range of its quantity is rejected and said so, never used.

Connections (each one is read-only):
  http       a device or hub that serves JSON (ESP32, Shelly, Tasmota, Home Assistant, a weather station) or Prometheus
             text metrics; numeric fields are found by themselves and you pick which to keep
  mqtt       a topic on an MQTT broker (JSON or a plain number); MQTT 3.1.1, read-only subscribe, standard library only
  serial     a USB/serial device that prints lines ("temp=21.4 hum=40", "21.4,40" or JSON); needs `pip install pyserial`
             on Windows and macOS, reads the device file directly on Linux
  file       a log file a logger appends to (CSV with a header, JSON lines, or key=value lines); the newest line is read
  simulated  a made-up garden node (air temperature, humidity, soil moisture), for trying it without hardware; every answer
             from it says SIMULATED

Readings are polled in the background (default every 30 s) into workbench/local/sensors/<id>.jsonl, 24 hours kept. Nothing
is sent anywhere."""
from __future__ import annotations

import csv
import json
import math
import os
import re
import socket
import struct
import subprocess
import sys
import threading
import time
import urllib.request
from pathlib import Path

LOCAL = Path(os.environ.get("ORACLE7_WORKBENCH_LOCAL", str(Path(__file__).resolve().parent / "local")))
DIR = LOCAL / "sensors"
DIR.mkdir(parents=True, exist_ok=True)
KEEP_S = 24 * 3600

# quantity: (unit, low, high, words that name it in a field or a question)
QUANTITIES = {
    "temperature": ("°C", -60, 70, "temp temperature t_c tc air_temp celsius"),
    "humidity": ("%", 0, 100, "hum humidity rh relative_humidity"),
    "soil moisture": ("%", 0, 100, "soil moisture vwc soil_moisture"),
    "pressure": ("hPa", 800, 1100, "press pressure baro hpa"),
    "co2": ("ppm", 250, 10000, "co2 eco2 carbon_dioxide"),
    "light": ("lux", 0, 200000, "lux light illuminance illum"),
    "pm2.5": ("µg/m³", 0, 1000, "pm25 pm2_5 pm2.5 particulates"),
    "voltage": ("V", 0, 60, "volt voltage vbat battery_v vcc"),
    "battery": ("%", 0, 100, "battery batt battery_pct soc"),
    "wind speed": ("m/s", 0, 80, "wind wind_speed windspeed"),
    "rain": ("mm", 0, 500, "rain precip precipitation rainfall"),
    "power": ("W", 0, 100000, "power watt watts apower"),
    "energy": ("kWh", 0, 1e9, "energy kwh total_energy"),
    "water level": ("cm", -1000, 10000, "level water_level depth"),
}
ASKWORDS = {q: set(v[3].split()) | set(q.split()) for q, v in QUANTITIES.items()}
ASKWORDS["temperature"] |= {"hot", "cold", "warm", "temperature"}
ASKWORDS["humidity"] |= {"humid", "damp"}
ASKWORDS["soil moisture"] |= {"wet", "dry", "watering", "water"}


def guess_quantity(field):
    f = re.sub(r"[^a-z0-9]+", "_", field.lower())
    parts = set(f.split("_")) | {f}
    best = None
    for q, (_, _, _, words) in QUANTITIES.items():
        hit = parts & set(words.split())
        if hit and (best is None or len(max(hit, key=len)) > best[0]):
            best = (len(max(hit, key=len)), q)
    return best[1] if best else None


# ---------------------------------------------------------------- reading one value set from a source
def flatten(obj, prefix=""):
    out = {}
    if isinstance(obj, dict):
        for k, v in obj.items():
            out.update(flatten(v, "%s.%s" % (prefix, k) if prefix else str(k)))
    elif isinstance(obj, list):
        for i, v in enumerate(obj[:20]):
            out.update(flatten(v, "%s.%d" % (prefix, i) if prefix else str(i)))
    elif isinstance(obj, bool):
        pass
    elif isinstance(obj, (int, float)) and math.isfinite(obj):
        out[prefix or "value"] = float(obj)
    elif isinstance(obj, str) and re.fullmatch(r"-?\d+(?:\.\d+)?", obj.strip()):
        out[prefix or "value"] = float(obj)
    return out


def parse_line(s, header=None):
    s = s.strip()
    if not s:
        return {}
    if s.startswith("{"):
        try:
            return flatten(json.loads(s))
        except Exception:  # noqa: BLE001
            return {}
    kv = re.findall(r"([A-Za-z_][\w.]*)\s*[=:]\s*(-?\d+(?:\.\d+)?)", s)
    if kv:
        return {k: float(v) for k, v in kv}
    if header:
        out = {}
        for h, cell in zip(header, next(csv.reader([s]))):
            if re.fullmatch(r"\s*-?\d+(?:\.\d+)?\s*", cell):
                out[h] = float(cell)
        if out:
            return out
    nums = re.findall(r"-?\d+(?:\.\d+)?", s)
    return {"value%d" % i if i else "value": float(n) for i, n in enumerate(nums)}


def parse_prometheus(text):
    out = {}
    for line in text.splitlines():
        if line.startswith("#") or not line.strip():
            continue
        m = re.match(r"^([a-zA-Z_:][\w:]*(?:\{[^}]*\})?)\s+(-?[\d.eE+-]+)", line)
        if m:
            try:
                out[m.group(1)] = float(m.group(2))
            except ValueError:
                pass
    return out


class MqttLast:
    """a read-only MQTT 3.1.1 subscriber that keeps the newest payload of one topic (QoS 0)"""

    def __init__(self, host, port, topic, user="", password=""):
        self.host, self.port, self.topic, self.user, self.password = host, int(port), topic, user, password
        self.last, self.error, self.stop = None, None, False
        threading.Thread(target=self.run, daemon=True).start()

    @staticmethod
    def _str(s):
        b = s.encode()
        return struct.pack("!H", len(b)) + b

    @staticmethod
    def _len(n):
        out = b""
        while True:
            d, n = n % 128, n // 128
            out += bytes([d | (0x80 if n else 0)])
            if not n:
                return out

    def _read_len(self, sock):
        mult, val = 1, 0
        while True:
            b = sock.recv(1)
            if not b:
                raise ConnectionError("broker closed the connection")
            val += (b[0] & 127) * mult
            if not b[0] & 128:
                return val
            mult *= 128

    def run(self):
        while not self.stop:
            try:
                s = socket.create_connection((self.host, self.port), timeout=15)
                flags = 0x02 | (0x80 if self.user else 0) | (0x40 if self.password else 0)
                payload = self._str("MQTT") + bytes([4, flags]) + struct.pack("!H", 60) + self._str("oracle7-wb-%d" % os.getpid())
                if self.user:
                    payload += self._str(self.user)
                if self.password:
                    payload += self._str(self.password)
                s.sendall(bytes([0x10]) + self._len(len(payload)) + payload)
                if s.recv(4)[3:4] != b"\x00":
                    raise ConnectionError("broker refused the connection")
                sub = struct.pack("!H", 1) + self._str(self.topic) + b"\x00"
                s.sendall(bytes([0x82]) + self._len(len(sub)) + sub)
                s.settimeout(45)
                last_ping = time.time()
                while not self.stop:
                    if time.time() - last_ping > 40:
                        s.sendall(b"\xc0\x00")
                        last_ping = time.time()
                    try:
                        h = s.recv(1)
                    except socket.timeout:
                        continue
                    if not h:
                        raise ConnectionError("broker closed the connection")
                    n = self._read_len(s)
                    body = b""
                    while len(body) < n:
                        chunk = s.recv(n - len(body))
                        if not chunk:
                            raise ConnectionError("broker closed the connection")
                        body += chunk
                    if h[0] >> 4 == 3:                         # PUBLISH (QoS 0: topic, then payload)
                        tl = struct.unpack("!H", body[:2])[0]
                        self.last = (time.time(), body[2 + tl:].decode("utf-8", "replace"))
                        self.error = None
            except Exception as e:  # noqa: BLE001
                self.error = "%s: %s" % (type(e).__name__, e)
                time.sleep(10)


_MQTT = {}


def read_source(cfg):
    """one set of {field: value} from the sensor's source, with a description of where it was read"""
    kind, addr = cfg["kind"], cfg.get("address", "")
    if kind == "simulated":
        t = time.time()
        day = (t % 86400) / 86400
        return {"air_temp": round(16 + 7 * math.sin(2 * math.pi * (day - 0.3)), 2),
                "humidity": round(62 - 18 * math.sin(2 * math.pi * (day - 0.3)), 1),
                "soil_moisture": round(34 - 6 * ((t / 3600) % 24) / 24, 1)}, "a simulated garden node"
    if kind == "http":
        req = urllib.request.Request(addr, headers={"Accept": "application/json, text/plain"})
        with urllib.request.urlopen(req, timeout=10) as r:
            body = r.read(2_000_000).decode("utf-8", "replace")
            ctype = r.headers.get("Content-Type", "")
        vals = flatten(json.loads(body)) if body.lstrip().startswith(("{", "[")) else parse_prometheus(body)
        return vals, addr
    if kind == "mqtt":
        m = re.match(r"^(?:mqtt://)?([^:/\s]+)(?::(\d+))?/(.+)$", addr)
        if not m:
            raise ValueError("write it as host:port/topic, e.g. 192.168.1.10:1883/garden/node1")
        key = addr
        if key not in _MQTT:
            _MQTT[key] = MqttLast(m.group(1), m.group(2) or 1883, m.group(3), cfg.get("user", ""), cfg.get("password", ""))
        c = _MQTT[key]
        for _ in range(30):
            if c.last:
                break
            time.sleep(0.5)
        if not c.last:
            raise ValueError("no message on %s yet%s" % (m.group(3), (" (" + c.error + ")") if c.error else ""))
        ts, payload = c.last
        return parse_line(payload) or flatten(json.loads(payload)), "mqtt %s (message at %s)" % (addr, time.strftime("%H:%M:%S", time.localtime(ts)))
    if kind == "serial":
        port, _, baud = addr.partition("@")
        baud = int(baud or 9600)
        try:
            import serial  # pyserial
            with serial.Serial(port, baud, timeout=5) as sp:
                sp.readline()                                   # a partial first line is dropped
                for _ in range(5):
                    vals = parse_line(sp.readline().decode("utf-8", "replace"))
                    if vals:
                        return vals, "serial %s at %d baud" % (port, baud)
        except ImportError:
            if sys.platform.startswith("linux") and os.path.exists(port):
                subprocess.run(["stty", "-F", port, str(baud), "raw", "-echo"], check=False)
                with open(port, "rb", buffering=0) as fh:
                    buf, t0 = b"", time.time()
                    while time.time() - t0 < 6:
                        buf += fh.read(256)
                        lines = buf.split(b"\n")
                        for ln in lines[1:-1]:
                            vals = parse_line(ln.decode("utf-8", "replace"))
                            if vals:
                                return vals, "serial %s at %d baud" % (port, baud)
            raise ValueError("reading a serial port here needs pyserial: pip install pyserial")
        raise ValueError("no readable line from %s in 5 tries" % port)
    if kind == "file":
        p = Path(addr).expanduser()
        if not p.is_file():
            raise ValueError("no file at %s" % p)
        with open(p, "rb") as fh:
            head = fh.readline().decode("utf-8", "replace")
            fh.seek(max(0, p.stat().st_size - 8192))
            tail = fh.read().decode("utf-8", "replace").strip().splitlines()
        header = [h.strip() for h in head.split(",")] if "," in head and not re.search(r"\d", head.split(",")[0] if head else "") else None
        for line in reversed(tail):
            vals = parse_line(line, header)
            if vals:
                return vals, "the newest line of %s" % p
        raise ValueError("no readable line in %s" % p)
    raise ValueError("unknown sensor kind %s" % kind)


# ---------------------------------------------------------------- configs, polling, history
def configs():
    out = {}
    for p in DIR.glob("*.json"):
        try:
            c = json.loads(p.read_text(encoding="utf-8"))
            out[c["id"]] = c
        except Exception:  # noqa: BLE001
            pass
    return out


def save_config(c):
    (DIR / ("%s.json" % c["id"])).write_text(json.dumps(c, indent=1), encoding="utf-8")


def check(field_cfg, v):
    q = field_cfg["quantity"]
    if q in QUANTITIES:
        unit, lo, hi, _ = QUANTITIES[q]
        if not lo <= v <= hi:
            return False, "%s %s is outside the physical range of %s (%s to %s %s)" % (v, unit, q, lo, hi, unit)
    return True, ""


def poll_once(c):
    vals, where = read_source(c)
    now = time.time()
    rows = []
    for f in c["fields"]:
        if f["path"] in vals:
            v = vals[f["path"]] * float(f.get("scale", 1))
            ok, why = check(f, v)
            rows.append({"t": now, "q": f["quantity"], "v": round(v, 4), "unit": f.get("unit") or QUANTITIES.get(f["quantity"], ("",))[0],
                         "ok": ok, "why": why, "src": "%s, field %s" % (where, f["path"])})
    hist = DIR / ("%s.jsonl" % c["id"])
    with open(hist, "a", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r) + "\n")
    if hist.stat().st_size > 4_000_000:                       # keep 24 h
        keep = [l for l in hist.read_text(encoding="utf-8").splitlines() if json.loads(l)["t"] > now - KEEP_S]
        hist.write_text("\n".join(keep) + "\n", encoding="utf-8")
    return rows


def history(sid, since=KEEP_S):
    p = DIR / ("%s.jsonl" % sid)
    if not p.exists():
        return []
    cut = time.time() - since
    out = []
    for line in p.read_text(encoding="utf-8").splitlines():
        try:
            r = json.loads(line)
        except Exception:  # noqa: BLE001
            continue
        if r["t"] >= cut:
            out.append(r)
    return out


_POLLERS = {}
STATUS = {}


def start_poller(sid):
    if sid in _POLLERS:
        return

    def loop():
        while True:
            c = configs().get(sid)
            if not c:
                _POLLERS.pop(sid, None)
                return
            try:
                rows = poll_once(c)
                STATUS[sid] = {"ok": True, "at": time.time(), "n": len(rows)}
            except Exception as e:  # noqa: BLE001
                STATUS[sid] = {"ok": False, "at": time.time(), "error": "%s: %s" % (type(e).__name__, e)}
            time.sleep(max(5, int(c.get("interval", 30))))
    _POLLERS[sid] = threading.Thread(target=loop, daemon=True)
    _POLLERS[sid].start()


def start_all():
    for sid in configs():
        start_poller(sid)


# ---------------------------------------------------------------- the sensor reader
def ago(s):
    s = int(s)
    return "%d s" % s if s < 90 else "%d min" % (s // 60) if s < 5400 else "%.1f h" % (s / 3600)


class SensorOrgan:
    """answers about one connected sensor: its newest valid reading of a quantity, with its age and source, and the last 24 h"""

    def __init__(self, sensor="", name="my sensor"):
        self.sid, self.name = sensor, name
        words = re.findall(r"[a-z0-9]+", name.lower())
        self.named = re.compile(r"\b%s\b" % r"\W+".join(map(re.escape, words))) if words else None   # the whole name

    def quantity(self, text):
        c = configs().get(self.sid) or {}
        qs = {f["quantity"] for f in c.get("fields", [])}
        tl = set(re.findall(r"[a-z0-9.]+", text.lower()))
        hits = [q for q in qs if tl & ASKWORDS.get(q, set(q.split()))]
        return hits[0] if len(hits) == 1 else (hits[0] if hits else None), qs

    def takes(self, text):
        t = str(text or "").lower()
        addressed = (self.named and self.named.search(t)) or (re.search(r"\b(my|the|our) sensor\b", t) and len(configs()) == 1)
        q, _ = self.quantity(t)
        return bool(addressed and (q or re.search(r"\b(readings?|status|everything|all)\b", t)))

    def answer(self, text, session):
        if not self.takes(text):
            return None
        c = configs().get(self.sid) or {}
        q, qs = self.quantity(text)
        h = history(self.sid)
        sim = c.get("kind") == "simulated"
        tag = "SIMULATED" if sim else "measured"
        want = [q] if q else sorted(qs)
        parts, srcs, now = [], [], time.time()
        for qq in want:
            rows = [r for r in h if r["q"] == qq]
            good = [r for r in rows if r["ok"]]
            if not rows:
                parts.append("%s: no readings yet" % qq)
                continue
            bad = rows[-1] if not rows[-1]["ok"] else None
            if not good:
                parts.append("%s: no valid reading (%s)" % (qq, bad["why"]))
                continue
            r = good[-1]
            srcs.append(r["src"])
            age = now - r["t"]
            stale = age > 3 * max(5, int(c.get("interval", 30)))
            vs = [x["v"] for x in good]
            s = "%s %s %s (%s %s ago%s)" % (qq, r["v"], r["unit"], tag, ago(age), "; the sensor may be offline" if stale else "")
            if re.search(r"\b(today|24|day|min|max|range|average|mean|trend|rising|falling|going up|going down|lowest|highest)\b", text, re.I) and len(vs) > 1:
                hour = [x for x in good if x["t"] > now - 3600]
                slope = (hour[-1]["v"] - hour[0]["v"]) if len(hour) > 1 else 0
                s += "; last 24 h: min %s, max %s, mean %.2f over %d readings; last hour %s %s" % (
                    min(vs), max(vs), sum(vs) / len(vs), len(vs), "rising" if slope > 0 else "falling" if slope < 0 else "steady", abs(round(slope, 3)) or "")
            if bad:
                s += "; the newest reading was rejected: %s" % bad["why"]
            parts.append(s)
        if len(srcs) == 1:
            src = srcs[0]
        elif srcs:
            src = "%s, fields %s" % (srcs[0].split(", field ")[0], ", ".join(x.split(", field ")[-1] for x in srcs))
        else:
            src = c.get("address", "") or c.get("kind", "")
        return {"kind": "reading", "status": "answered", "subject": self.name,
                "response": "%s: %s. Source: %s." % (self.name[:1].upper() + self.name[1:], "; ".join(parts), src)}
