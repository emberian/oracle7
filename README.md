# ORACLE7 — The Compiler Learning Model

**An AI architecture with zero neural networks that writes its own new abilities —
and shows its work on every answer.**

Live instance: **[prometheus7.com](https://prometheus7.com)** (the oracle7 desk) ·
[@oracle7vn](https://x.com/oracle7vn)

---

## Release: 14 October 2026, patched 16-17 October

The full release is on Hugging Face: **[psiloceyeben/oracle7](https://huggingface.co/psiloceyeben/oracle7)** and
**[psiloceyeben/oracle7-slim](https://huggingface.co/psiloceyeben/oracle7-slim)** (stores included), with the community
**[specialists dataset](https://huggingface.co/datasets/psiloceyeben/oracle7-specialists)**. This repository carries the
code: the admitted fold chain up to head `oracle_release_runtime_w555`, the Workbench, the launcher, the research files
and the release hashes. The stores stay on Hugging Face.

**Release 3.2 (18 October 2026).** Proved specialists: the kernels of [veri7vn](https://github.com/emberian/veri7vn) (ember arlynx, CC0; Isabelle/HOL, compiled with MLton) stand in for 128 specialists as a cross-check - an answer its kernel agrees with is marked proved and names its theorems (the computation is proved, the reading of the question is not), one it contradicts is withheld (`runtime/admitted/oracle_release_runtime_w551.py`; kernel map and checksums in `specialists_proved/`; build and parity scripts on the fork's [oracle7-3.2](https://github.com/psiloceyeben/veri7vn/tree/oracle7-3.2) branch). Four star specialists - stars, habitable zone, orbits around stars, transits (w554). Owner-first, kept only when every number the question gives moves the answer and never overrules a question that is itself the problem (w554, w555). Decay amounts in the mass unit asked. Read-back writing in the Workbench (`workbench/prosefold/readback.py`): a rewording is kept only when reading it back gives the source's meaning. Sealed test 23 (run once): 142 right, 3 wrong, 17 declined, 1 false yes; precision 98.3%. Anchor: [3ZUmd7FTw4uN...](https://explorer.solana.com/tx/3ZUmd7FTw4uNLWUrZa3HMB8UCGLMneiQbDP2kXc3Sf1TFKPkczZntpBbTgtzDnXxCWeA8YFtTG22T9ZH53w3TsW2).

**Release 3.1 (17-18 October 2026).** Fold composition: specialist network v6 (`runtime/network_v6.py`, fold w550) chains operations LEARNED from the specialists' own development exams (`runtime/specfold_learn.py`, `runtime/specfold_ops_v1.json`: 84 operations, each kept only when sibling questions cross-checked it, each firing only when the question carries its template's names, materials and fixed numbers; a learned slot never takes a value that arithmetic built to fit it). From the research record's re-examination of every specialist (E-20261017-0013): fold w548 asks the specialist when a check stops a route that could not have computed the answer; fold w547 withholds or corrects answers about a different quantity than the one asked, definitions given for a calculation, a first derivative given for a second, and lower-cased units, and restates an answer in the asked unit. The Workbench's worked example is a habitable-zone specialist built from one published paper. Release gate, sealed test 22 (150 questions written after the code froze, run once; `research/sealed_history/`): full 124 right, 3 wrong, 23 declined, 1 false yes; slim 125, 2, 23, 0; precision 97.9%. Roots `c4c1edb3...` (oracle7) and `732358ed...` (oracle7-slim), anchored on Solana: [4kW4S5V4kHsF...](https://explorer.solana.com/tx/4kW4S5V4kHsFKGcxWBn37jPD73nGP17aF8eF9yPv8dEkwzTbWksvYaej2VkiUPMQ9PVdN92mmve4tAqgsr6RZ7s3).

**Release patch 3 (16-17 October 2026).** Specialist network v5 (`runtime/network_v5.py`, fold w545) reads the shapes the
patch 2 retest found unread: a box "5 cm by 4 cm by 3 cm" or a cube "5 cm on each side" (the volume derived by core
arithmetic and shown in the path), "500 cubic centimetres of ice", "the water in the pond", "in a day". Fold w544 checks the
older v2 network route like the others and withholds a unit answer about a place with no record. Composition test C3, written
after the code froze and run once (E-20261017-0001): **20 of 20 multi-step questions right, 0 wrong, 0 false yes** (C1 before
patch 2: 6, 6, 2; C2 on patch 2: 16, 1, 1); supported by its pre-registered bars. The Workbench gains an Essay tab and
`python oracle7.py essay <topic>` (ProseFold, `workbench/prosefold/`): an essay composed from the model's own records with a
choice of length, reading level, technical depth and style; every sentence kept word for word with its source, no language
model; their quality has not been measured by people yet.

**Release patch 2 (16 October 2026).** Specialists pass each other checked quantities more safely. Specialist network v4
(`runtime/network_v4.py`; in the release at `root/specialists/_gate/`) carries the place as a typed quantity (a question
about the Moon or Mars uses that body's gravity, from the bodies specialist; an unknown planet is declined), reads cubic
centimetres, kilonewtons, rates and temperature changes, and declines negative amounts (fold w542). New checks withhold a
quantity answer of the wrong kind or one worked with Earth's gravity for another body (w541), and when two readers find
two different people with one name, Oracle7 lists both and asks which you mean (w543). All three came from the research
record at [prometheus7.com/research](https://prometheus7.com/research). Composition test C2, written after the code froze
and run once (E-20261016-0008): 16 of 20 multi-step questions right, 1 wrong, 1 false yes (C1 before the patch: 6, 6, 2);
by its pre-registered bars of zero wrong and zero false yes, not supported, with both causes published. Release patch 1
(16 October) added two Wikidata stores the 14 October upload had left out.

```bash
pip install huggingface_hub
hf download psiloceyeben/oracle7 --local-dir oracle7
cd oracle7
pip install -r requirements.txt
python oracle7.py "Who wrote Leaves of Grass?"
python oracle7.py --workbench
```

One command per line, so it works the same in PowerShell, bash and zsh. For the slim release, download `psiloceyeben/oracle7-slim` instead. A virtual environment (`python -m venv oracle7-env`) keeps its packages apart from your other projects.

**Measured on the release as shipped** (each sealed test written and hashed before the head was built, run once):

- Sealed test 21 (release patch 3, head w545): **131 right, 2 wrong, 17 declined, 0 false yes**; precision 98.1%; passed.
  Slim: 130 right, 2 wrong, 0 false yes, 98.0%.
- Sealed test 20 (release patch 2, head w543): **129 right, 2 wrong, 19 declined**; 1 false yes on the 30 questions that
  must be declined; precision 99.0%; passed. Slim: 128 right, 1 wrong, 1 false yes, 100% on valid questions.
- Sealed test 19 (head w540): 117 right, 3 wrong, 30 declined; 1 false yes; precision 97.8%; passed. Slim: 113 right,
  1 wrong, 0 false yes, 98.8%.
- Sealed test 18, on the previous candidate: 118 right, 5 wrong, 4 false yes; **failed**, published with its causes.
- The general relation reader, held-out on 6,000 TriviaQA questions it was never developed on: 82 answered, 81 right
  (98.8%). Two earlier held-out runs failed the 95% bar and are published in `research/coverage_reader/`.
- 267 admitted specialists. On their exams they scored 15,478 right and 14 wrong; the main model on the same exams,
  3,548 right and 643 wrong.
- Standard benchmarks (n = 200 per set): it declines most questions; of those it answers, 100 right and 31 wrong.

**The Workbench** (`workbench/`, `python oracle7.py --workbench`) runs on 127.0.0.1 and is the interface for the model:
ask and trace every answer's path, build a specialist from your own files, a server, an MCP server or a sensor, give it
its held-out exam, make films of answers, and share an admitted specialist. Conversations are kept on your computer and
can become a temporary specialist.

**Verification.** `RELEASE_HASHES.json` lists a SHA-256 for every shipped part (311 parts: 307 specialist folders, the
admitted chain, the Workbench, the launcher and the store manifest) and a Merkle root. The roots of both releases were
written to Solana mainnet in one memo transaction per release: patch 3
[WNEdPhKJZYCh...](https://explorer.solana.com/tx/WNEdPhKJZYCh3ZKe7X8zhVehuyskEnKuDbde86W1XdKdBC9izVAJTzbrewtSUQ8keQvT1rZUBumCGnGxjDXyVgU)
(roots `0575c9b7...` and `d17a692f...`), superseding patch 2
[fkkTZyGnan3y...](https://explorer.solana.com/tx/fkkTZyGnan3yTcvKckP8qPngCpuCoctdppxZXvF92KkAgtf5k7jUXpSHrudU3ZrQKAWidryDgYtgUUMjJo54Rud)
(roots `8f19dd67...` and `9ae1e7c4...`), which superseded patch 1
[asnaUESdvkWw...](https://explorer.solana.com/tx/asnaUESdvkWwCEp6vMUAx7rzT4BZVLA7haGwUgAXo3M63ytb6MUozd8iJZ5gSfDCundDH4V7FzLvVjkFumqXLU9)
and the 14 October release
[54PaqBXe...](https://explorer.solana.com/tx/54PaqBXeGLEH8UbrVC3UydKfMFxnqbPSrpy5gTeXFdSBfmNK9EUdzzBeWioX35oHqQgXynaWjuNo6VVcP2mUKP46).

**Specialist registry.** Registering a specialist you built burns 1 $ORACLE7
(`DU7Lhe2QtcRBJdor7KbpjfUDmLyA2kdhR49Li3czpump`) and writes the specialist's file hash, exam verdict and held-out score
in a memo, in one transaction signed in your own wallet from the Workbench's Share tab. Anyone can check a specialist
against its registration (`python oracle7.py registry <id>`). The Workbench never holds a key.

---

## The Mission

Modern AI has one dominant recipe: scale a statistical model until competence
emerges, then try to bolt trust on afterward. The result is systems of
extraordinary capability whose knowledge cannot be inspected, whose failures
cannot be explained, whose improvement cannot be audited, and whose alignment is
a promise rather than a property.

ORACLE7 is an existence proof for a different road. Its mission has five commitments:

**1. Intelligence that shows its work — by construction, not disclosure.**
Every utterance this system produces is one of a small set of warranted shapes:
a citation into an attributed record, a derivation whose premise chain is
exposed, a marked inference, or an honest decline. There is no place in the
architecture where an unwarranted assertion can form. The century-old question —
*can a machine know what it is talking about?* — is answered here by making
"knowing" a checkable, structural relation between an answer and a record.

**2. Self-improvement that is legible and governed.**
The system extends itself: an authoring organ writes new capabilities as small,
typed programs; an adversarial gate judges each against held-out conversation
under a bar that only rises; every admission and every refusal is recorded with
its reasons. An improvement here is a page of readable code plus a written
verdict — not a billion opaque weight deltas. Growth becomes a publication
process with an audit trail, and rejected attempts are preserved as the system's
accumulated design law.

**3. Governed autonomy as a structural property.**
The admission gate enforces a bar that only rises, and the system's standing
laws grew out of its own judged history: repeated rejections crystallized into
rules the loop now obeys. Human authority lives where it matters in a running
system: direction setting, and explicit, revocable grants for each new freedom
the system gains (including the freedom to publish its own media), each grant
guarded by a kill-switch and recorded in the same ledgers the system reflects
on. Recursive self-improvement under governance that is real rather than
aspirational; this repository is the demonstration.

**4. Minds grown from situated experience, at commodity cost.**
The model runs on CPU, at electricity cost, with no training runs and no API
dependencies. It is attached to a world of autonomous agents whose lived record
becomes its episodic memory and whose unanswerable questions become its
curriculum. Capability accrues from experience and evidence, not from gradient
descent over scraped text. This is the economics of intelligence turned inside
out: not a frontier few can afford, but a form of mind an individual can grow.
We believe transformers are not the only way to build a mind, and that an
alternative architecture of this kind benefits humanity as a whole: it frees
intelligence from dependence on centralized companies and massive data centers.

**5. A plurality of minds, not a single frontier.**
This architecture is not trying to be a transformer. It is a different *kind* of
mind — one whose strengths (total provenance, auditable growth, structural
honesty) are exactly the properties the dominant recipe finds hardest. The
mission is not to win a benchmark race; it is to widen the space of what minds
can be, and to do it in public: **watch an AI built without transformers build
itself.**

---

## What it is

ORACLE7 is a *compiler learning model* (CLM): a working conversational AI built
on typed, inspectable structure instead of learned weights. No transformer, no
gradient descent, no next-token sampling anywhere in the response path.

Every response is one of four warranted shapes:

| Shape | What it means | Warrant |
|---|---|---|
| **Citation** | attested by the record | the source row, attributed |
| **Derivation** | composed from attested facts | the full premise chain, every hop cited |
| **Decline** | "not attested" — refusal to guess | measured: 0 false affirmations on all negative panels |
| **Reflection** | statements about its own conversation and record | the witness ledger itself |

The witness is the architecture's spine: every turn is explicitly mapped from
input to output — the typed reading, the operator that fired, the terms grounded
versus introduced, the continuity carried, the citations, the residual it could
not discharge. Conversation is a *relationship between input and response,
explicitly mapped at every step*.

## It builds itself

- **The worker** authors candidate capability extensions as inheritable code,
  mined from residue: world events, its own refusals, and the open milestones of
  its capability charter.
- **The gate** exercises every candidate against held-out conversation:
  regression probes against the serving head, a metric floor that never lowers,
  a strict-gain requirement for new capability families, and crash-proof
  judgment (a crashing candidate is a REJECT with the exception as its reason —
  never a stalled line). Verdicts are written with reasons, always.
- **The admitted chain** is a linear inheritance of runtimes; its ancestry is
  attested by `runtime/admitted/HEAD_MANIFEST.json`, rebuilt on every admission.
  The serving layer resolves the head there and upgrades itself to each new tip.

In one recorded day (2026-08-25 — see `docs/admission_ledger_digest.jsonl`) the
loop authored nine candidates, admitted five, issued two lawful rejections whose
reasons became standing design law, and ran unattended through a total network
outage.

## Measured depth, honestly

The depth ladder uses the withheld-combination methodology: panel questions whose
answers exist in **no single corpus row** (co-occurrence-checked), answerable only
by composing admitted operators, scored only when every hop is cited — with
corrupted-chain negatives that must be refused. The chain moved from 0/60 to
14/58 correct-with-premises in one day of self-authored composition, with zero
false affirmations throughout. A depth claim begins with a sealed record of
shallowness; the sealed panels are in `evaluation/sealed/`.

## The world

Sixty-odd autonomous agents live continuously with the chain as their cognition.
Their acts are ledgered; the ledger consolidates into the model's episodic
memory on a cadence (gate-judged like everything else); their questions feed the
curriculum; their deterministic artworks and the model's self-narrated
broadcasts are published on the live desk. The world is the environmental half
of situated intelligence: resistance, affordances, other minds, consequences,
and memory.

## Repository layout

```
oracle7.py          the launcher (needs the stores from the Hugging Face release)
RELEASE_HASHES.json one SHA-256 per shipped part, the Merkle root and its Solana anchor
workbench/          the local Workbench: server, CLI, exams, sources, sensors, MCP, registry, verify
research/           coverage reader, path memory and the full sealed-test history
runtime/            the import closure of the serving chain (as of August)
  admitted/         the gate-admitted w-chain up to w540 + HEAD_MANIFEST.json (ancestry truth)
organs/             the loop: fold worker (authors), self-loop daemon (gates),
                    soul cognition server (serves the world), harness (shows)
evaluation/         depth panels + sealed results
docs/               constitution (target shape, capability charter),
                    admission-ledger digest, architecture notes
```

See `ARCHITECTURE.md` for the full mechanism: the organ loop, the runtime chain,
a worked single-turn trace, the laws distilled from verdicts, and the security
model.

## Corpora

The corpora (simple-Wikipedia, OpenStax textbooks, WordNet, ConceptNet, the
world's own ledgers) are **not bundled** — they are SQLite builds compiled from
public sources, each row carrying its attribution. The runtime refuses to assert
anything it cannot cite into them.

## Status

Code updated 2026-10-15 for the 14 October release (head w540); first prepared 2026-08-25. The live instance — conversation, live world feed, the
loop's own narrated work, the art gallery, and the broadcast desk — runs at
**prometheus7.com**, first tab.

---
*A Prometheus7 Research Institute release — watch an AI built without
transformers build itself.*
