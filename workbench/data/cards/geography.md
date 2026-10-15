# Oracle7 World Geography (#67, tier A)

**id** `geography` - organ `organ_geography_v1.GeographyOrgan` composed in front of the frozen head `oracle_release_runtime_w503`.

## Verdict

- decision: **ADMIT** (gate v2)
- held-out domain: specialist 9/9 (false yes 0) vs head 1/9 (false yes 0)
- core capability panel: head 161 -> composed 161 (1 items swept in by the full sweep)
- reasons: none

## Sources and licences

- CIA World Factbook - capitals (including split capitals) (public domain (US government)) https://www.cia.gov/the-world-factbook/
- Haversine great-circle distance on the mean Earth sphere (R = 6,371 km); 15 degrees of longitude per hour of solar time (facts) https://www.movable-type.co.uk/scripts/latlong.html

## What it takes

- answers: capital, capital_split, gc_km, gc_miles, antipode, solar_time, lat_km
- declines (in-domain): none
- everything else falls through to the head unchanged

## Notes and known gaps

Split or relocating capitals answered with the split stated, never a single guessed city. Spherical Earth for distances (said so). Civil time zones differ from solar time (said so). Narrowed from the start (narrow_v1).
