# Oracle7 Oceanography (#21, tier B)

**id** `ocean` - organ `organ_ocean_v1.OceanOrgan` composed in front of the frozen head `oracle_release_runtime_w503`.

## Verdict

- decision: **ADMIT** (gate v2)
- held-out domain: specialist 23/23 (false yes 0) vs head 2/23 (false yes 0)
- core capability panel: head 160 -> composed 160 (0 items swept in by the full sweep)
- reasons: none

## Sources and licences

- NOAA Ocean Service / NOAA Tsunami program - shallow-water wave speed sqrt(g d), deep-water dispersion, pressure with depth, echo sounding (public domain (US government)) https://oceanservice.noaa.gov/facts/

## What it takes

- answers: shallow_speed, tsunami_time, deep_speed, deep_wavelength, pressure, pressure_abs, sonar_depth
- declines (in-domain): none
- everything else falls through to the head unchanged

## Notes and known gaps

g = 9.81; seawater 1,025 kg/m3 and sound 1,500 m/s unless given (said so). No in-domain declines in v1: the organ answers what it can compute and is silent otherwise; the panel's invalid items are off-domain ocean questions it must NOT take. Narrowed from the start (narrow_v1).
