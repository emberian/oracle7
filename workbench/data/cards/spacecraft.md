# Oracle7 Spacecraft Operations (#18, tier B)

**id** `spacecraft` - organ `organ_spacecraft_v1.SpacecraftOrgan` composed in front of the frozen head `oracle_release_runtime_w503`.

## Verdict

- decision: **ADMIT** (gate v2)
- held-out domain: specialist 14/21 (false yes 0) vs head 0/21 (false yes 1)
- core capability panel: head 160 -> composed 160 (0 items swept in by the full sweep)
- reasons: none

## Sources and licences

- NASA Glenn Research Center Beginner's Guide to Rockets: ideal rocket equation, specific impulse, thrust, mass flow (public domain (US government)) https://www.grc.nasa.gov/www/k-12/rocket/rktpow.html

## What it takes

- answers: delta_v, propellant, exhaust_velocity, twr, mass_flow, burn_time
- declines (in-domain): impossible
- everything else falls through to the head unchanged

## Notes and known gaps

Ideal (Tsiolkovsky) relations, g0 = 9.80665 m/s2, stated. Mass roles from grammar (initial/wet/fueled vs final/dry/empty/burnout), never order. Narrowed from the start (narrow_v1); no numbers rule.
