# Oracle7 Soil Science (#25, tier B)

**id** `soil` - organ `organ_soil_v1.SoilOrgan` composed in front of the frozen head `oracle_release_runtime_w503`.

## Verdict

- decision: **ADMIT** (gate v2)
- held-out domain: specialist 36/36 (false yes 0) vs head 1/36 (false yes 2)
- core capability panel: head 160 -> composed 160 (0 items swept in by the full sweep)
- reasons: none

## Sources and licences

- USDA NRCS soil texture triangle and texture-class rules (Soil Survey Manual, USDA Handbook 18); bulk density, porosity (particle density 2.65 g/cm3) and water content - NRCS Soil Quality Indicators (public domain (US government)) https://www.nrcs.usda.gov/resources/education-and-teaching-materials/soil-texture-calculator

## What it takes

- answers: texture, bulk_density, porosity, gwc, vwc
- declines (in-domain): underspecified, impossible
- everything else falls through to the head unchanged

## Notes and known gaps

USDA texture class by the NRCS triangle rules; particle density 2.65 g/cm3 (typical mineral soil) unless given, said so in each answer. Panel texture expectations were read off the triangle by hand for interior points, not computed by the organ's rules. Only answers when the turn is about soil (soil/texture/bulk density/porosity/water content vocabulary). Narrowed from the start (narrow_v1).
