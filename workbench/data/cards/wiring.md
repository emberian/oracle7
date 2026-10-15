# Oracle7 Electrical Systems & Wiring (#12, tier B)

**id** `wiring` - organ `organ_wiring_v1.WiringOrgan` composed in front of the frozen head `oracle_release_runtime_w363`.

## Verdict

- decision: **ADMIT** (gate v2)
- held-out domain: specialist 45/45 (false yes 0) vs head 3/45 (false yes 0)
- core capability panel: head 160 -> composed 160 (0 items swept in by the full sweep)
- reasons: none

## Sources and licences

- AWG definition (ASTM B258): d = 0.127 mm x 92^((36-n)/39); IACS annealed copper resistivity 1/58 uohm m (facts / standards definitions) https://www.nist.gov/
- NEC 210.19(A)(1) / 210.20(A) continuous-load 80% rule, as summarised in OSHA and US Navy NEETS training material (public domain (US government summaries)) https://www.osha.gov/electrical

## What it takes

- answers: continuous, vdrop, resistance, area, diameter, current3, current
- declines (in-domain): underspecified, judgement
- everything else falls through to the head unchanged

## Notes and known gaps

Arithmetic only; never says an installation is safe or to code (declined: licensed electrician + local code). Resistances at 20 C. Three-phase power factor taken as 1 only when not given, and said so. Check: 12 AWG = 2.053 mm.
