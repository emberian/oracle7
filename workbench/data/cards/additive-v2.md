# Oracle7 Additive Manufacturing & Design (#96, tier B)

**id** `additive-v2` - organ `organ_additive_v2.AdditiveOrganV2` composed in front of the frozen head `oracle_release_runtime_w503`.

## Verdict

- decision: **ADMIT** (gate v2)
- held-out domain: specialist 20/20 (false yes 0) vs head 1/20 (false yes 0)
- core capability panel: head 160 -> composed 160 (0 items swept in by the full sweep)
- reasons: none

## Sources and licences

- OpenSCAD User Manual (cube / sphere / cylinder primitives and parameters) (CC-BY-SA 3.0 (store ships share-alike)) https://en.wikibooks.org/wiki/OpenSCAD_User_Manual
- NIST additive manufacturing (STL / closed mesh); Euler characteristic V - E + F = 2 - 2g (public domain (US government) / facts) https://www.nist.gov/additive-manufacturing

## What it takes

- answers: scad_volume, mesh_vertices, mesh_edges, mesh_faces, scale_amount, scale_factor, extrude_time
- declines (in-domain): impossible, underspecified
- everything else falls through to the head unchanged

## Notes and known gaps

v2 of additive (v1 NEGATIVE 2026-09-29: flow rate '15 mm3/s' read as the volume - confident wrong; 'Scale a 100 g part by 0.5 times' unread). Flow only as volume-per-time, volume never followed by '/'; scale factor from by/to N times; recognise-then-decline. Fresh panel v2.
