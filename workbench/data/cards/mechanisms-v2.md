# Oracle7 Mechanical Engineering & Mechanisms v2 (#42, tier B)

**id** `mechanisms-v2` - organ `organ_mechanisms_v2.MechanismsOrganV2` composed in front of the frozen head `oracle_release_runtime_w503`.

## Verdict

- decision: **ADMIT** (gate v2)
- held-out domain: specialist 55/55 (false yes 0) vs head 3/55 (false yes 0)
- core capability panel: head 160 -> composed 160 (0 items swept in by the full sweep)
- reasons: none

## Sources and licences

- Ideal simple-machine relations (gears, belts, levers, pulleys, inclined planes, torque, shaft power) - OpenStax University Physics vol. 1 ch. 10-12 (CC-BY 4.0) https://openstax.org/details/books/university-physics-volume-1

## What it takes

- answers: gear_speed, gear_torque, gear_ratio, belt_speed, pulley_ma, pulley_effort, lever_effort, lever_ma, incline_ma, shaft_power, torque
- declines (in-domain): underspecified, impossible
- everything else falls through to the head unchanged

Supersedes: mechanisms (ADMIT gate v2, held-out 57/64; 7 misses safe declines)

## Notes and known gaps

v2 = v1 + (a) torque asked about a force on a lever with no effort/load arm named reads the lever as the lever arm - v1's held-out misses ('Find the torque when a force of 120 N is applied to a 0.25 m lever', declined for want of arms); (b) found on panel v2 DEV, a latent v1 defect: 'what effort lifts 600 N' - v1 read 'lift N' not 'lifts N' and with no load fell through to the mechanical advantage (confident answer to a different question); v2 reads lifts/lifted/lifting and NEVER answers an effort question with a mechanical advantage; (c) the family numbers rule (an underspecified decline on a turn with numbers becomes silence - the head answers). Judged under spec_gate_v3.1 on a FRESH panel v2 (seeds 424242/42424242; new phrasings incl. torque on a lever). Same author - disclosed.
