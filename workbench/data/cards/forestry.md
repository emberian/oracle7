# Oracle7 Forestry (#37, tier B)

**id** `forestry` - organ `organ_forestry_v1.ForestryOrgan` composed in front of the frozen head `oracle_release_runtime_w503`.

## Verdict

- decision: **ADMIT** (gate v2)
- held-out domain: specialist 14/16 (false yes 0) vs head 1/16 (false yes 0)
- core capability panel: head 160 -> composed 160 (0 items swept in by the full sweep)
- reasons: none

## Sources and licences

- USDA Forest Service - forest mensuration: basal area factor 0.005454, trees per acre, clinometer heights, Smalian's formula, Doyle log rule (public domain (US government)) https://www.fs.usda.gov/

## What it takes

- answers: basal_area, ba_per_acre, basal_area_m2, tpa, height, smalian, doyle
- declines (in-domain): impossible
- everything else falls through to the head unchanged

## Notes and known gaps

Rules named in every answer (Doyle underestimates small logs - a property of the rule, not corrected). Clinometer height is above eye level unless an eye height is given. Panel two-role items in both orders (end diameters). Narrowed from the start (narrow_v1).
