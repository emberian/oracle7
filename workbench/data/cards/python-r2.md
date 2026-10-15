# Oracle7 Python Reference (r2: re-gated under gate v2) (#51, tier A)

**id** `python-r2` - organ `organ_pyref_v1.PyRefOrgan` composed in front of the frozen head `oracle_release_runtime_w363`.

## Verdict

- decision: **ADMIT** (gate v2)
- held-out domain: specialist 186/224 (false yes 0) vs head 0/224 (false yes 5)
- core capability panel: head 160 -> composed 160 (0 items swept in by the full sweep)
- reasons: none

## Sources and licences

- Python 3.12.3 standard library, read by introspection (signatures, modules, docstrings; 856 entries) (PSF License) https://docs.python.org/3.12/

## What it takes

- answers: signature, module, doc
- declines (in-domain): unknown, clarify, no_signature
- everything else falls through to the head unchanged

Supersedes: python (v1, ADMIT under spec_gate_v1)

## Notes and known gaps

The core's code organ WRITES programs (MBPP-graded); this specialist answers reference questions exactly, from the interpreter's own introspection, version-stamped. Answer keys read from the same introspection data (the source of truth). Held-out phrasings written by the same author, not used to tune the organ. || r2 (2026-09-29): the organ is BYTE-IDENTICAL to the admitted v1; re-gated under spec_gate_v2 (full core sweep, per-item no-worse, runtime v2) so the whole family stands under the same gate. The full sweep takes 0 core items. The SAME held-out panel is re-run - identical organ, so its domain result is v1's by construction.
