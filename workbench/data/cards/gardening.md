# Oracle7 Gardening (#63, tier B)

**id** `gardening` - organ `organ_gardening_v1.GardeningOrgan` composed in front of the frozen head `oracle_release_runtime_w503`.

## Verdict

- decision: **ADMIT** (gate v2)
- held-out domain: specialist 14/15 (false yes 1) vs head 1/15 (false yes 1)
- core capability panel: head 160 -> composed 160 (0 items swept in by the full sweep)
- reasons: none

## Sources and licences

- USDA / land-grant extension home-garden guides (raised beds, mulch depth, fertilizer per 1,000 sq ft, 1 inch of water = 0.623 gal/sq ft) (public domain (US government)) https://www.usda.gov/

## What it takes

- answers: cubic_feet, cubic_yards, bags, plants_grid, fert_area, water_gal
- declines (in-domain): none
- everything else falls through to the head unchanged

## Notes and known gaps

Volumes with no settling allowance; plants on a square grid (floor per side), said so. Advice questions (when to plant, why leaves yellow) fall through. Narrowed from the start (narrow_v1).
