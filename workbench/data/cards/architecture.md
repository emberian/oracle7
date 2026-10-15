# Oracle7 Architecture (zoning and code arithmetic) (#88, tier B)

**id** `architecture` - organ `organ_architecture_v1.ArchitectureOrgan` composed in front of the frozen head `oracle_release_runtime_w503`.

## Verdict

- decision: **ADMIT** (gate v2)
- held-out domain: specialist 10/10 (false yes 0) vs head 1/10 (false yes 0)
- core capability panel: head 160 -> composed 160 (0 items swept in by the full sweep)
- reasons: none

## Sources and licences

- International Building Code 2021 - occupant load factors (Table 1004.5) and egress width (1005.3); zoning FAR and lot coverage definitions (facts (code values)) https://codes.iccsafe.org/content/IBC2021P2
- 2010 ADA Standards for Accessible Design 405.2 (ramp running slope 1:12) (public domain (US government)) https://www.ada.gov/law-and-regs/design-standards/2010-stds/

## What it takes

- answers: far, max_floor, coverage, occupant_load, egress_width, ramp_run
- declines (in-domain): none
- everything else falls through to the head unchanged

## Notes and known gaps

Model-code values (IBC 2021, ADA 2010) named in every answer; local codes and amendments govern real projects. Aesthetic questions are not taken. Narrowed from the start (narrow_v1).
