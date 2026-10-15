# Oracle7 Greenhouse & Controlled Agriculture (#4, tier B)

**id** `greenhouse` - organ `organ_greenhouse_v1.GreenhouseOrgan` composed in front of the frozen head `oracle_release_runtime_w363`.

## Verdict

- decision: **ADMIT** (gate v2)
- held-out domain: specialist 45/45 (false yes 0) vs head 3/45 (false yes 0)
- core capability panel: head 160 -> composed 160 (0 items swept in by the full sweep)
- reasons: none

## Sources and licences

- FAO Irrigation and Drainage Paper 56 (Tetens saturation vapour pressure, eq. 11) (FAO (free to reproduce with attribution)) https://www.fao.org/3/x0490e/x0490e00.htm
- Daily light integral and growing degree days as defined by USDA / land-grant extension services (public domain (US government)) https://www.usda.gov/

## What it takes

- answers: vpd, vpd_leaf, dli, ppfd_needed, gdd, plant_count
- declines (in-domain): underspecified, impossible
- everything else falls through to the head unchanged

## Notes and known gaps

Formulas stated in every answer. The GDD base temperature is never assumed (it depends on the crop). Leaf vs air temperature read from grammar, never order of mention (the panel states the leaf first in half the leaf-VPD items). Narrowed from the start (narrow_v1).
