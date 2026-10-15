# Oracle7 Electronics & Circuits (r2: re-gated under gate v2) (#41, tier A)

**id** `electronics-r2` - organ `organ_circuits_v1.CircuitsOrgan` composed in front of the frozen head `oracle_release_runtime_w363`.

## Verdict

- decision: **ADMIT** (gate v2)
- held-out domain: specialist 111/111 (false yes 0) vs head 3/111 (false yes 0)
- core capability panel: head 160 -> composed 160 (0 items swept in by the full sweep)
- reasons: none

## Sources and licences

- Circuit laws (Ohm's law, Joule heating, Kirchhoff series/parallel, RC time constant), as in US Navy NEETS modules 1-2 (public domain (US government work)) https://www.navy.mil/

## What it takes

- answers: current, voltage, resistance, power, series, parallel, divider, rc, led
- declines (in-domain): impossible, underspecified
- everything else falls through to the head unchanged

Supersedes: electronics (v1, ADMIT under spec_gate_v1)

## Notes and known gaps

The knowledge is exact physics; the store is the organ itself. Panel answers computed with formulas written separately in circuits_panel_v1.py; dev and held-out use different seeds and phrasings (same author). || r2 (2026-09-29): the organ is BYTE-IDENTICAL to the admitted v1; re-gated under spec_gate_v2 (full core sweep, per-item no-worse, runtime v2) so the whole family stands under the same gate. The full sweep takes 0 core items. The SAME held-out panel is re-run - identical organ, so its domain result is v1's by construction.
