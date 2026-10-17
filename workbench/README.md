# Oracle7 Workbench

A local page for your copy of Oracle7. It shows the model as a diagram, lights the path each answer takes, and lets you
add to the model: readers of your computer, servers, files and MCP tools, and specialists you write and examine yourself.

```bash
python oracle7.py --workbench          # opens http://127.0.0.1:8177/ in your browser
python oracle7.py --workbench 8200     # another port
```

It runs on the same CPU-only install as the model. The server listens on 127.0.0.1 only and sends nothing anywhere,
except to services you connect yourself (an SSH server, an MCP server, a sensor, ElevenLabs) and the optional Solana check. Type `/help` or ask
"what can you do?" in the chat for a guide to every feature and command.

## From a terminal

Everything that makes sense in a terminal works there too, with the same code, so a terminal answer is the page's answer:

```bash
python oracle7.py ask "Who directed Jaws?"            # the answer, its status and the path it took
python oracle7.py ask "..." --json                     # machine-readable
python oracle7.py chat                                 # a conversation; /path, /new, /help, /quit
python oracle7.py specialists moons                    # find specialists, with held-out scores
python oracle7.py card astronomy-v3                    # one specialist's card
python oracle7.py verify --chain                       # this install against RELEASE_HASHES.json and the Solana anchor
python oracle7.py example && python oracle7.py exam paint-coverage dev
python oracle7.py new beekeeping hive bees honey       # scaffold your own specialist
python oracle7.py scan                                 # read this computer
python oracle7.py sensor-test http http://192.168.1.40/data
python oracle7.py sensors                              # read every connected sensor once
python oracle7.py history                              # saved conversations
python oracle7.py registry paint-coverage               # its on-chain registration and attestations
python oracle7.py help                                 # all of it
```

## The layout

The layout has three panes, plus a Conversations panel you can open and collapse:

- **Far left (the button at the top): Conversations.** Every conversation is kept on this computer. Open one and carry on:
  the core picks up its context, so "when was he born?" still means the person you were talking about. You can rename,
  search or delete conversations, or switch keeping off. "Make specialist" turns a conversation into a temporary specialist
  (7 days unless you choose) that answers "what did we say earlier about…?" by quoting the earlier answer with its date
  and route. The Workbench also answers "what did I ask first?" and "what did you just say?" from the conversation itself.
- **Left: the conversation.** The diagram of the whole model sits above it. Each answer lights the stages and modules it
  passed through. When Oracle7 declines, the answer says why.
- **Top right: the workspace,** in tabs: Start, Specialists, Sensors, Systems, Build, Gaps, Code, Film, Share.
- **Bottom right: the live log** of every turn, route, exam and change.

## Start: point it at something of yours

| | What it reads | Ask it |
|---|---|---|
| **Scan this computer** | system, CPU, memory, disks, uptime, the processes using the most memory (figures and process names only, never your files) | "How much disk space is free on my computer?" |
| **Connect a server** | over SSH with your own key, a fixed list of read-only commands: hostname, uptime, load, memory, disks, top processes, failed services | "How much memory is web server using?" |
| **Add files** | tables (.csv, .tsv) and text (.txt, .md), copied into the reader's own folder | "What is the price of honey?" · "What do my notes say about the boiler?" |
| **Connect an MCP server** | the tools of any MCP server, by command (stdio) or URL | "Count the words in 'the quick brown fox'" |
| **Connect a sensor** | an HTTP device or hub (JSON or Prometheus metrics), an MQTT topic, a USB/serial device, a log file, or a simulated garden node | "What is the soil moisture on garden node?" · "Show my sensor readings" |

Each becomes a reader whose answers name exactly where the value came from:
- the system call;
- the command;
- the file with its row and column, or line;
- the tool with the arguments it was sent.

Before a reader joins your model it passes an automatic check:
- it reads its own source back correctly;
- it declines general questions;
- it takes at most 9 of the 924 published general questions;
- it leaves identity questions alone;
- it answers within its time budget.

**MCP specialists adapt.** A tool specialist routes each question to the tool whose name, description and learned words
match it. It fills the tool's arguments from the question, or says which argument is missing. Mark its answers right or
wrong:
- A right mark teaches the tool the question's words.
- A wrong mark counts against the tool. After three wrongs, if wrongs outnumber rights, the tool is no longer used.

Every mark re-runs the check. Bad lessons therefore take the specialist out of your model rather than widen what it
answers.

## Sensors

Connect a sensor from Start or the Sensors tab:
- **Test** reads it once and lists the numbers it found, with a guess at what each measures: temperature, humidity, soil
  moisture, pressure, CO2, light, PM2.5, voltage, battery, wind, rain, power, energy, water level, or a name you give.
- **Add** polls it in the background (every 30 s unless you choose) and keeps 24 hours of readings in
  `workbench/local/sensors/`.

The Sensors tab shows each sensor's newest values with a 24-hour line.

Every answer gives:
- the value and its unit;
- how old the reading is, and says so if the sensor seems offline;
- whether it was measured or simulated;
- its source, down to the field;
- min, max and mean for the day, and the last hour's trend, when you ask for them.

A value outside the physical range of its quantity (412 °C for air, 140% humidity) is rejected. The answer says which
reading was rejected and why, and uses the last valid one.

| Connection | Address | Notes |
|---|---|---|
| HTTP | `http://192.168.1.40/data` | JSON (any nesting) or Prometheus text metrics; ESP32, Shelly, Tasmota, Home Assistant, weather stations |
| MQTT | `broker:1883/garden/node1` | read-only subscribe, MQTT 3.1.1; JSON or a plain number per message |
| USB / serial | `COM3@9600` or `/dev/ttyUSB0@9600` | lines like `temp=21.4 hum=40`, `21.4,40` or JSON; needs `pip install pyserial` on Windows and macOS |
| Log file | `C:\logs\garden.csv` | the newest line of a CSV (with header), JSON-lines or key=value log |
| Simulated | none | a made-up garden node for trying it; every answer says SIMULATED |

## Build: write a specialist and examine it

"New specialist" makes a folder you edit in the page:
- `manifest.json`: what it takes and its sources;
- an organ: rules, tables or computation, no language model;
- `panel.json`: dev items and held-out items;
- `scorer.py`.

"Add the worked example" installs a complete one that works out paint coverage.

- **Dev exam:** run it as often as you like.
- **Held-out exam:** run it once. Its items are hashed and logged, and the same held-out set is refused a second time.

A specialist joins your model only if all of these hold on its held-out items:

1. **Domain:** with it, your model gets at least max(3, 2% of n) more right than without it.
2. **No false yes:** it answers no more must-decline items than the core alone.
3. **Few wrong:** at most max(1, 2% of n) answered wrong.
4. **Stays in lane:** it would take at most max(5, 1%) of 924 general questions.
5. **Self:** identity questions stay the core's.
6. **Budget:** median reply time within its budget.

This is the same idea as the gate that admitted the release's own specialists, made portable. An admitted specialist
appears on the diagram's Specialists ring. It answers only where the core declined for lack of a reading. It never
replaces an answer the core gave, and it never answers where a check stopped the core (false premise, private question,
changed sign). If you change one of its files, it leaves your model until it passes a new held-out set.

## Gaps: the model tells you what it is missing

Turn on the gap journal and every question you ask, answered or not, is kept in `workbench/local/journal.jsonl`, on
this machine only. Declines are grouped by why they happened and by the words they share. "Start a specialist" turns a
group into a new specialist whose first dev items are your own questions. That is the loop by which your copy improves:
- declines show what is missing;
- you, or tools you trust, write a specialist;
- the exam decides whether it joins.

Nothing joins without passing.

## Code

The code organ hands over only programs it has run. It writes and proves functions from a fixed set:
- a small website;
- palindromes, factorials, vowel and word counts, word frequencies;
- HTTP routes, regular-expression extraction, memoisation;
- a bank-account class, matrix multiplication, fizzbuzz, fibonacci;
- string reversal, a JSON round-trip, concurrent work;
- binary search, tower of hanoi, quicksort, list sums, prime tests;
- a number-guessing game and tic tac toe.

It declines anything else. The bench runs any code against your own tests, in a separate Python process with a
10-second limit.

## Film

Record answers as a video (1280×720 .webm, made in your browser).
- The left of the frame shows the diagram tracing each path.
- The right shows the question, the answer and the path step by step.

Every new answer is ticked; untick any to leave it out. "Film this" under an answer records just that one. Keep the tab
in front while it records: if you switch away, recording pauses and picks up where it stopped.

You can optionally connect your own ElevenLabs account. This is the only feature that sends content to a third party:
the narration text, the sound description and the image prompts. It can:
- narrate each answer in a voice you pick;
- lay a sound you describe underneath;
- open each answer with a generated illustration. This uses Gemini 2.5 Flash Image or GPT Image 1 through the ElevenLabs
  Image & Video API, which needs their Pro plan. The film labels these images as generated.

The key stays in the page unless you tick "remember on this computer".

## Verify

Specialists > Verify this install (or `/verify`) recomputes the SHA-256 of every shipped part and rebuilds the Merkle root
published in `RELEASE_HASHES.json`. The parts are all 307 specialist folders, the admitted fold chain, the workbench, the
launcher and the store manifest. A changed or missing specialist is listed by name.

"Check the anchor on Solana" then reads the release's anchor transaction from a public Solana RPC. This is read-only and
the only network call Verify makes. It confirms the memo carries the same root.

## The $ORACLE7 registry: one specialist, one $ORACLE7

A specialist you built and examined becomes **verified on-chain** when you register it (Share > Register on Solana, or
`python oracle7.py registry-memo <id> register`). Registering is one Solana transaction, signed in your own wallet (Phantom),
that does two things together:
- it **burns exactly 1 $ORACLE7** from your wallet (mint `DU7Lhe2QtcRBJdor7KbpjfUDmLyA2kdhR49Li3czpump`);
- it records the specialist's fingerprint in a memo: the SHA-256 of its files, of its held-out exam verdict and of its
  held-out set, and the release it was examined on.

Before your wallet is asked, the Workbench simulates the exact transaction on Solana and stops if it would fail (for example a
balance under 1 $ORACLE7). Anyone who imports the specialist and sees it pass its held-out exam on their own machine can
**Attest** for free.

**Check on Solana** (or `python oracle7.py registry <id>`) reads every registration and attestation back from the chain and
confirms each one:
- that the memo matches the specialist's files as they are now;
- that a registration burned 1 $ORACLE7, signed by the same wallet.

It shows each signer and how much $ORACLE7 they hold. The records live in the specialist's `registry.json` and travel with
it when shared. The Workbench never sees a key. The only token that moves is that one burn, which you approve in your
wallet. The public Solana RPC refuses browser pages, so the page's few read calls go through the local Workbench server.

## Share

Share packages an admitted specialist for the community registry: its folder, its exam verdict and the SHA-256 of every
file. Upload it with your own Hugging Face account using the command it prints. To import a shared specialist, give the
path of its .zip:
- every hash is checked;
- its verdict is set aside;
- it joins your model only after it passes its held-out exam on your machine.

Readers of your computer, servers and files are never packaged.

## What comes with it

**267 specialists.** Each was admitted by a held-out exam it saw once. The Specialists tab lists every one with its
held-out score against the core alone and its card. The 23 failed exams are published.

| Group | Count | Examples |
|---|---:|---|
| Relation readers | 161 | moons, directors, novels, painters, composers, airports, battles, bridges: each reads one family of Wikidata relations and names the record |
| Earth & life | 26 | geology, hydrology, soil, ecology, botany, medicine, genetics, meteorology |
| Everyday | 22 | warehouse, cold chain, cooking, first aid, fleet, retail, wiring, woodworking |
| Physical science | 21 | acoustics, chemistry, densities, decay, energy, optics, thermo, units |
| Humanities | 16 | law, grammar, literature, music, economics, world history |
| Computing | 10 | python, javascript, sql, git, linux, networking, data formats |
| Space | 6 | astronomy, orbits, planetary, spacecraft, space comms |
| Mathematics | 5 | calculus, geometry, statistics, logic, algorithms |

**Five systems built the same way.** Each is its own repository in the release, with no language model, a receipt for
every decision, and held-out results run once.

| System | What it does | Measured |
|---|---|---|
| **DeepSpace** | fault response for deep-space spacecraft, from telemetry to admissible response | 98.9% on 1,700 fresh single faults, 0 harmful (baseline 29.4%) |
| **Trafficcop** | a decision service: one choice from a set of options, with a receipt, or abstain | 30/32 held-out routes; about 0.1 ms a decision |
| **Chameleon** | builds websites and components; done only when contracts written in advance pass in a browser | 0 false completions on held-out repositories |
| **Vision** | sees with no trained weights; cites the stored examples behind every answer | MNIST 98.58%, Fashion-MNIST 90.46%, CIFAR-10 62.99% |
| **Artist** | images by citation: every object is a real photographed instance, cited | GenEval-style 50.9% on 2,212 images (independent judge) |

## Essays: ProseFold

```bash
python oracle7.py essay "volcano"
python oracle7.py essay "volcano" --voice my_writing.md
```

`essay` writes a few paragraphs about a topic from this model's own cited answers, with no language model. It asks the
model the questions a writer would (what it is, how it works, where it is used, its history), keeps only the sentences
that came back with a record id, and arranges them. ProseFold chooses the arrangement: where sentences join with "and" or
a semicolon, where a short sentence stands alone, where "it" replaces the subject. It searches those choices for the voice
closest to a target text (by default Prometheus7's essay *The Slow Fire*; `--voice` takes any text of yours) on four
measures a composition can change: comma rhythm, sentence-length spread, longest sentence and short "snap" sentences.

What it does not do: change a word of what the record says, add a connective the record does not support, or write about
anything the model has no record of. Every sentence keeps its source numbers, and every composed sentence is checked to
carry the content words of its sources and nothing else (the output says how many passed). On the full release the
topic's own page is read in order; slim works from the model's answers only, so its essays are shorter.

Measured on 20 topics: 205 of 205 composed sentences faithful to their sources, a planted word change caught 20 of 20
times, and the fold closer to the target voice than random legal choices on all 20. Whether the essays read well has not
been measured: that needs blind human scoring, which has not been done.

## Commands

```
/help                         every feature and command
/scan                         read this computer
/connect user@host [port] [key]   read a server over SSH
/files                        add files
/mcp                          connect an MCP server
/sensors                      connect and watch sensors
/verify                       check this install against the published hashes
/history                      open or close the conversations panel
/new-chat                     start a new conversation
/remember [days]              keep this conversation as a temporary specialist
/new <id> [words]             a new specialist
/exam <id> dev|heldout        run an exam
/specialists <word>           find a specialist
/systems                      the five systems
/gaps on|off                  the gap journal
/code <what it does>          compose a function
/film                         film the answers
/share <id>                   package a specialist
/clear                        clear the conversation
```

## Files

```
workbench/server.py     the local server (standard library only)
workbench/exam.py       the exam and the source-reader check
workbench/sources.py    scan, server, files readers
workbench/mcp.py        MCP client and the adaptive tool specialist
workbench/sensors.py    sensor connections, polling, physical-range checks and the sensor reader
workbench/verify.py     release hashes, Merkle root and the Solana anchor check
workbench/template/     what "New specialist" copies
workbench/examples/     the worked example
workbench/data/         the specialist list, cards, the five systems, the core panel
workbench/static/       the page (three.js r128 and the fonts are bundled; SIL Open Font Licence)
workbench/local/        YOURS: specialists, conversations, sensor readings, journal, settings, outbox. Never shipped,
                        never uploaded, never hashed.
```
