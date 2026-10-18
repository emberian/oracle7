"""cli - Oracle7 from the terminal. Everything the Workbench page does that makes sense in a terminal, with the same code,
so an answer here is the answer the page gives. `python oracle7.py help` lists the commands.

  ask "question" [--json]        one question: the answer, its status and the path it took (your specialists included)
  chat                           a conversation (follow-ups work); /help, /path, /new, /quit inside
  specialists [word]             the 267 admitted specialists (and yours), with held-out scores
  card <id>                      one specialist's card
  systems                        the five systems built the same way
  verify [--chain]               check this install against RELEASE_HASHES.json (and the root against its Solana anchor)
  mine                           your specialists and their state
  new <id> [words...]            scaffold a specialist in workbench/local/specialists/<id>
  example                        install the worked example (habitable zone)
  exam <id> dev|heldout          run its exam (held-out: once) and print the verdict
  scan                           read this computer (system, CPU, memory, disks, uptime, top processes)
  sensors                        your sensors: read each once now and print the newest values
  sensor-test <kind> <address>   read a sensor once and list the numbers found (kinds: http mqtt serial file simulated)
  history [id]                   saved conversations, or one conversation's turns
  essay "topic" [options]        ProseFold: an essay composed from this model's own records, no language model; options
                                 --length short|medium|long|full --level young|general|advanced --depth basic|standard|technical
                                 --style plain|encyclopedic|textbook|prometheus7 --voice <your writing.txt>
  registry <id>                  a specialist's on-chain registrations and attestations, with each signer's $ORACLE7
  registry-memo <id> register|attest   the memo to sign (in the Workbench's Share tab, or any wallet that signs memos);
                                 then: registry-record <id> register|attest <signature>
  serve [port] | workbench [port] | setup | help
Add --json to ask, specialists, verify, mine, scan and sensors for machine-readable output."""
from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
STAGE = {"L0": "Intake", "L1": "Parse", "L2": "Route", "L3": "Conversation", "L4": "Speak & verify", "L5": "Self-model",
         "S": "Specialists", "E": "Engines", "V": "Knowledge vault"}
COMMANDS = {"ask", "chat", "specialists", "card", "systems", "verify", "mine", "new", "example", "exam", "scan", "sensors",
            "sensor-test", "history", "help", "registry", "registry-memo", "essay"}


def out(obj, as_json, text):
    print(json.dumps(obj, indent=1, ensure_ascii=False, default=str) if as_json else text)


def path_line(steps):
    return " -> ".join("%s: %s" % (STAGE.get(s, s), m) if m else STAGE.get(s, s) for s, m in steps)


class Session:
    """the Workbench's own answering (core + your specialists, readers first when addressed, history, help)"""

    def __init__(self, engine):
        import server
        self.server = server
        server.WB = server.Workbench(engine)
        self.wb = server.WB

    def ask(self, text, sid):
        r = self.wb.chat(text, sid)
        st = r.get("status")
        why = None if st == "answered" else self.server.why_declined(r.get("path"))[1]
        steps = self.server.trace(r.get("path"), r.get("response"), st)
        if self.server.settings().get("keep_conversations") and self.server.CID.match(sid):
            self.server.conv_add(sid, {"t": int(time.time()), "q": text, "status": st, "response": str(r.get("response", "")),
                                       "path": str(r.get("path", "")), "trace": steps, "why": why, "ms": 0})
        return {"status": st, "response": str(r.get("response", "")), "path": str(r.get("path", "")), "why": why, "trace": steps}


def show_answer(r, as_json):
    if as_json:
        return out(r, True, "")
    print(r["response"].strip() or "(no answer)")
    if r["why"]:
        print("  why: %s" % r["why"])
    print("  [%s] %s" % (r["status"], path_line(r["trace"])))


def specialists_data():
    import server
    return server.specialists_payload()


def main(argv, engine_factory):
    a = list(argv)
    as_json = "--json" in a
    a = [x for x in a if x != "--json"]
    cmd, rest = a[0], a[1:]
    if cmd == "help":
        print(__doc__.split("\n\n", 1)[1])
        return 0
    if cmd == "specialists":
        d = specialists_data()
        w = " ".join(rest).lower()
        items = [x for x in d["items"] if not w or w in (x["name"] + " " + x["id"] + " " + " ".join(x["takes"])).lower()]
        lines = ["%-34s %-17s %s" % (x["id"][:34], x["group"][:17], ("%s/%s vs core %s" % (x["heldout"][0], x["heldout"][2], x["heldout"][1])) if x["heldout"] else "")
                 for x in items]
        lines += ["%-34s %-17s %s" % (y["id"][:34], "yours", y["state"]) for y in d["yours"] if not w or w in y["id"]]
        out({"items": items, "yours": d["yours"]}, as_json, "\n".join(lines) + "\n%d specialists%s" % (len(items), " matching '%s'" % w if w else ""))
        return 0
    if cmd == "card":
        if not rest:
            print("usage: card <id>")
            return 2
        f = HERE / "data" / "cards" / (rest[0] + ".md")
        if f.exists():
            print(f.read_text(encoding="utf-8"))
            return 0
        x = next((x for x in specialists_data()["items"] if x["id"] == rest[0]), None)
        if not x:
            print("no specialist %s (try: specialists <word>)" % rest[0])
            return 1
        print("%s\n%s · takes: %s\nheld-out: %s" % (x["name"], x["group"], ", ".join(x["takes"]), x["heldout"]))
        return 0
    if cmd == "systems":
        s = json.loads((HERE / "data" / "systems.json").read_text(encoding="utf-8"))
        out(s, as_json, "\n\n".join("%s (%s)\n%s\n%s" % (x["name"], x["id"], x["does"], "\n".join("  - " + m for m in x["measured"])) for x in s["items"]))
        return 0
    if cmd == "verify":
        import verify
        v = verify.verify_install()
        ok = v["root_matches"] and not v["changed"]
        txt = "%s: %d of %d parts, %d specialist folders\npublished root %s\ncomputed root  %s" % (
            "VERIFIED" if ok else "DOES NOT MATCH", v["verified"], v["parts"], v["specialists_verified"], v["published_root"], v["computed_root"])
        if v["changed"]:
            txt += "\nchanged: " + ", ".join(v["changed"])
        if v["missing"]:
            txt += "\nmissing: " + ", ".join(v["missing"])
        if "--chain" in rest:
            try:
                c = verify.check_anchor()
                v["anchor_check"] = c
                txt += "\nSolana anchor: %s (slot %s) %s" % ("root is on-chain" if c["root_on_chain"] else "root NOT in that transaction", c["slot"], c["explorer"])
            except Exception as e:  # noqa: BLE001
                txt += "\nSolana anchor: %s" % e
        out(v, as_json, txt)
        return 0 if ok else 1
    if cmd == "mine":
        d = specialists_data()["yours"]
        out(d, as_json, "\n".join("%-36s %-9s %s" % (y["id"], y["state"], y.get("note", "")) for y in d) or "none yet (try: new <id>, example, or the Workbench)")
        return 0
    if cmd == "new":
        import server
        if not rest or not server.ID.match(rest[0]):
            print("usage: new <id> [words...]   (id: lower-case letters, digits, hyphens)")
            return 2
        d = server.scaffold(rest[0], rest[0], [w.lower() for w in rest[1:]])
        print("made %s\nedit %s, write held-out items in panel.json, then: exam %s dev" % (d, d / ("organ_%s.py" % rest[0].replace("-", "_")), rest[0]))
        return 0
    if cmd == "example":
        import shutil
        import server
        dst = server.SPECS / "habitable-zone"
        if dst.exists():
            print("already installed: %s" % dst)
            return 0
        shutil.copytree(HERE / "examples" / "habitable-zone", dst)
        print("installed %s\nnext: exam habitable-zone dev, then exam habitable-zone heldout" % dst)
        return 0
    if cmd == "scan":
        import sources
        rd = sources.scan_local()
        out(rd, as_json, "\n".join("%-22s %s   [%s]" % ("%s %s" % (r["entity"], r["signal"]), r["text"], r["source"]) for r in rd))
        return 0
    if cmd == "sensor-test":
        import sensors
        if len(rest) < 1:
            print("usage: sensor-test <http|mqtt|serial|file|simulated> <address>")
            return 2
        vals, where = sensors.read_source({"kind": rest[0], "address": rest[1] if len(rest) > 1 else ""})
        out({"source": where, "fields": vals}, as_json, "read from %s\n%s" % (where, "\n".join("  %-30s %-12s guess: %s" % (k, v, sensors.guess_quantity(k)) for k, v in vals.items())))
        return 0
    if cmd == "sensors":
        import sensors
        res = []
        for sid, c in sorted(sensors.configs().items()):
            try:
                rows = sensors.poll_once(c)
                res.append({"id": sid, "name": c["name"], "rows": rows})
            except Exception as e:  # noqa: BLE001
                res.append({"id": sid, "name": c["name"], "error": str(e)})
        txt = "\n".join("%s: %s" % (x["name"], x.get("error") or "; ".join("%s %s %s%s" % (r["q"], r["v"], r["unit"], "" if r["ok"] else " (REJECTED: %s)" % r["why"])
                                                                            for r in x["rows"])) for x in res)
        out(res, as_json, txt or "no sensors (connect one in the Workbench, Sensors tab)")
        return 0
    if cmd in ("registry", "registry-memo", "registry-record"):
        import registry
        import server
        if not rest or not (server.SPECS / rest[0]).is_dir():
            print("usage: registry <id> | registry-memo <id> register|attest | registry-record <id> register|attest <signature>")
            return 2
        d = server.SPECS / rest[0]
        if cmd == "registry-memo":
            print(registry.memo_for(d, rest[1] if len(rest) > 1 else "register"))
            return 0
        if cmd == "registry-record":
            recs = registry.record(d, rest[1], rest[2])
            print("recorded: %d record(s) for %s" % (len(recs), rest[0]))
            return 0
        c = registry.check(d)
        txt = "%s: %s, %d attestation(s), vouching wallets hold %s $ORACLE7\n" % (
            c["id"], "registered" if c["registered"] else "not registered", c["attestations"], c["vouching_oracle7"])
        txt += "\n".join("  %-8s %s %s %s %s" % (r.get("kind"), (r.get("signer") or "")[:12] + "...", time.strftime("%Y-%m-%d %H:%M", time.gmtime(r["time"])) if r.get("time") else "",
                                                 "matches" if r.get("matches_files") else ("ERROR " + r["error"] if r.get("error") else "DOES NOT MATCH"),
                                                 "%s $ORACLE7" % r.get("oracle7", "")) for r in c["records"])
        out(c, as_json, txt)
        return 0
    if cmd == "history":
        import server
        if rest:
            c = server.conv_load(rest[0])
            print("\n".join("> %s\n  %s [%s]" % (t["q"], str(t.get("response", ""))[:300].replace("\n", " "), t.get("status")) for t in c["turns"]) or "empty")
        else:
            print("\n".join("%s  %s  %d turns  %s" % (c["id"], time.strftime("%Y-%m-%d %H:%M", time.localtime(c["updated"])), c["turns"], c["title"])
                            for c in server.conv_list()) or "no saved conversations")
        return 0
    # the rest needs the core
    eng = engine_factory()
    if cmd == "essay":
        import prosefold.options as PO
        opt = {"length": "medium", "level": "general", "depth": "standard", "style": "plain"}
        voice = None
        for flag in ("--length", "--level", "--depth", "--style", "--voice"):
            if flag in rest:
                i = rest.index(flag)
                val = rest[i + 1] if i + 1 < len(rest) else ""
                rest = rest[:i] + rest[i + 2:]
                if flag == "--voice":
                    voice = val
                else:
                    opt[flag[2:]] = val
        allowed = {"length": PO.LENGTHS, "level": PO.LEVELS, "depth": PO.DEPTHS, "style": PO.STYLES}
        bad = [k for k, v in opt.items() if v not in allowed[k]]
        if not rest or bad:
            print('usage: essay "topic" [--length short|medium|long|full] [--level young|general|advanced]\n'
                  '                     [--depth basic|standard|technical] [--style plain|encyclopedic|textbook|prometheus7] [--voice file]')
            return 2
        r = PO.write(eng.chat, " ".join(rest), voice_path=voice, **opt)
        if as_json:
            return out(r, True, "") or 0
        print(r["essay_md"])
        print("[prosefold] %d sentences from %d records, %d of %d checked word for word against their sources; reading grade %s "
              "(asked %s%s); no language model" % (r["sentences"], r["records_used"], r["faithful"], r["sentences"], r["reading_grade"],
                                                  opt["level"], "" if r["level_reached"] else ", the record could not get closer"))
        return 0 if r["sentences"] else 1
    sess = Session(eng)
    if cmd == "ask":
        if not rest:
            print('usage: ask "question" [--json]')
            return 2
        show_answer(sess.ask(" ".join(rest), "cli%d" % int(time.time())), as_json)
        return 0
    if cmd == "exam":
        import exam
        import server
        if len(rest) < 2 or rest[1] not in ("dev", "heldout"):
            print("usage: exam <id> dev|heldout")
            return 2
        d = server.SPECS / rest[0]
        if not d.is_dir():
            print("no specialist %s in %s" % (rest[0], server.SPECS))
            return 1
        if rest[1] == "heldout" and input("The held-out set is used once. Run it? [y/N] ").strip().lower() != "y":
            return 1
        v = exam.run(d, rest[1], eng)
        print("%s EXAM %s: %s" % (rest[1].upper(), rest[0], v["decision"]))
        print("  domain   %d/%d with it, %d/%d core alone (gain needed %d)" % (v["with_specialist"]["ok"], v["n"], v["head"]["ok"], v["n"], v["gain_needed"]))
        print("  false yes %d (core %d) · wrong %d · lane %d/%d (cap %d) · self %s · median %.1f ms" % (
            v["with_specialist"]["fy"], v["head"]["fy"], v["with_specialist"]["wrong"], v["core"]["taken"], v["core"]["n"], v["core"]["cap"],
            "ok" if v["self_ok"] else "FAIL", v["p50_ms"]))
        for r in v["reasons"]:
            print("  - " + r)
        for f in v["fails"][:8]:
            print("  not right: %s | expected %s | got %s" % (f["q"][:60], f["expected"][:30], f["got"][:60]))
        return 0
    if cmd == "chat":
        sid = "cli%d" % int(time.time())
        print("Oracle7 (%s). Ask anything. /path shows the last path, /new starts over, /help lists Workbench features, /quit leaves." % eng.tip)
        last = None
        while True:
            try:
                q = input("> ").strip()
            except (EOFError, KeyboardInterrupt):
                print()
                return 0
            if not q:
                continue
            if q in ("/quit", "/exit"):
                return 0
            if q == "/new":
                sid = "cli%d" % int(time.time())
                print("(new conversation)")
                continue
            if q == "/path":
                print(path_line(last["trace"]) if last else "(nothing asked yet)")
                continue
            last = sess.ask(q, sid)
            print(last["response"].strip() or "(no answer)")
            if last["why"]:
                print("  why: %s" % last["why"])
    print("unknown command %s; try: help" % cmd)
    return 2
