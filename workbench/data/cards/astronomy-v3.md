# Oracle7 Astronomy v3 (#16, tier A)

**id** `astronomy-v3` - organ `organ_astronomy_v3.AstronomyOrganV3` composed in front of the frozen head `oracle_release_runtime_w363`.

## Verdict

- decision: **ADMIT** (gate v2)
- held-out domain: specialist 137/138 (false yes 0) vs head 9/138 (false yes 0)
- core capability panel: head 160 -> composed 160 (0 items swept in by the full sweep)
- reasons: none

## Sources and licences

- NASA NSSDCA Planetary Fact Sheet (8 planets, the Moon, Pluto; 20 properties) (public domain (NASA)) https://nssdc.gsfc.nasa.gov/planetary/factsheet/
- OpenStax Astronomy 2e (already in the core's world stores) (CC-BY 4.0) https://openstax.org/details/books/astronomy-2e

## What it takes

- answers: mass, diameter, density, gravity, escape_velocity, length_of_day, rotation_period, distance_from_the_sun, orbital_period, orbital_velocity, orbital_eccentricity, axial_tilt, mean_temperature, surface_pressure, number_of_moons, ring_system, magnetic_field, light_time, weight, ratio, year_years, distance_from_earth
- declines (in-domain): unknown, no_value
- everything else falls through to the head unchanged

Supersedes: astronomy-v2 (ADMIT 2026-09-29 01:41 UTC, held-out 130/138; 8 misses = ratio direction)

## Notes and known gaps

v3 = v2 + comparison DIRECTION read from grammar (the body after relative to / than / exceed / compared to|with / versus / divided by / 'ratio of X to Y' is the reference). v2's held-out found 8 inverted ratios ('Relative to Mars, how many times as massive is Mercury?' answered Mars/Mercury). Judged under spec_gate_v2 on a FRESH panel v3 (seed 161616, new phrasings both splits, reference-first comparisons, fictional worlds mostly NOT on the organ's list). Same author - disclosed.
