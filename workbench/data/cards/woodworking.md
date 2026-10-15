# Oracle7 Home Repair & Woodworking (#64, tier B)

**id** `woodworking` - organ `organ_woodworking_v1.WoodworkingOrgan` composed in front of the frozen head `oracle_release_runtime_w503`.

## Verdict

- decision: **ADMIT** (gate v2)
- held-out domain: specialist 33/36 (false yes 0) vs head 3/36 (false yes 0)
- core capability panel: head 160 -> composed 160 (0 items swept in by the full sweep)
- reasons: none

## Sources and licences

- USDA Forest Products Laboratory, Wood Handbook (FPL-GTR-282): moisture content, lumber sizes (public domain (US government)) https://www.fpl.fs.usda.gov/documnts/fplgtr/fplgtr282/fpl_gtr282.pdf
- American Softwood Lumber Standard PS 20 (dressed dry sizes); IRC R311.7.5.1 maximum riser 7 3/4 in; board foot, cubic yard, pitch geometry (facts) https://www.nist.gov/standardsgov/voluntary-product-standards-program

## What it takes

- answers: actual_size, board_feet, concrete, drywall, risers, riser_height, rafter, pitch_angle, miter, wood_mc
- declines (in-domain): impossible
- everything else falls through to the head unchanged

## Notes and known gaps

Conventions named in every answer: no waste allowance on concrete or drywall; IRC 7 3/4 in maximum riser (local codes may differ - said via the citation); rafter length without overhang or ridge deduction. Declines only structural impossibilities. Narrowed from the start (narrow_v1).
