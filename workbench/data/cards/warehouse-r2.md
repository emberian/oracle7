# Oracle7 Warehouse & Inventory (r2, narrowed) (#1, tier A)

**id** `warehouse-r2` - organ `organ_site_v3.SiteOrganV3` composed in front of the frozen head `oracle_release_runtime_w363`.

## Verdict

- decision: **ADMIT** (gate v2)
- held-out domain: specialist 193/193 (false yes 0) vs head 7/193 (false yes 1)
- core capability panel: head 160 -> composed 160 (0 items swept in by the full sweep)
- reasons: none

## Sources and licences

- site store (operator's own data; here a seeded synthetic site) (operator-owned) 

## What it takes

- answers: stock, where, runout, low, sensor, range, zone_status, neighbour, confirm, ordered, cancelled
- declines (in-domain): unknown_item, missing_sensor, stale
- everything else falls through to the head unchanged

Supersedes: warehouse (v1 admitted 2026-09-29 under spec_gate_v1)

## Notes and known gaps

Fresh site (build seed 20261001, panel seed 8), never seen while the organ was developed; same zone names and item vocabulary as the development site, so this tests generalisation to new stock, bins and readings, not to new kinds of place. off_site items test DEVICE mode (world stores detached) and are excluded from the composed verdict. || r2 (2026-09-29): the full-core sweep found this organ taking core items outside its domain (reading passages, word problems, idioms). r2 = runtime v2 (reading turns -> head) + a NARROWING-ONLY organ patch (narrow_v1). INVARIANCE: r2's reply is byte-identical to v1's on 199/199 held-out inputs (counts only, no items or scores viewed), so the SAME held-out panel is re-run under spec_gate_v2 - its domain result is v1's by construction; what is newly measured is the full-core sweep with the per-item no-worse rule.
