# Oracle7 Agriculture & Crop Science v2 (#99, tier B)

**id** `agriculture-v2` - organ `organ_agriculture_v2.AgricultureOrganV2` composed in front of the frozen head `oracle_release_runtime_w503`.

## Verdict

- decision: **ADMIT** (gate v2)
- held-out domain: specialist 17/17 (false yes 0) vs head 1/17 (false yes 1)
- core capability panel: head 160 -> composed 160 (0 items swept in by the full sweep)
- reasons: none

## Sources and licences

- USDA / land-grant extension: fertilizer grade arithmetic, seeding rate from spacing, standard bushel test weights (USDA AMS), acre-inch (public domain (US government)) https://www.ams.usda.gov/

## What it takes

- answers: fert_product, nutrient_lb, seeds_per_acre, seeds_needed, yield_kgha, yield_tha, acre_inch
- declines (in-domain): impossible, underspecified
- everything else falls through to the head unchanged

Supersedes: agriculture (v1 NEGATIVE under gate v3: 2 wrong from head fallthrough)

## Notes and known gaps

v2 = v1 + hyphenated bag sizes ('40-pound bag'), 'lb/acre of N', and RECOGNISE-THEN-DECLINE for fertilizer-grade questions it cannot read. v1 NEGATIVE under gate v3: held-out 14/17 vs 1/17 but 2 WRONG - the head's 0 and -15 on '40-pound bag of 20-10-10' turns the organ fell silent on. Fresh panel v2 (seeds 999999/99999999). Same author - disclosed.
