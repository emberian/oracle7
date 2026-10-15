# Oracle7 Earth Science & Geology (#19, tier A)

**id** `geology` - organ `organ_geology_v1.GeologyOrgan` composed in front of the frozen head `oracle_release_runtime_w503`.

## Verdict

- decision: **ADMIT** (gate v2)
- held-out domain: specialist 18/18 (false yes 0) vs head 2/18 (false yes 0)
- core capability panel: head 160 -> composed 160 (0 items swept in by the full sweep)
- reasons: none

## Sources and licences

- USGS - radiometric dating, half-lives, plate tectonics rates, geothermal gradient (public domain (US government)) https://pubs.usgs.gov/gip/geotime/radiometric.html
- NNDC / NIST half-life values (C-14 5,730 y; K-40 1.248 Gy; U-238 4.468 Gy; U-235 704 My) (public domain (US government)) https://www.nndc.bnl.gov/

## What it takes

- answers: fraction_left, age_fraction, age_ratio, plate_distance, plate_rate, depth_temp
- declines (in-domain): underspecified, impossible
- everything else falls through to the head unchanged

## Notes and known gaps

Ideal decay, no initial daughter (said so via the formula); C-14 uses the 5,730-year (Cambridge) half-life, not the 5,568-year Libby value of conventional radiocarbon ages. Panel two-role items in both orders in DEV (panel rule). Narrowed from the start (narrow_v1).
