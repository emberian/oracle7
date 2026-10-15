# Oracle7 Carbon Materials (Nanotubes & Graphene) (#92, tier B)

**id** `carbonmat` - organ `organ_carbonmat_v1.CarbonMatOrgan` composed in front of the frozen head `oracle_release_runtime_w503`.

## Verdict

- decision: **ADMIT** (gate v2)
- held-out domain: specialist 17/17 (false yes 0) vs head 1/17 (false yes 0)
- core capability panel: head 160 -> composed 160 (0 items swept in by the full sweep)
- reasons: none

## Sources and licences

- Graphene lattice constant 0.246 nm, graphite interlayer 0.335 nm, CNT chirality rules (diameter, chiral angle, metallic when n - m divisible by 3) - NIST nanomaterials / standard solid-state texts (facts) https://www.nist.gov/topics/nanotechnology

## What it takes

- answers: cnt_diameter, cnt_angle, cnt_type, cnt_kind, graphene_layers, graphene_mass
- declines (in-domain): impossible
- everything else falls through to the head unchanged

## Notes and known gaps

Ideal (unrelaxed) geometry from the graphene lattice; the metallic rule is the zone-folding rule (small-diameter curvature gaps not modelled - a property of the rule). Aerogel porosity lives in #40 materials. Narrowed from the start (narrow_v1).
