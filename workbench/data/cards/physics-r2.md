# Oracle7 Physics (Mechanics) (r2, narrowed) (#39, tier A)

**id** `physics-r2` - organ `organ_mechanics_v2.MechanicsOrganV2` composed in front of the frozen head `oracle_release_runtime_w363`.

## Verdict

- decision: **ADMIT** (gate v2)
- held-out domain: specialist 123/123 (false yes 0) vs head 2/123 (false yes 1)
- core capability panel: head 160 -> composed 160 (0 items swept in by the full sweep)
- reasons: none

## Sources and licences

- Classical mechanics (constant-acceleration kinematics, Newton's second law, work-energy, momentum) with standard gravity 9.80665 m/s^2 (CGPM 1901) (public domain (physical law; value from NIST)) https://physics.nist.gov/cuu/Constants/
- OpenStax University Physics (already in the core's world stores) (CC-BY 4.0) https://openstax.org/details/books/university-physics-volume-1

## What it takes

- answers: range, impact_speed, fall_time, ke, pe, momentum, weight, force, work, power, final_velocity, distance
- declines (in-domain): underspecified
- everything else falls through to the head unchanged

Supersedes: physics (v1 admitted 2026-09-29 under spec_gate_v1)

## Notes and known gaps

Computation with the formula shown; no air resistance stated. Panel answers from formulas written separately; dev/held-out differ in seed and phrasing (same author). || r2 (2026-09-29): the full-core sweep found this organ taking core items outside its domain (reading passages, word problems, idioms). r2 = runtime v2 (reading turns -> head) + a NARROWING-ONLY organ patch (narrow_v1). INVARIANCE: r2's reply is byte-identical to v1's on 123/123 (counts only, no items or scores viewed), so the SAME held-out panel is re-run under spec_gate_v2 - its domain result is v1's by construction; what is newly measured is the full-core sweep with the per-item no-worse rule.
