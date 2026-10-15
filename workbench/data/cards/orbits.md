# Oracle7 Spacecraft Operations (Orbital Mechanics) (#18, tier B)

**id** `orbits` - organ `organ_orbits_v1.OrbitsOrgan` composed in front of the frozen head `oracle_release_runtime_w363`.

## Verdict

- decision: **ADMIT** (gate v2)
- held-out domain: specialist 35/35 (false yes 0) vs head 3/35 (false yes 0)
- core capability panel: head 160 -> composed 160 (0 items swept in by the full sweep)
- reasons: none

## Sources and licences

- JPL Solar System Dynamics planetary physical parameters (GM, radii, sidereal rotation) (public domain (NASA/JPL)) https://ssd.jpl.nasa.gov/planets/phys_par.html
- Two-body relations (vis-viva, Hohmann transfer) - NASA 'Basics of Space Flight' (public domain (NASA)) https://science.nasa.gov/learn/basics-of-space-flight/

## What it takes

- answers: sync_alt, hohmann_time, hohmann_dv, escape, period, orbit_speed
- declines (in-domain): underspecified, no_sync
- everything else falls through to the head unchanged

## Notes and known gaps

Idealised two-body mechanics (point masses, circular orbits, no drag or perturbations), said so; constants stated in every answer. Checks: geostationary altitude 35,786 km, Earth surface escape 11.18 km/s, ISS (420 km) 7.66 km/s. Hohmann start orbit read from 'from X km' (roles from grammar).
