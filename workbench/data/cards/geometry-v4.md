# Oracle7 Geometry v4 (#46, tier A)

**id** `geometry-v4` - organ `organ_geometry_v4.GeometryOrganV4` composed in front of the frozen head `oracle_release_runtime_w363`.

## Verdict

- decision: **ADMIT** (gate v2)
- held-out domain: specialist 93/93 (false yes 0) vs head 4/93 (false yes 0)
- core capability panel: head 160 -> composed 163 (3 items swept in by the full sweep)
- reasons: none

## Sources and licences

- Euclidean measurement formulas (area, perimeter, volume, surface area, Pythagoras, Heron, polygon angle sum) (public domain (mathematics)) https://en.wikipedia.org/wiki/Area#Area_formulas

## What it takes

- answers: circle_area, circumference, sphere_volume, sphere_surface, cylinder_volume, cylinder_surface, cone_volume, cube_volume, cube_surface, box_volume, rect_area, rect_perimeter, square_area, square_perimeter, tri_area, heron, hypotenuse, leg, angle_sum
- declines (in-domain): underspecified, impossible
- everything else falls through to the head unchanged

Supersedes: geometry-v3 (ADMIT gate v2, 93/100; 7 misses = imperative 'Compute the hypotenuse')

## Notes and known gaps

v4 = v3 + imperative verbs (compute / calculate / determine / give / work out) read as 'find' for the hypotenuse. Judged under spec_gate_v2 on a FRESH panel (new seeds, new phrasings both splits including the class). Same author - disclosed. Earlier notes: v3 = v1 + narrowing (v2: word problems to the head; no false 'I need X' when numbers are present - the full-core sweep found v1 taking 17 core word problems incl. a confident wrong 10.95 for 5) + two reading classes v1 missed (sides stated with a verb, 'sides are a, b and c' - all 8 v1 held-out misses; a hypotenuse value stated after the verb). Judged under spec_gate_v2 on a FRESH panel v2 (new seeds, new phrasings both splits, new declines). Same author - disclosed. Deliberately does NOT read '10 feet across' as a diameter: those core textbook problems use pi = 3.14.
