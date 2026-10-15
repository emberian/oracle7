# Oracle7 Hydrology & Rivers (#24, tier B)

**id** `hydrology` - organ `organ_hydrology_v1.HydrologyOrgan` composed in front of the frozen head `oracle_release_runtime_w363`.

## Verdict

- decision: **ADMIT** (gate v2)
- held-out domain: specialist 52/52 (false yes 0) vs head 3/52 (false yes 0)
- core capability panel: head 160 -> composed 160 (0 items swept in by the full sweep)
- reasons: none

## Sources and licences

- Rational method (USDA NRCS / FHWA HEC-22), Manning's equation (USGS), continuity Q = vA (public domain (US government)) https://www.fhwa.dot.gov/engineering/hydraulics/library_arc.cfm?pub_number=22
- Rainwater harvesting yield: 0.623 US gal per inch per sq ft (Texas Water Development Board manual) (public (state government)) https://www.twdb.texas.gov/publications/brochures/conservation/doc/RainwaterHarvestingManual_3rdedition.pdf

## What it takes

- answers: rational, harvest, harvest_si, manning_q, manning_v, fill_time, continuity
- declines (in-domain): underspecified, impossible
- everything else falls through to the head unchanged

## Notes and known gaps

Formulas stated in every answer; runoff coefficient, Manning's n and collection efficiency are never assumed (harvest is 'before losses' unless an efficiency is given). Narrowed (narrow_v1) from the start: word problems to the head.
