# Oracle7 Materials Science & Aerogels (#40, tier B)

**id** `materials-v2` - organ `organ_materials_v2.MaterialsOrganV2` composed in front of the frozen head `oracle_release_runtime_w503`.

## Verdict

- decision: **ADMIT** (gate v2)
- held-out domain: specialist 24/24 (false yes 0) vs head 3/24 (false yes 0)
- core capability panel: head 160 -> composed 160 (0 items swept in by the full sweep)
- reasons: none

## Sources and licences

- NASA aerogel technical reports (bulk vs skeletal density, porosity); NIST materials data (public domain (US government)) https://www.nasa.gov/general/aerogels-insulating-materials/
- OpenStax University Physics / Chemistry: stress, strain, Young's modulus, thermal expansion, cubic unit cells (n M / N_A a^3), packing factors (CC-BY 4.0) https://openstax.org/details/books/chemistry-2e

## What it takes

- answers: apf, crystal_density, porosity, stress, strain, modulus, expansion
- declines (in-domain): impossible, underspecified
- everything else falls through to the head unchanged

## Notes and known gaps

v2 of materials (v1 NEGATIVE 2026-09-29: 3 head-fallthrough wrongs on 'BCC, a = X pm' + 1 false yes from a dropped decline). Reads 'a = X pm', 'an N mm specimen', 'heated N °C'; keeps recognised declines on numeric turns; recognise-then-decline. Fresh panel v2.
