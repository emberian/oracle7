#!/usr/bin/env python3
"""Oracle7 Workbench - your own Oracle7, on your own machine, with the diagram of everything it is.

  python oracle7.py --workbench [port]        (default 8177; opens on http://127.0.0.1:<port>/)

What it does
  Ask          talk to Oracle7; the diagram lights the path each answer took and shows why a decline happened
  Specialists  the 267 admitted specialists and the five systems built the same way, each with its card
  Build        scaffold a specialist, edit it here, run its dev exam as often as you like, its held-out exam once
  Grow         admitted specialists join your model and appear on the diagram; a changed file sends one back to the exam
  Gaps         (off until you turn it on) your declines, grouped into the specialists your model is missing
  Code         describe a function by examples; the code organ composes it and runs it on your examples
  Film         record any answer's path on the diagram as a video file, made in your browser
  Share        package a specialist (its folder, card, exam verdict and hashes) for the community registry

Privacy: the server listens on 127.0.0.1 only. Nothing is sent anywhere. The gap journal is off by default, lives in
workbench/local/journal.jsonl when on, is never packaged, and the Gaps page deletes it in one click.
Your specialists can only ADD answers: one runs only when the core declined for lack of a reading, never when the core
answered and never when a check (false premise, private question, units...) stopped the answer. Stdlib only."""
from __future__ import annotations

import hashlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import zipfile
from collections import Counter, defaultdict
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

HERE = Path(__file__).resolve().parent
LOCAL = Path(os.environ.get("ORACLE7_WORKBENCH_LOCAL", str(HERE / "local")))
SPECS = LOCAL / "specialists"
OUTBOX = LOCAL / "outbox"
JOURNAL = LOCAL / "journal.jsonl"
CONVS = LOCAL / "conversations"
SETTINGS = LOCAL / "settings.json"
STATIC = HERE / "static"
DATA = HERE / "data"
for d in (SPECS, OUTBOX, CONVS):
    d.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(HERE))
import exam  # noqa: E402
import sources  # noqa: E402
import mcp  # noqa: E402
import verify  # noqa: E402
import sensors  # noqa: E402
import registry  # noqa: E402

ID = re.compile(r"^[a-z][a-z0-9-]{1,40}$")
FNAME = re.compile(r"^[A-Za-z0-9_][A-Za-z0-9_.-]{0,60}\.(py|json|md|txt|csv)$")
READING_DECLINES = ("act:clarify", "unverified:", "corpus_query", "factoid", "deliberation", "capability:", "arb:", "compose",
                    "family_precedence:low_credit", "verified:", "cube:")
CHECK_DECLINES = ("precision_guard", "same_name_guard", "weight:", "chat:unresolved")
TYPES = {".html": "text/html; charset=utf-8", ".js": "text/javascript; charset=utf-8", ".css": "text/css; charset=utf-8",
         ".json": "application/json", ".svg": "image/svg+xml", ".png": "image/png", ".woff2": "font/woff2"}


def settings():
    try:
        s = json.loads(SETTINGS.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        s = {}
    s.setdefault("journal", False)
    s.setdefault("keep_conversations", True)
    return s


# ---------------------------------------------------------------- conversations (kept on this computer; one switch turns it off)
CID = re.compile(r"^[a-z0-9]{6,40}$")


def conv_path(cid):
    if not CID.match(cid or ""):
        raise ValueError("bad conversation id")
    return CONVS / ("%s.json" % cid)


def conv_load(cid):
    p = conv_path(cid)
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {"id": cid, "title": "", "created": int(time.time()), "turns": []}


def conv_add(cid, turn):
    c = conv_load(cid)
    c["turns"].append(turn)
    c["updated"] = int(time.time())
    if not c.get("title"):
        c["title"] = turn["q"][:70]
    conv_path(cid).write_text(json.dumps(c, indent=0), encoding="utf-8")


def conv_list():
    out = []
    for p in CONVS.glob("*.json"):
        try:
            c = json.loads(p.read_text(encoding="utf-8"))
            out.append({"id": c["id"], "title": c.get("title") or "(untitled)", "updated": c.get("updated", c.get("created", 0)),
                        "turns": len(c.get("turns", [])), "answered": sum(1 for t in c.get("turns", []) if t.get("status") == "answered")})
        except Exception:  # noqa: BLE001
            pass
    return sorted(out, key=lambda x: -x["updated"])


def save_settings(s):
    SETTINGS.write_text(json.dumps(s, indent=1), encoding="utf-8")


# ---------------------------------------------------------------- the path an answer took (names from the diagram only)
SPEC_GROUP = {
    "Physical science": "acoustics additive chemistry densities decay electrical electronics energy fluids fuels materials mechanisms optics "
                        "physics springs thermo units carbonmat carboncapture renewables hvac".split(),
    "Earth & life": "agriculture airquality anatomy biology botany climate ecology entomology forestry genetics geology hydrology marinebio "
                    "medicine meteorology microbiology mycelial mycology ocean ornithology seismology soil water wildlife greenhouse geography".split(),
    "Computing": "algorithms cyber dataformats embedded git iot javascript linux networking python sql logic statistics calculus geometry".split(),
    "Space": "astronomy orbits planetary spacecomms spacecraft bodies".split(),
    "Humanities": "architecture arthistory economics government grammar law library linguistics literature music mythology poetry "
                  "psychology sociology ushistory worldhistory".split(),
}


def spec_group(sid):
    if sid.startswith("rel-"):
        return "Relation readers"
    base = re.sub(r"-(v\d+|r\d+)$", "", sid).split("-")[0]
    for g, names in SPEC_GROUP.items():
        if base in names:
            return g
    return "Everyday"


def trace(path, response, status):
    p, resp = str(path or ""), str(response or "")
    s = [["L0", "Front door"], ["L1", None]]
    if "chat:and_parts" in p or "chat:parts" in p:
        s.append(["L3", "Two-part turns"])
    if re.search(r"(^|[>|])chat:(resolved|unresolved)", p):
        s.append(["L3", "Follow-up resolver"])
    if p.startswith("workbench:history"):
        return [["L0", "Front door"], ["L3", "Conversation engine"], ["L3", "Dialogue organ"], ["L4", "Speaker"], ["L0", "Front door"]]
    if p.startswith("workbench:help"):
        return [["L0", "Front door"], ["L5", "Self-explanation"], ["L4", "Speaker"], ["L0", "Front door"]]
    if p.startswith(("act:", "organ:converse")) or "arb:act_" in p:
        s.append(["L3", "Conversation acts"])
    if "family_precedence" in p or "specialist_precedence" in p:
        s.append(["L2", "Family precedence"])
    m = re.search(r"specialist:([a-z0-9-]+)", p)
    mine = re.match(r"yours:([a-z0-9-]+)", p)
    net = re.match(r"network\d*>([a-z0-9 _-]+)", p)
    if mine:
        s += [["L2", "Specialist call"], ["S", "Yours: " + mine.group(1)]]
    elif net and not m:
        s.append(["L2", "Specialist call"])
        for tok in net.group(1).split():
            if tok not in ("core_math", "validity"):
                s.append(["S", spec_group(tok)])
        s.append(["E", "Math organ"])
    elif m:
        g = spec_group(m.group(1))
        s += [["L2", "Specialist call"], ["S", g]]
        if g == "Relation readers":
            s.append(["V", "Relation store"])
    elif "exact_router" in p:
        s += [["L2", "Exact router"], ["V", "Relation store"]]
    elif "general_reader" in p:
        s += [["L2", "General reader"], ["V", "Relation store"]]
    elif "organ:relation" in p:
        s += [["L2", "Organ dispatch"], ["V", "Relation store"]]
    elif re.search(r"organ:code|code_organ|graded_code", p):
        s += [["L2", "Organ dispatch"], ["E", "Code organ"]]
    elif re.search(r"organ:math|network>|core_math|agent:maths|algebra:", p):
        s += [["L2", "Organ dispatch"], ["E", "Math organ"]]
    elif re.search(r"(^|[>|])op:", p):
        s += [["L2", "Organ dispatch"], ["E", "Calculator"]]
    elif "deliberation" in p:
        s += [["L2", "Deliberation"], ["V", "Deep store"]]
    elif "compose" in p:
        s += [["L2", "Compose"], ["V", "Deep store"]]
    elif re.search(r"factoid|cube|corpus_query|verified:", p):
        s += [["L2", "Factoid & reading"], ["V", "Deep store"]]
    elif re.search(r"capability:|arb:", p) and "arb:act_" not in p:
        s += [["L2", "Capability routes"], ["V", "Deep store"]]
    elif status != "answered" and p.startswith("act:clarify"):
        s.append(["L2", "Front parser"])
    if p.startswith("same_name_guard"):
        s += [["L3", "Conversation engine"], ["L4", "Same-name check"], ["V", "Relation store"]]
    if re.match(r"precision_guard:(N1|C1|D1|N2|G3)_", p):
        s.append(["L4", "Answer checks"])
    elif p.startswith("precision_guard:") or "same_name_guard:withheld" in p:
        s.append(["L4", "Final-answer checks" if re.match(r"precision_guard:(G\d|Q\d)", p) else "Precision guard"])
    elif status != "answered" and not p.startswith("act:"):
        s.append(["L4", "Precision guard"])
    if status == "answered":
        if "From the Wikidata relation store" in resp:
            s.append(["L4", "Receipts"])
        s.append(["L4", "Speaker"])
    s.append(["L0", "Front door"])
    out = []
    for x in s:
        if not out or out[-1] != x:
            out.append(x)
    return out


def why_declined(path):
    p = str(path or "")
    if exam.CHECK.search(p):
        return "check", "A check stopped it: the answer would rest on a premise or value it could not verify."
    if "precision_guard:P" in p:
        return "reading", "It found a reply but could not verify it against a record, so it declined rather than guess."
    if p.startswith("act:clarify") or "Front parser" in p:
        return "parse", "It did not read the question's shape. Rephrasing as a direct question often works."
    if any(k in p for k in READING_DECLINES):
        return "reading", "Nothing it holds could verify an answer, so it declined rather than guess."
    return "other", "It declined rather than guess."



# ---------------------------------------------------------------- what it can do (answered by the Workbench itself)
HELP_TOPICS = [
    ("ask", r"\b(ask|question|answer|decline|why did it|path)\b",
     "Ask anything in the box at the bottom left. Each answer lights the path it took on the diagram and shows its route. "
     "When Oracle7 cannot verify an answer it declines and says why (a check stopped it, it did not parse the question, or "
     "nothing it holds could verify it). 'show path' replays a path; 'route' writes the raw route to the log."),
    ("scan", r"\b(scan|my (?:pc|computer|laptop|machine))\b",
     "Start > Scan this computer (or type /scan). It reads this machine's system, CPU, memory, disks, uptime and the processes "
     "using the most memory - figures and process names only, never your files - and shows them. 'Make it a specialist' adds a "
     "reader, so 'how much disk space is free on my computer?' gets the value and the call it was read from."),
    ("connect", r"\b(connect|server|ssh|remote)\b",
     "Start > Connect a server (or /connect user@host). It uses your own SSH key and runs a fixed list of read-only commands "
     "(hostname, uptime, load, memory, disks, top processes, failed services). Name the server, then ask 'how much memory is "
     "<name> using?'. A password is never asked for or stored."),
    ("files", r"\b(files?|upload|documents?|csv|spreadsheet|notes|tables?)\b",
     "Start > Add files (or /files): drop .csv, .tsv, .txt or .md files. Tables answer 'what is the <column> of <row>?' with "
     "the file, row and column; text answers 'what do my notes say about ...?' by quoting the sentence with its file and line. "
     "The files are copied into the reader's own folder on this machine."),
    ("build", r"\b(build|make|create|write|new)\b.*\bspecialists?\b|\bspecialist\b|\bexams?\b",
     "Build: 'New specialist' scaffolds a folder (manifest, organ, panel of test items, scorer) that you edit here, or 'Add the "
     "worked example'. Run the dev exam as often as you like and the held-out exam once. It joins your model only if it gets "
     "more right than the core alone, adds no false yes, has few wrong answers, stays in its lane on 924 general questions, "
     "leaves identity questions alone and is fast. Commands: /new <id> [words], /exam <id> dev, /exam <id> heldout."),
    ("grow", r"\b(grow|improve|self.improv|learn|diagram)\b",
     "Your model grows only through exams: an admitted specialist appears on the diagram's Specialists ring and answers where "
     "the core declined. Change one of its files and it leaves your model until it passes a new held-out set. With the gap "
     "journal on (Gaps, or /gaps on) your declines are grouped into the specialists you are missing, and 'Start a specialist' "
     "turns a group into a new specialist with your questions as its first dev items."),
    ("code", r"\b(code|coding|program|function|python|script|tests?)\b",
     "Code (or /code <what it should do>): ask for a function, e.g. 'check whether a string is a palindrome'. The code organ "
     "hands over only programs it has run: a small website, palindromes, factorials, vowel and word counts, word frequencies, "
     "HTTP routes, regex extraction, memoisation, a bank-account class, matrix multiply, fizzbuzz, fibonacci, string reversal, "
     "JSON round-trips, concurrent work, binary search, tower of hanoi, quicksort, list sums, prime tests and two small games. "
     "Check what it hands over with tests of your own: Run tests runs them in a separate Python process with a 10 second limit."),
    ("film", r"\b(film|video|record|movie|clip)\b",
     "Film (or /film): record answers as a video of the diagram tracing each path beside the question, answer and path. It is "
     "made in your browser as a .webm file; 'film this' under any answer records just that one."),
    ("voice", r"\b(eleven ?labs|narrat\w*|voice|voiceover|music|sound|audio|image|images|picture|illustrat\w*)\b",
     "Film > Narration, sound and images (optional): connect your own ElevenLabs account with its API key to narrate each filmed "
     "answer in a voice you choose, lay an ambient sound you describe under it, and open each answer with an illustration "
     "(Gemini 2.5 Flash Image or GPT Image, through ElevenLabs; image generation needs their Pro plan). Generated images are "
     "labelled as generated in the film and saved in workbench/local/assets. This is the only feature that sends anything off "
     "your computer: the narration text, the sound description and the image prompts go to ElevenLabs. The key stays in the page "
     "unless you tick 'remember on this computer'."),
    ("share", r"\b(share|registry|import|package|hugging ?face)\b",
     "Share (or /share <id>): packages a specialist you built - its folder, exam verdict and the SHA-256 of every file - and shows "
     "the command to upload it to the community registry with your own Hugging Face account. Import takes a shared .zip, which "
     "must pass its held-out exam on your machine before it joins. Readers of your computer, servers and files are never packaged."),
    ("specialists", r"\b(specialists?|systems?|deepspace|trafficcop|chameleon|vision|artist)\b",
     "Specialists lists the 267 admitted specialists (106 by field plus 161 relation readers), each with its held-out score and "
     "card; search it or type /specialists <word>. Systems describes the five systems built the same way: DeepSpace, Trafficcop, "
     "Chameleon (builds websites), Vision (sees and reads) and Artist (makes images by citation)."),
    ("mcp", r"\b(mcp|tools?|model context protocol|plug ?in|integrat\w*)\b",
     "Start > Connect an MCP server: give the command that starts it (for example npx -y @modelcontextprotocol/server-filesystem "
     "with a folder) or its URL. The Workbench lists its tools; tick the ones to use, add a few example questions if you like, and "
     "it builds an adaptive specialist. It routes each question to the tool it fits, fills the arguments from the question (or "
     "says which one is missing), answers with the tool's result and the exact call it made, and learns from your right/wrong "
     "marks under each answer. Questions routed to a server are sent to it, so connect servers you trust."),
    ("history", r"\b(history|previous|past|earlier|old|saved) (?:conversations?|chats?)\b|\bconversations?\b|\bremember\w*\b|\bmemory of\b",
     "Conversations (the panel on the left; the button at the top opens and collapses it): every conversation is kept on this "
     "computer. Open one and carry on - the core picks up its context, so follow-ups still work. Rename, search or delete them, "
     "or switch keeping off. 'Make specialist' turns a conversation into a temporary specialist (7 days unless you choose) that "
     "answers 'what did we say earlier about...?' and repeated questions by quoting the earlier answer with its date and route. "
     "It is checked like any reader before it joins, and leaves your model when it expires."),
    ("verify", r"\b(verify|verified|hash\w*|blockchain|chain|solana|on.chain|tamper\w*|authentic\w*|merkle)\b",
     "Specialists > Verify this install (or /verify): recomputes the SHA-256 of every shipped part - all 307 specialist folders, "
     "the admitted fold chain, this workbench, the launcher and the store manifest - and rebuilds the Merkle root published in "
     "RELEASE_HASHES.json. A changed or missing specialist shows by name. 'Check the anchor on Solana' then asks a public Solana "
     "RPC (read-only; the only network call) for the release's anchor transaction and confirms its memo carries the same root, "
     "so your copy is provably the one released. Stores are checked against PACK_MANIFEST.json by oracle7.py --setup."),
    ("sensors", r"\b(sensors?|iot|esp32|arduino|mqtt|serial|usb|thermometer|probe|telemetry|readings?|home assistant|shelly)\b",
     "Start > Connect a sensor, or the Sensors tab (or /sensors): an HTTP device or hub that serves JSON or Prometheus metrics "
     "(ESP32, Shelly, Tasmota, Home Assistant, weather stations), an MQTT topic, a USB/serial device that prints readings, a log "
     "file a logger appends to, or a simulated garden node to try it without hardware. Test shows the numbers it found and what "
     "each one measures; Add starts polling it (every 30 s by default, 24 h kept on this computer) and makes a reader you can ask: "
     "'what is the soil moisture on garden node?', 'temperature on my sensor today?'. Every answer gives the value, its age, its "
     "source and whether it was measured or simulated; a value outside its physical range is rejected and said so."),
    ("terminal", r"\b(cli|terminal|command line|shell|script|json output)\b",
     "Everything that makes sense in a terminal works there too, with the same code: python oracle7.py help lists it. "
     "ask \"question\" (answer, status and path), chat, specialists [word], card <id>, systems, verify [--chain], mine, new <id>, "
     "example, exam <id> dev|heldout, scan, sensors, sensor-test <kind> <address>, history. Add --json for machine-readable output."),
    ("registry", r"\b(oracle7 token|\$?oracle7 registry|registry|register|attest\w*|vouch\w*|on.chain|token|holders?)\b",
     "Share > Register on Solana: one specialist, one $ORACLE7. The creator of an admitted specialist signs, in their own wallet (Phantom), one Solana transaction that burns exactly 1 $ORACLE7 and carries, in a memo, the "
     "specialist's fingerprint - the SHA-256 of its files, its held-out verdict and its held-out set, and the release it was examined "
     "on. Anyone who imports it and sees it pass its held-out exam on their machine can Attest the same way. Check reads every "
     "registration and attestation back from the chain, confirms it matches the specialist's files now, and shows each signer's "
     "wallet and how much $ORACLE7 it holds. The records travel with the specialist when it is shared. No key is ever seen or "
     "stored here; the burn is the only token movement, approved in the creator's wallet. Attesting is free."),
    ("privacy", r"\b(privacy|private|data|sent|stored|safe)\b",
     "The Workbench answers on 127.0.0.1 only and sends nothing anywhere. The gap journal is off until you turn it on, stays in "
     "workbench/local/journal.jsonl, and one click deletes it. Conversations are kept in workbench/local/conversations so you can "
     "go back to them; switch that off or delete them in the Conversations panel."),
]
COMMANDS = ["/help - this guide", "/scan - read this computer", "/connect user@host [port] [key] - read a server",
            "/files - add files", "/mcp - connect an MCP server", "/sensors - connect and watch sensors", "/new <id> [words] - a new specialist", "/exam <id> dev|heldout - run an exam",
            "/specialists <word> - find one", "/systems - the five systems", "/gaps on|off - the gap journal",
            "/code <what it does> - compose a function", "/film - film the answers", "/share <id> - package one",
            "/verify - check this install against the published hashes", "/registry <id> - its on-chain registrations and attestations", "/history - open the conversations panel", "/new-chat - start a new conversation",
            "/remember [days] - make this conversation a temporary specialist", "/clear - clear the conversation"]
HELP_Q = re.compile(r"^\s*(?:/help\b|help\b|what (?:can|do) (?:you|it|the workbench|oracle7) do|what (?:are|is) (?:your|the|its) "
                    r"(?:features|commands|abilities)|(?:list|show) (?:me )?(?:the |your |all )?(?:features|commands)|what commands|"
                    r"how do i (?:use|start)\b|how does (?:this|the workbench) work)", re.I)
HOWTO_Q = re.compile(r"^\s*(?:how (?:do|can|would) i|how to|can i|can you|is it possible to)\b", re.I)


SENSORS_ALL = re.compile(r"\b(?:my|our|the|all(?: the| my)?) sensors\b|\bsensor readings\b|\ball (?:my )?readings\b", re.I)
PRONOUN = re.compile(r"\b(it|its|that one|this one|them|they)\b", re.I)
HISTORY_Q = re.compile(r"^\s*(?:what|which) (?:did|was|were) (?:i|my) (?:just |first |last |previous |earlier )?(?:ask|asked|question|questions)\b|"
                       r"^\s*what (?:was|were) my (first|last|previous|earlier|latest) questions?\b|"
                       r"^\s*what did you (?:just )?(?:say|answer|tell me)\b|^\s*what (?:have|did) (?:i|we) (?:asked|ask|talk(?:ed)? about|discuss(?:ed)?)\b", re.I)


def history_reply(text, sid):
    """the conversation itself is kept by the Workbench, so it answers questions about it: what was asked first or last,
    what it just said, what we have covered"""
    t = str(text or "")
    if not HISTORY_Q.search(t):
        return None
    try:
        c = conv_load(sid)
    except ValueError:
        return None
    asked = [x for x in c.get("turns", []) if not str(x.get("path", "")).startswith("workbench:")]
    topic = re.search(r"\babout (.+?)[?.!]*$", t, re.I)
    if topic:
        want = set(sources._words(topic.group(1))) - sources.RECALL_FILLER
        hits = [x for x in asked if want & set(sources._words(x["q"] + " " + str(x.get("response", ""))))]
        if not hits:
            return None                                    # not in this conversation: a saved conversation may recall it
        return "\n\n".join("At %s you asked \"%s\". I %s: %s" % (time.strftime("%H:%M", time.localtime(x.get("t", 0))), x["q"],
                             "answered" if x.get("status") == "answered" else "declined", str(x.get("response", ""))[:400]) for x in hits[-3:])
    if not asked:
        return "Nothing has been asked in this conversation yet."
    when = lambda x: time.strftime("%H:%M", time.localtime(x.get("t", 0)))
    if re.search(r"\bfirst\b", t, re.I):
        x = asked[0]
        return "Your first question in this conversation (%s) was: \"%s\"" % (when(x), x["q"])
    if re.search(r"\bwhat did you (?:just )?(?:say|answer|tell me)\b", t, re.I):
        x = asked[-1]
        return "I said (%s), to \"%s\": %s" % (when(x), x["q"], str(x.get("response", ""))[:600])
    if re.search(r"\b(just|last|previous|latest)\b", t, re.I):
        x = asked[-1]
        return "Your last question (%s) was: \"%s\"" % (when(x), x["q"])
    lines = ["%d. %s - %s" % (i, x["q"], "answered" if x.get("status") == "answered" else "declined") for i, x in enumerate(asked[-12:], max(1, len(asked) - 11))]
    return "In this conversation you have asked %d question%s:\n%s" % (len(asked), "" if len(asked) == 1 else "s", "\n".join(lines))


def help_reply(text):
    t = str(text or "")
    if HELP_Q.search(t):
        body = "\n\n".join("%s. %s" % (k.capitalize(), v) for k, _, v in HELP_TOPICS)
        return ("Here is everything the Workbench does. The core model answers questions from sourced records and declines what "
                "it cannot verify. Around it you can read your computer, servers and files, build and examine specialists, find "
                "your gaps, compose code, film answers and share what you build.\n\n" + body + "\n\nCommands:\n" + "\n".join(COMMANDS))
    if HOWTO_Q.search(t):
        first = ("registry", "terminal", "sensors", "mcp", "voice", "film", "verify", "history", "files", "scan", "code", "share", "grow", "build", "connect", "specialists", "privacy", "ask")
        topics = sorted(HELP_TOPICS, key=lambda x: first.index(x[0]) if x[0] in first else 99)
        hits = [v for k, pat, v in topics if re.search(pat, t, re.I)]
        if hits:
            return "\n\n".join(hits[:2])
    return None

# ---------------------------------------------------------------- the engine + your specialists (fill declines only)
class Workbench:
    def __init__(self, engine):
        self.eng = engine
        self.lock = threading.Lock()
        self.mine = {}            # id -> exam.Loaded (admitted and unchanged since its exam)
        self.last = {}            # session -> (your specialist id, subject) of its last answer, for follow-ups
        self.warm = set()         # sessions whose context the core holds in this run
        self.reload()

    def reload(self):
        mine = {}
        for d in sorted(SPECS.iterdir()) if SPECS.exists() else []:
            st = exam.status(d)
            if st["state"] == "admitted":
                try:
                    mine[d.name] = exam.load_specialist(d)
                except Exception as e:  # noqa: BLE001
                    print("workbench: %s did not load: %s" % (d.name, e), file=sys.stderr)
        self.mine = mine

    def chat(self, text, sid):
        h = help_reply(text)
        if h:
            return {"status": "answered", "response": h, "path": "workbench:help"}
        h = history_reply(text, sid)
        if h:
            return {"status": "answered", "response": h, "path": "workbench:history"}
        # a follow-up to an answer from one of your readers ("what shelf is it on?") is read against that answer's subject
        prev = self.last.get(sid)
        if prev and PRONOUN.search(text):
            sp = self.mine.get(prev[0])
            if sp is not None:
                a = sp.reply(PRONOUN.sub(prev[1], text, count=1), sid)
                if a and a.get("status") == "answered":
                    a = dict(a)
                    a["path"] = "yours:%s>followup>%s" % (prev[0], a.get("path", ""))
                    return self.remember(text, sid, a)
        # questions ADDRESSED to your own things (my computer, my notes, a named server, your table's rows) go to their
        # readers first: the core cannot know them, and its general answer would not be about them. The readers' lane
        # check bounds how often that can happen on general questions.
        now = time.time()
        live = {i: sp for i, sp in self.mine.items() if not sp.m.get("expires") or float(sp.m["expires"]) > now}
        if SENSORS_ALL.search(text):                       # "my sensors": every connected sensor answers, one line each
            lines = []
            for i, sp in live.items():
                if sp.m.get("organ", {}).get("module", "").startswith("organ_sensor"):
                    a = sp.organ.answer("%s readings %s" % (sp.organ.name, text), sid)
                    if a and a.get("status") == "answered":
                        lines.append(a["response"])
            if lines:
                return self.remember(text, sid, {"status": "answered", "response": "\n".join(lines), "path": "yours:sensors>all"})
        for i, sp in live.items():
            if sp.m.get("source"):
                a = sp.reply(text, sid)
                if a and a.get("status") == "answered":
                    a = dict(a)
                    a["path"] = "yours:%s>%s" % (i, a.get("path", ""))
                    return self.remember(text, sid, a)
        if sid not in self.warm:
            self.warm.add(sid)
            try:
                prior = [x for x in conv_load(sid).get("turns", []) if x.get("status") == "answered"
                         and not str(x.get("path", "")).startswith(("workbench:", "yours:"))][-2:]
            except ValueError:
                prior = []
            for x in prior:                               # replies discarded: this only restores what the core remembers
                try:
                    self.eng.chat(x["q"], session_id="wb-" + sid)
                except Exception:  # noqa: BLE001
                    pass
        r = self.eng.chat(text, session_id="wb-" + sid)
        self.last.pop(sid, None)                          # the core answered (or declined): follow-ups are its own
        path = str(r.get("path", ""))
        if r.get("status") != "answered" and live and exam.fillable(path):
            for i, sp in live.items():
                a = sp.reply(text, sid)
                if a and a.get("status") == "answered":
                    a = dict(a)
                    a["path"] = "yours:%s>%s" % (i, a.get("path", ""))
                    a["declined_by"] = path
                    return self.remember(text, sid, a)
        return r

    def remember(self, text, sid, a):
        """hand an answer from your specialist back to the core's conversation memory, so a follow-up ("and in winter?",
        "what did I just ask?") reads against it like any answer the core gave"""
        m = re.match(r"^yours:([a-z0-9-]+)>", str(a.get("path", "")))
        if m and a.get("subject"):
            self.last[sid] = (m.group(1), str(a["subject"]))

        def upd():
            try:
                import chat_context_v2 as cc
                cc.update("wb-" + sid, text, a)
            except Exception:  # noqa: BLE001
                pass
        try:
            self.eng._ex.submit(upd).result(timeout=5)
        except Exception:  # noqa: BLE001
            pass
        return a


WB = None


def specialists_payload():
    base = json.loads((DATA / "specialists.json").read_text(encoding="utf-8")) if (DATA / "specialists.json").exists() else {"items": []}
    yours = []
    for d in sorted(SPECS.iterdir()):
        if d.is_dir():
            st = exam.status(d)
            m = exam.read_manifest(d) or {}
            yours.append({"id": d.name, "name": m.get("name", d.name), "state": st["state"], "note": st.get("note", ""),
                          "verdict": st.get("verdict")})
    base["yours"] = yours
    return base


def gaps():
    """declines from the journal, grouped by what is missing: the decline kind, then the domain words the questions share"""
    rows = []
    if JOURNAL.exists():
        for line in JOURNAL.read_text(encoding="utf-8").splitlines():
            try:
                rows.append(json.loads(line))
            except Exception:  # noqa: BLE001
                pass
    dec = [r for r in rows if r.get("status") != "answered"]
    stop = set("the a an of in on at to is was were are be by for with from and or what which who whom whose where when why how "
               "did does do it its this that these those i you he she they we my your his her their our me him them as than then "
               "there here can could would should will shall may might must much many most more about into over after before "
               "name tell give find please".split())
    groups = defaultdict(list)
    for r in dec:
        words = [w for w in re.findall(r"[a-z][a-z-]{2,}", r["q"].lower()) if w not in stop]
        groups[r.get("why", "other")].append((r["q"], words))
    out = []
    for kind, items in groups.items():
        c = Counter(w for _, ws in items for w in set(ws))
        themes = []
        for w, n in c.most_common(8):
            if n < 2:
                break
            ex = [q for q, ws in items if w in ws][:4]
            themes.append({"word": w, "count": n, "examples": ex})
        out.append({"kind": kind, "count": len(items), "themes": themes, "examples": [q for q, _ in items[:5]]})
    out.sort(key=lambda g: -g["count"])
    return {"on": settings().get("journal", False), "turns": len(rows), "declined": len(dec), "groups": out}


def scaffold(sid, name, words, examples=()):
    d = SPECS / sid
    if d.exists():
        raise ValueError("a specialist named %s already exists" % sid)
    shutil.copytree(HERE / "template", d)
    for f in d.iterdir():
        if f.is_file():
            cue = "|".join(w.replace("-", "[- ]") for w in words) or "(?!x)x"      # words are [a-z0-9-] only: safe in JSON and regex
            t = f.read_text(encoding="utf-8").replace("__ID__", sid).replace("__NAME__", name.replace('"', "'")).replace(
                "__CUE__", cue).replace("__MODULE__", "organ_" + sid.replace("-", "_"))
            f.write_text(t, encoding="utf-8")
    (d / "organ.py").rename(d / ("organ_%s.py" % sid.replace("-", "_")))
    if examples:                                            # questions from your Gaps page become dev items to answer
        pf = d / "panel.json"
        panel = json.loads(pf.read_text(encoding="utf-8"))
        panel["dev"] = [{"q": q, "a": "", "valid": True, "kind": "fact"} for q in examples] + panel["dev"]
        pf.write_text(json.dumps(panel, indent=1), encoding="utf-8")
    return d


def package(sid):
    d = SPECS / sid
    st = exam.status(d)
    if (exam.read_manifest(d) or {}).get("source"):
        raise ValueError("source readers read your own computer, servers or files, so they are not packaged for sharing")
    if st["state"] != "admitted":
        raise ValueError("only an admitted specialist is packaged (this one is %s); pass its held-out exam first" % st["state"])
    files = sorted(p for p in d.rglob("*") if p.is_file() and "__pycache__" not in p.parts)
    sums = {str(p.relative_to(d)).replace("\\", "/"): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    man = {"id": sid, "state": st["state"], "verdict": st.get("verdict"), "files": sums,
           "packaged": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "format": "oracle7-specialist/1"}
    h = hashlib.sha256(json.dumps(sums, sort_keys=True).encode()).hexdigest()[:12]
    out = OUTBOX / ("%s-%s.zip" % (sid, h))
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for p in files:
            z.write(p, "%s/%s" % (sid, p.relative_to(d).as_posix()))
        z.writestr("%s/SHARE_MANIFEST.json" % sid, json.dumps(man, indent=1))
    return {"zip": str(out), "sha12": h, "state": st["state"],
            "command": "huggingface-cli upload Prometheus7/oracle7-specialists \"%s\" specialists/%s --repo-type dataset" % (out, out.name)}


def import_zip(path):
    p = Path(path).expanduser()
    if not p.is_file() or p.suffix != ".zip":
        raise ValueError("give the path of a .zip made by Share")
    with zipfile.ZipFile(p) as z:
        names = z.namelist()
        top = {n.split("/")[0] for n in names}
        if len(top) != 1:
            raise ValueError("a shared specialist is one folder")
        sid = top.pop()
        if not ID.match(sid) or (SPECS / sid).exists():
            raise ValueError("bad or existing specialist id: %s" % sid)
        for n in names:
            parts = n.split("/")
            if ".." in parts or n.startswith("/") or (len(parts) > 1 and parts[-1] and not FNAME.match(parts[-1])):
                raise ValueError("refused file in package: %s" % n)
        man = json.loads(z.read("%s/SHARE_MANIFEST.json" % sid))
        tmp = Path(tempfile.mkdtemp(prefix="o7import-"))
        z.extractall(tmp)
    src = tmp / sid
    for rel, h in man["files"].items():
        if hashlib.sha256((src / rel).read_bytes()).hexdigest() != h:
            shutil.rmtree(tmp)
            raise ValueError("%s does not match its published hash" % rel)
    (src / "SHARE_MANIFEST.json").unlink()
    for v in src.glob("verdict_*.json"):          # their verdict is theirs: it takes the exam again here
        v.rename(v.with_name("shared_" + v.name))
    shutil.move(str(src), str(SPECS / sid))
    shutil.rmtree(tmp, ignore_errors=True)
    return {"id": sid, "note": "imported; it joins your model only after it passes its held-out exam on this machine"}


def slug(s):
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", str(s).lower())).strip("-")[:30] or "x"


def machine_probes(rd, on):
    """questions whose answers the readings already hold, in parts that do not change between two reads"""
    by = {(r["entity"].split()[0], r["signal"]): r for r in rd}
    P = []
    if ("cpu", "cores") in by:
        P.append(("How many cores does %s have?" % on, str(by[("cpu", "cores")]["value"])))
    if ("system", "hostname") in by:
        P.append(("What is the hostname of %s?" % on, str(by[("system", "hostname")]["value"])))
    if ("memory", "used") in by:
        P.append(("How much memory is %s using?" % on, by[("memory", "used")]["text"].split(" used of ")[1].split(" (")[0]))
    if ("disk", "free") in by:
        P.append(("How much disk space is free on %s?" % on, " free of "))
    if ("system", "uptime") in by:
        P.append(("How long has %s been up?" % on, "up "))
    if ("processes", "top_memory") in by:
        P.append(("What is using the most memory on %s?" % on, "using the most memory"))
    P += [("How much memory does a computer need?", None), ("What is the capital of France?", None), ("Who wrote Hamlet?", None)]
    return P


def file_probes(d):
    org = sources.FilesOrgan(folder=d.name + "/files")
    org.load()
    P = []
    for fname, hdr, rows in org.tables:
        keys = [r[0].strip() for r in rows if r and r[0].strip()]
        for r in rows[:: max(1, len(rows) // 6)][:6]:
            if r and r[0].strip() and keys.count(r[0].strip()) == 1:
                for j in range(1, min(len(hdr), len(r))):
                    if hdr[j].strip() and r[j].strip():
                        P.append(("What is the %s of %s?" % (hdr[j].strip(), r[0].strip()), r[j].strip()))
                        break
    for fname, i, sent in org.lines[:: max(1, len(org.lines) // 5)][:5]:
        ws = [w for w in sources._words(sent) if len(w) > 4][:3]
        if len(ws) >= 2:
            P.append(("What do my notes say about %s?" % " ".join(ws), sent[:30]))
    P += [("What is the capital of France?", None), ("Who wrote Hamlet?", None)]
    return P


def run_code(code, tests, timeout=10):
    """your function + your tests, in a separate Python process (isolated mode, a temp dir, a time limit)"""
    with tempfile.TemporaryDirectory(prefix="o7code-") as t:
        f = Path(t) / "run.py"
        f.write_text(code + "\n\n" + tests + "\nprint('ALL TESTS PASSED')\n", encoding="utf-8")
        try:
            r = subprocess.run([sys.executable, "-I", str(f)], cwd=t, capture_output=True, text=True, timeout=timeout)
            out = (r.stdout + r.stderr)[-4000:]
            return {"ok": r.returncode == 0 and "ALL TESTS PASSED" in r.stdout, "output": out}
        except subprocess.TimeoutExpired:
            return {"ok": False, "output": "stopped after %d s" % timeout}



# ---------------------------------------------------------------- optional: ElevenLabs for film narration and sound (your key)
# The ONLY feature that sends anything off this machine, and only when you connect it: the text of the narration (or the
# sound description) goes to api.elevenlabs.io with your key; the audio comes back into your film. The key is kept in this
# page's memory, or in workbench/local/settings.json if you tick "remember on this computer". Off by default.
EL_API = "https://api.elevenlabs.io/v1"


def el_key(b):
    k = str(b.get("key") or settings().get("elevenlabs_key") or "").strip()
    if not k:
        raise ValueError("connect ElevenLabs first (Film tab): paste your API key")
    if not re.match(r"^[A-Za-z0-9_\-]{20,128}$", k):
        raise ValueError("that does not look like an ElevenLabs API key")
    return k


def el_call(path, key, body=None, accept="application/json", timeout=90):
    import urllib.error
    import urllib.request
    req = urllib.request.Request(EL_API + path, data=None if body is None else json.dumps(body).encode(),
                                 headers={"xi-api-key": key, "Content-Type": "application/json", "Accept": accept},
                                 method="GET" if body is None else "POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read()
    except urllib.error.HTTPError as e:
        raw = e.read()[:2000].decode("utf-8", "replace")
        try:
            d = json.loads(raw).get("detail")
            msg = d.get("message") if isinstance(d, dict) else str(d)
        except Exception:  # noqa: BLE001
            msg = raw[:200]
        raise ValueError("ElevenLabs refused it (%d): %s" % (e.code, msg))
    except urllib.error.URLError as e:
        raise ValueError("could not reach ElevenLabs: %s" % e.reason)

# ---------------------------------------------------------------- http
class H(BaseHTTPRequestHandler):
    server_version = "oracle7-workbench"

    def log_message(self, *a):
        pass

    def _send(self, code, obj, ctype="application/json", raw=None):
        b = raw if raw is not None else json.dumps(obj, default=str).encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(b)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(b)

    def _body(self):
        n = int(self.headers.get("Content-Length") or 0)
        return json.loads(self.rfile.read(min(n, 2_000_000)) or b"{}")

    def _local_only(self):
        host = (self.headers.get("Host") or "").split(":")[0]
        return host in ("127.0.0.1", "localhost", "[::1]")

    def do_GET(self):  # noqa: N802
        if not self._local_only():
            return self._send(403, {"error": "the workbench answers on 127.0.0.1 only"})
        u = urlparse(self.path)
        q = {k: v[0] for k, v in parse_qs(u.query).items()}
        if u.path in ("/", "/index.html"):
            return self._send(200, None, TYPES[".html"], (STATIC / "index.html").read_bytes())
        if u.path.startswith("/static/"):
            f = (STATIC / u.path[len("/static/"):]).resolve()
            if STATIC.resolve() in f.parents and f.is_file():
                return self._send(200, None, TYPES.get(f.suffix, "application/octet-stream"), f.read_bytes())
            return self._send(404, {"error": "not found"})
        if u.path == "/api/state":
            return self._send(200, {"head": WB.eng.tip, "journal": settings().get("journal", False), "yours": sorted(WB.mine),
                                    "elevenlabs_remembered": bool(settings().get("elevenlabs_key"))})
        if u.path == "/api/sensors":
            out = []
            for sid, c in sorted(sensors.configs().items()):
                h = sensors.history(sid)
                latest = {}
                for r in h:
                    if r["ok"]:
                        latest[r["q"]] = {"v": r["v"], "unit": r["unit"], "t": r["t"]}
                out.append({"id": sid, "name": c["name"], "kind": c["kind"], "address": c.get("address", ""), "interval": c.get("interval", 30),
                            "status": sensors.STATUS.get(sid), "latest": latest, "rejected": sum(1 for r in h if not r["ok"]),
                            "state": exam.status(SPECS / sid)["state"] if (SPECS / sid).exists() else "none"})
            return self._send(200, {"items": out, "quantities": {k: v[0] for k, v in sensors.QUANTITIES.items()}})
        if u.path == "/api/sensor/series":
            rows = [r for r in sensors.history(q.get("id", "")) if r["q"] == q.get("q") and r["ok"]]
            step = max(1, len(rows) // 300)
            return self._send(200, {"points": [[int(r["t"]), r["v"]] for r in rows[::step]]})
        if u.path == "/api/registry/memo":
            sid, kind = q.get("id", ""), q.get("kind", "register")
            if not ID.match(sid) or not (SPECS / sid).is_dir():
                return self._send(404, {"error": "no such specialist"})
            try:
                return self._send(200, {"memo": registry.memo_for(SPECS / sid, kind), "mint": registry.ORACLE7_MINT, "rpc": registry.RPC,
                                        "burn_raw": registry.BURN_RAW, "decimals": registry.DECIMALS})
            except ValueError as e:
                return self._send(400, {"error": str(e)})
        if u.path == "/api/convs":
            return self._send(200, {"keep": settings().get("keep_conversations"), "items": conv_list()})
        if u.path == "/api/conv":
            return self._send(200, conv_load(q.get("id", "")))
        if u.path == "/api/help":
            return self._send(200, {"topics": [{"topic": k, "text": v} for k, _, v in HELP_TOPICS], "commands": COMMANDS})
        if u.path == "/api/specialists":
            return self._send(200, specialists_payload())
        if u.path == "/api/systems":
            return self._send(200, json.loads((DATA / "systems.json").read_text(encoding="utf-8")))
        if u.path == "/api/gaps":
            return self._send(200, gaps())
        if u.path == "/api/card":
            sid = q.get("id", "")
            f = DATA / "cards" / (sid + ".md")
            if re.match(r"^[a-z0-9-]+$", sid) and f.exists():
                return self._send(200, {"id": sid, "md": f.read_text(encoding="utf-8")})
            return self._send(404, {"error": "no card"})
        if u.path == "/api/files":
            d = SPECS / q.get("id", "")
            if not ID.match(q.get("id", "")) or not d.is_dir():
                return self._send(404, {"error": "no such specialist"})
            return self._send(200, {"files": sorted(p.name for p in d.iterdir() if p.is_file()), "status": exam.status(d)})
        if u.path == "/api/file":
            d, name = SPECS / q.get("id", ""), q.get("name", "")
            if not ID.match(q.get("id", "")) or not FNAME.match(name) or not (d / name).is_file():
                return self._send(404, {"error": "no such file"})
            return self._send(200, {"name": name, "text": (d / name).read_text(encoding="utf-8")})
        if u.path == "/api/exam":
            return self._send(200, exam.progress(q.get("id", "")))
        return self._send(404, {"error": "not found"})

    def do_POST(self):  # noqa: N802
        if not self._local_only() or (self.headers.get("Origin") and not re.match(r"^https?://(127\.0\.0\.1|localhost)(:\d+)?$",
                                                                                    self.headers.get("Origin", ""))):
            return self._send(403, {"error": "the workbench answers its own page on 127.0.0.1 only"})
        u = urlparse(self.path)
        try:
            b = self._body()
        except Exception:  # noqa: BLE001
            return self._send(400, {"error": "bad request"})
        try:
            if u.path == "/api/chat":
                text, sid = str(b.get("text", "")).strip()[:4000], re.sub(r"[^a-z0-9]", "", str(b.get("sid", "x")))[:40] or "x"
                if not text:
                    return self._send(400, {"error": "ask something"})
                t = time.time()
                r = WB.chat(text, sid)
                status = r.get("status")
                kind, why = (None, None) if status == "answered" else why_declined(r.get("path"))
                if settings().get("keep_conversations") and not b.get("nokeep") and CID.match(sid):
                    conv_add(sid, {"t": int(time.time()), "q": text, "status": status, "response": str(r.get("response", "")),
                                   "path": str(r.get("path", "")), "trace": trace(r.get("path"), r.get("response"), status),
                                   "why": why, "ms": int((time.time() - t) * 1000)})
                if settings().get("journal"):
                    with open(JOURNAL, "a", encoding="utf-8") as fh:
                        fh.write(json.dumps({"t": int(time.time()), "q": text, "status": status, "why": kind,
                                             "path": str(r.get("path"))[:120]}) + "\n")
                return self._send(200, {"status": status, "response": str(r.get("response", "")), "path": str(r.get("path", "")),
                                        "trace": trace(r.get("path"), r.get("response"), status), "why": why, "why_kind": kind,
                                        "ms": int((time.time() - t) * 1000)})
            if u.path == "/api/essay":
                # ProseFold v2: an essay composed from this model's own cited records, with the chosen length, reading level,
                # technical depth and style (profiles measured from the release's corpora); no language model
                import prosefold.options as PO
                topic = re.sub(r"\s+", " ", str(b.get("topic", ""))).strip()[:80]
                if not topic:
                    return self._send(400, {"error": "name a topic"})
                pick = lambda k, allowed, d: b.get(k) if b.get(k) in allowed else d  # noqa: E731
                voice_path = None
                vt = str(b.get("voice_text", "") or "")
                if b.get("style") == "custom" and len(vt.split()) >= 150:
                    LOCAL.mkdir(parents=True, exist_ok=True)
                    voice_path = LOCAL / "essay_voice.txt"
                    voice_path.write_text(vt[:200000], encoding="utf-8")
                elif b.get("style") == "custom":
                    return self._send(400, {"error": "paste at least 150 words of the writing whose voice you want"})
                t = time.time()
                r = PO.write(WB.eng.chat, topic, length=pick("length", PO.LENGTHS, "medium"), level=pick("level", PO.LEVELS, "general"),
                             depth=pick("depth", PO.DEPTHS, "standard"), style=pick("style", PO.STYLES, "plain"), voice_path=voice_path)
                r["ms"] = int((time.time() - t) * 1000)
                return self._send(200, r)
            if u.path == "/api/journal":
                s = settings()
                s["journal"] = bool(b.get("on"))
                save_settings(s)
                return self._send(200, {"on": s["journal"]})
            if u.path == "/api/journal/clear":
                JOURNAL.unlink(missing_ok=True)
                return self._send(200, {"cleared": True})
            if u.path == "/api/new":
                sid = str(b.get("id", "")).strip().lower()
                if not ID.match(sid):
                    return self._send(400, {"error": "an id of lower-case letters, digits and hyphens, 2-41 long"})
                words = [w for w in re.findall(r"[a-z][a-z0-9-]+", str(b.get("words", "")).lower())][:20]
                scaffold(sid, str(b.get("name") or sid)[:80], words, [str(x)[:300] for x in (b.get("examples") or [])][:20])
                return self._send(200, {"id": sid})
            if u.path == "/api/scan":
                rd = sources.scan_local()
                return self._send(200, {"readings": rd})
            if u.path == "/api/scan/save":
                d = exam.make_source(SPECS, "this-computer", "this computer", "MachineOrgan", {"target": "local", "name": "this computer"},
                                     ["computer", "pc", "laptop", "machine", "desktop"])
                exam.start_source(d, machine_probes(sources.scan_local(), "my computer"), on_done=WB.reload)
                return self._send(200, {"id": d.name})
            if u.path in ("/api/server", "/api/server/save"):
                name = re.sub(r"[^A-Za-z0-9 .-]", "", str(b.get("name") or b.get("host") or ""))[:40].strip() or "server"
                host, user, port, key = str(b.get("host", "")).strip(), str(b.get("user", "")).strip(), int(b.get("port") or 22), str(b.get("key", "")).strip()
                rd = sources.scan_server(host, user, port, key)
                if u.path == "/api/server":
                    return self._send(200, {"readings": rd})
                d = exam.make_source(SPECS, "server-" + slug(name), name, "MachineOrgan",
                                     {"target": "server", "name": name, "host": host, "user": user, "port": port, "key": key}, [w for w in slug(name).split("-") if w])
                exam.start_source(d, machine_probes(rd, name), on_done=WB.reload)
                return self._send(200, {"id": d.name})
            if u.path == "/api/files/add":
                name = re.sub(r"[^A-Za-z0-9 .-]", "", str(b.get("name") or "my files"))[:40].strip() or "my files"
                sid = str(b.get("id") or "files-" + slug(name))
                if not ID.match(sid):
                    return self._send(400, {"error": "bad id"})
                d = SPECS / sid
                if not d.exists():
                    exam.make_source(SPECS, sid, name, "FilesOrgan", {"folder": sid + "/files", "name": name}, ["notes", "files", "documents"])
                saved = []
                for f in (b.get("files") or [])[:50]:
                    fn = re.sub(r"[^A-Za-z0-9_.-]", "_", Path(str(f.get("name", ""))).name)[:80]
                    if not re.search(r"\.(csv|tsv|txt|md)$", fn, re.I):
                        continue
                    text = str(f.get("text", ""))
                    if len(text) > 5_000_000:
                        continue
                    (d / "files" / fn).write_text(text, encoding="utf-8")
                    saved.append(fn)
                if not saved:
                    return self._send(400, {"error": "add .csv, .tsv, .txt or .md files (save other documents as text or CSV first)"})
                exam.start_source(d, file_probes(d), on_done=WB.reload)
                return self._send(200, {"id": sid, "saved": saved})
            if u.path == "/api/el/connect":
                key = el_key(b)
                voices = json.loads(el_call("/voices", key)).get("voices", [])
                st = settings()
                if b.get("remember"):
                    st["elevenlabs_key"] = key
                else:
                    st.pop("elevenlabs_key", None)
                save_settings(st)
                return self._send(200, {"voices": [{"id": v["voice_id"], "name": v.get("name", "")} for v in voices][:80],
                                        "remembered": bool(b.get("remember"))})
            if u.path == "/api/el/forget":
                st = settings()
                st.pop("elevenlabs_key", None)
                save_settings(st)
                return self._send(200, {"forgotten": True})
            if u.path == "/api/el/speech":
                key, text = el_key(b), str(b.get("text", ""))[:2500]
                vid = re.sub(r"[^A-Za-z0-9]", "", str(b.get("voice") or "JBFqnCBsd6RMkjVDRZzb"))
                audio = el_call("/text-to-speech/%s?output_format=mp3_44100_128" % vid, key,
                                {"text": text, "model_id": "eleven_multilingual_v2"}, accept="audio/mpeg")
                return self._send(200, None, "audio/mpeg", audio)
            if u.path == "/api/el/image":
                # ElevenLabs Image & Video API: create, poll until completed, download the signed content_url
                key, prompt = el_key(b), str(b.get("prompt", ""))[:1500]
                model = str(b.get("model") or "gemini-2.5-flash-image")
                if model not in ("gemini-2.5-flash-image", "gpt-image-1"):
                    return self._send(400, {"error": "model must be gemini-2.5-flash-image or gpt-image-1"})
                body = {"model_id": model, "prompt": prompt, "aspect_ratio": "16:9" if model.startswith("gemini") else "3:2"}
                gid = json.loads(el_call("/flows/image", key, body))["id"]
                t0, g = time.time(), {}
                while time.time() - t0 < 180:
                    g = json.loads(el_call("/flows/image/%s" % re.sub(r"[^A-Za-z0-9_-]", "", gid), key))
                    if g.get("status") in ("completed", "failed"):
                        break
                    time.sleep(2)
                if g.get("status") != "completed":
                    return self._send(502, {"error": "image not made: %s" % (g.get("failure_reason") or g.get("status") or "timed out")})
                import urllib.request
                try:
                    data = urllib.request.urlopen(g["content_url"], timeout=60).read()
                except Exception:  # noqa: BLE001 - the signed URL normally needs no key; try once with it
                    data = urllib.request.urlopen(urllib.request.Request(g["content_url"], headers={"xi-api-key": key}), timeout=60).read()
                assets = LOCAL / "assets"
                assets.mkdir(exist_ok=True)
                ext = ".png" if "png" in str(g.get("content_mime_type", "")) else ".jpg" if "jp" in str(g.get("content_mime_type", "")) else ".webp"
                (assets / ("image-%s%s" % (time.strftime("%Y%m%d-%H%M%S"), ext))).write_bytes(data)
                return self._send(200, None, g.get("content_mime_type") or "image/png", data)
            if u.path == "/api/el/sound":
                key, prompt = el_key(b), str(b.get("prompt", ""))[:400]
                audio = el_call("/sound-generation", key, {"text": prompt, "duration_seconds": min(22.0, max(2.0, float(b.get("seconds") or 20))),
                                                           "prompt_influence": 0.4}, accept="audio/mpeg")
                return self._send(200, None, "audio/mpeg", audio)
            if u.path == "/api/mcp/connect":
                tools = mcp.connect(str(b.get("name", "")).strip(), str(b.get("command", "")).strip(), str(b.get("url", "")).strip(),
                                    str(b.get("token", "")).strip())
                return self._send(200, {"tools": tools})
            if u.path == "/api/mcp/save":
                server, tools = str(b.get("name", "")).strip(), [str(t) for t in (b.get("tools") or [])][:40]
                if server not in mcp.servers() or not tools:
                    return self._send(400, {"error": "connect the server and pick at least one tool"})
                sid = "mcp-" + slug(server)
                ex = [(str(x.get("q", ""))[:300], (str(x.get("want")) if x.get("want") else None)) for x in (b.get("examples") or [])][:20]
                probes = [p for p in ex if p[0]] + [("What is the capital of France?", None), ("Who wrote Hamlet?", None)]
                d = exam.make_source(SPECS, sid, "%s tools" % server, "mcp.McpOrgan", {"server": server, "tools": tools, "name": server, "folder": sid},
                                     [w for w in mcp.words(server)] or ["mcp"])
                exam.start_source(d, probes, on_done=WB.reload)
                return self._send(200, {"id": sid})
            if u.path == "/api/feedback":
                m = re.match(r"^yours:([a-z0-9-]+)>", str(b.get("path", "")))
                right = bool(b.get("right"))
                if not m or not (SPECS / m.group(1)).is_dir():
                    return self._send(200, {"learned": False, "note": "marks teach your own specialists; this answer came from the core"})
                d = SPECS / m.group(1)
                tool = re.search(r"tool ([\w.-]+)\(", str(b.get("response", "")))
                if (exam.read_manifest(d) or {}).get("organ", {}).get("module", "").startswith("organ_mcp") or tool:
                    e = mcp.learn(d / "credit.json", tool.group(1), str(b.get("q", "")), right) if tool else {}
                    exam.start_source(d, None, on_done=WB.reload)        # the lane check runs again after learning
                    return self._send(200, {"learned": True, "tool": tool.group(1) if tool else None, "credit": e})
                return self._send(200, {"learned": False, "note": "noted; only tool specialists learn from marks"})
            if u.path == "/api/conv/rename":
                c = conv_load(str(b.get("id", "")))
                c["title"] = str(b.get("title", ""))[:120]
                conv_path(c["id"]).write_text(json.dumps(c, indent=0), encoding="utf-8")
                return self._send(200, {"ok": True})
            if u.path == "/api/conv/delete":
                conv_path(str(b.get("id", ""))).unlink(missing_ok=True)
                return self._send(200, {"ok": True})
            if u.path == "/api/conv/delete_all":
                for p in CONVS.glob("*.json"):
                    p.unlink()
                return self._send(200, {"ok": True})
            if u.path == "/api/conv/keep":
                st = settings()
                st["keep_conversations"] = bool(b.get("on"))
                save_settings(st)
                return self._send(200, {"keep": st["keep_conversations"]})
            if u.path == "/api/conv/specialist":
                cid, days = str(b.get("id", "")), max(1, min(365, int(b.get("days") or 7)))
                c = conv_load(cid)
                done = [t for t in c["turns"] if t.get("status") == "answered" and not str(t.get("path", "")).startswith("workbench:")]
                if not done:
                    return self._send(400, {"error": "this conversation has no answers to remember yet"})
                sid = ("chat-" + slug(c.get("title") or cid))[:34].rstrip("-") + "-" + cid[:4]
                d = exam.make_source(SPECS, sid, "conversation: " + (c.get("title") or cid)[:60], "ConversationOrgan",
                                     {"conv": cid, "name": (c.get("title") or cid)[:60]}, ["conversation", "earlier"])
                m = exam.read_manifest(d)
                m["expires"] = time.time() + days * 86400
                m["temporary"] = True
                (d / "manifest.json").write_text(json.dumps(m, indent=1), encoding="utf-8")
                probes = []
                for t in done[:8]:
                    ws = [w for w in sources._words(t["q"]) if w not in sources.RECALL_FILLER][:3]
                    if ws:
                        probes.append(("What did we say earlier about %s?" % " ".join(ws), t["q"][:40]))
                probes += [("What is the capital of France?", None), ("Who wrote Hamlet?", None), ("Who directed Jaws?", None)]
                exam.start_source(d, probes, on_done=WB.reload)
                return self._send(200, {"id": sid, "expires": m["expires"]})
            if u.path == "/api/verify":
                return self._send(200, verify.verify_install())
            if u.path == "/api/verify/chain":
                return self._send(200, verify.check_anchor(str(b.get("signature") or "") or None))
            if u.path == "/api/sensor/test":
                cfg = {"kind": str(b.get("kind", "")), "address": str(b.get("address", "")).strip(), "user": str(b.get("user", "")),
                       "password": str(b.get("password", ""))}
                if cfg["kind"] == "http" and not re.match(r"^https?://", cfg["address"]):
                    return self._send(400, {"error": "the address must start with http:// or https://"})
                vals, where = sensors.read_source(cfg)
                return self._send(200, {"source": where, "fields": [{"path": k, "value": v, "guess": sensors.guess_quantity(k)}
                                                                   for k, v in list(vals.items())[:60]]})
            if u.path == "/api/sensor/add":
                name = re.sub(r"[^A-Za-z0-9 .-]", "", str(b.get("name") or "my sensor"))[:40].strip() or "my sensor"
                fields = [{"path": str(f["path"])[:120], "quantity": str(f["quantity"])[:40], "unit": str(f.get("unit") or "")[:12]}
                          for f in (b.get("fields") or []) if f.get("path") and f.get("quantity")][:30]
                if not fields:
                    return self._send(400, {"error": "pick at least one reading and say what it measures"})
                sid = "sensor-" + slug(name)
                c = {"id": sid, "name": name, "kind": str(b.get("kind", "")), "address": str(b.get("address", "")).strip(),
                     "interval": max(5, min(3600, int(b.get("interval") or 30))), "fields": fields,
                     "user": str(b.get("user", "")), "password": str(b.get("password", "")), "added": int(time.time())}
                sensors.save_config(c)
                sensors.poll_once(c)
                sensors.start_poller(sid)
                d = exam.make_source(SPECS, sid, name, "sensors.SensorOrgan", {"sensor": sid, "name": name},
                                     [w for w in slug(name).split("-") if w] or ["sensor"])
                qs = sorted({f["quantity"] for f in fields})
                probes = [("What is the %s on %s?" % (qq, name), qq) for qq in qs]
                probes += [("What is the temperature of the Sun?", None), ("How much does a litre of water weigh?", None)]
                exam.start_source(d, probes, on_done=WB.reload)
                return self._send(200, {"id": sid})
            if u.path == "/api/sensor/remove":
                sid = str(b.get("id", ""))
                if not ID.match(sid):
                    return self._send(400, {"error": "bad id"})
                for p in (sensors.DIR / ("%s.json" % sid), sensors.DIR / ("%s.jsonl" % sid)):
                    p.unlink(missing_ok=True)
                shutil.rmtree(SPECS / sid, ignore_errors=True)
                WB.reload()
                return self._send(200, {"removed": sid})
            if u.path == "/api/solana/rpc":
                raw = json.dumps(b).encode()
                out = registry.relay(raw)
                return self._send(200, None, "application/json", out)
            if u.path == "/api/registry/record":
                sid = str(b.get("id", ""))
                if not ID.match(sid) or not (SPECS / sid).is_dir():
                    return self._send(400, {"error": "no such specialist"})
                return self._send(200, {"records": registry.record(SPECS / sid, str(b.get("kind", "")), str(b.get("signature", "")).strip())})
            if u.path == "/api/registry/check":
                sid = str(b.get("id", ""))
                if not ID.match(sid) or not (SPECS / sid).is_dir():
                    return self._send(400, {"error": "no such specialist"})
                return self._send(200, registry.check(SPECS / sid))
            if u.path == "/api/example":
                src = HERE / "examples" / "habitable-zone"
                if (SPECS / src.name).exists():
                    return self._send(400, {"error": "the example is already in your specialists"})
                shutil.copytree(src, SPECS / src.name, ignore=shutil.ignore_patterns("__pycache__", "verdict_*", "exam_log*"))
                return self._send(200, {"id": src.name})
            if u.path == "/api/file":
                d, name = SPECS / str(b.get("id", "")), str(b.get("name", ""))
                if not ID.match(str(b.get("id", ""))) or not d.is_dir() or not FNAME.match(name) or name.startswith("verdict_"):
                    return self._send(400, {"error": "that file cannot be written here"})
                (d / name).write_text(str(b.get("text", "")), encoding="utf-8")
                WB.reload()
                return self._send(200, {"saved": name, "status": exam.status(d)})
            if u.path == "/api/exam":
                sid, split = str(b.get("id", "")), str(b.get("split", "dev"))
                if not ID.match(sid) or not (SPECS / sid).is_dir() or split not in ("dev", "heldout"):
                    return self._send(400, {"error": "which specialist, and dev or heldout?"})
                exam.start(SPECS / sid, split, WB.eng, on_done=WB.reload)
                return self._send(200, exam.progress(sid))
            if u.path == "/api/package":
                sid = str(b.get("id", ""))
                if not ID.match(sid) or not (SPECS / sid).is_dir():
                    return self._send(400, {"error": "no such specialist"})
                return self._send(200, package(sid))
            if u.path == "/api/import":
                r = import_zip(str(b.get("path", "")))
                return self._send(200, r)
            if u.path == "/api/code/run":
                return self._send(200, run_code(str(b.get("code", ""))[:100_000], str(b.get("tests", ""))[:50_000]))
        except ValueError as e:
            return self._send(400, {"error": str(e)})
        except Exception as e:  # noqa: BLE001
            return self._send(500, {"error": "%s: %s" % (type(e).__name__, e)})
        return self._send(404, {"error": "not found"})


def serve(engine, port=8177):
    global WB
    WB = Workbench(engine)
    sensors.start_all()
    srv = ThreadingHTTPServer(("127.0.0.1", port), H)
    print("Oracle7 Workbench (%s) on http://127.0.0.1:%d/" % (engine.tip, port), flush=True)
    srv.serve_forever()
