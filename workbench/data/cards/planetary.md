# Oracle7 Planetary Science (#17, tier A)

**id** `planetary` - organ `organ_planetary_v1.PlanetaryOrgan` composed in front of the frozen head `oracle_release_runtime_w503`.

## Verdict

- decision: **ADMIT** (gate v2)
- held-out domain: specialist 16/18 (false yes 2) vs head 0/18 (false yes 2)
- core capability panel: head 160 -> composed 160 (0 items swept in by the full sweep)
- reasons: none

## Sources and licences

- NASA Goddard Planetary Fact Sheet relations (surface gravity, escape velocity, mean density) (public domain (US government)) https://nssdc.gsfc.nasa.gov/planetary/factsheet/

## What it takes

- answers: gravity, escape, orbital_v, density, weight
- declines (in-domain): none
- everything else falls through to the head unchanged

## Notes and known gaps

Computes ONLY from mass and radius given in the turn (SI or Earth units); no stored planet table - 'surface gravity of Jupiter' falls through (convention-dependent for gas giants). Earth units: g 9.81, M 5.972e24 kg, R 6371 km, said so. No in-domain declines. Narrowed from the start (narrow_v1).
