# Oracle7 Building Environment & HVAC (#2, tier B)

**id** `hvac` - organ `organ_hvac_v1.HvacOrgan` composed in front of the frozen head `oracle_release_runtime_w363`.

## Verdict

- decision: **ADMIT** (gate v2)
- held-out domain: specialist 42/42 (false yes 0) vs head 3/42 (false yes 0)
- core capability panel: head 160 -> composed 160 (0 items swept in by the full sweep)
- reasons: none

## Sources and licences

- Standard-air sensible heat factor 1.08, ton = 12,000 BTU/h, conduction Q = A dT / R, degree-day energy - DOE Building Technologies / Energy Saver (public domain (US government)) https://www.energy.gov/eere/buildings/building-technologies-office

## What it takes

- answers: tons, btuh, ach, cfm_needed, sensible, seasonal, conduction
- declines (in-domain): underspecified, sizing
- everything else falls through to the head unchanged

## Notes and known gaps

Formulas stated; never sizes equipment for a real building (declined: needs a Manual J load calculation). Scorer reads exact a/b values too (scorer template rule). Narrowed from the start (narrow_v1).
