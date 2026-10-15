# Oracle7 Workshop & 3D Printing v2 (#8, tier B)

**id** `printing-v2` - organ `organ_printing_v2.PrintingOrganV2` composed in front of the frozen head `oracle_release_runtime_w503`.

## Verdict

- decision: **ADMIT** (gate v2)
- held-out domain: specialist 36/37 (false yes 1) vs head 2/37 (false yes 1)
- core capability panel: head 160 -> composed 160 (0 items swept in by the full sweep)
- reasons: none

## Sources and licences

- Cylinder volume and mass (geometry), typical polymer densities (PLA 1.24, PETG 1.27, ABS 1.04, ASA 1.07, TPU 1.21, nylon 1.14 g/cm^3) as published on manufacturer technical data sheets - stated as typical in every answer (facts) https://reprap.org/wiki/Filament

## What it takes

- answers: shrink_scale, layers, flow, cost, length, mass
- declines (in-domain): underspecified, impossible
- everything else falls through to the head unchanged

Supersedes: printing (ADMIT gate v2, held-out 30/36; 6 misses safe)

## Notes and known gaps

v2 = v1 + 'printed' as a print cue and 'mm high' read as 'mm tall' - v1's held-out misses ('A part 180 mm high is printed with 0.2 mm layers', not taken) - and the family numbers rule. Judged under spec_gate_v3.1 on a FRESH panel v2 (seeds 808080/80808080). Same author - disclosed.
