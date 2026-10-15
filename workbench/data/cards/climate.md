# Oracle7 Climate Science (#22, tier B)

**id** `climate` - organ `organ_climate_v1.ClimateOrgan` composed in front of the frozen head `oracle_release_runtime_w503`.

## Verdict

- decision: **ADMIT** (gate v2)
- held-out domain: specialist 24/24 (false yes 0) vs head 3/24 (false yes 0)
- core capability panel: head 160 -> composed 160 (0 items swept in by the full sweep)
- reasons: none

## Sources and licences

- NOAA Global Monitoring Laboratory / NASA climate basics; CO2 forcing 5.35 ln(C/C0) (Myhre et al. 1998, adopted by IPCC TAR); Stefan-Boltzmann effective temperature (public domain (US government) / facts) https://gml.noaa.gov/aggi/aggi.html
- Global Carbon Project conversion 1 ppm CO2 = 2.124 GtC (facts) https://www.globalcarbonproject.org/carbonbudget/

## What it takes

- answers: forcing, warming_ecs, warming_lambda, ppm_to_gtc, ppm_to_gtco2, mass_to_ppm, effective_temp, co2e
- declines (in-domain): underspecified, impossible
- everything else falls through to the head unchanged

## Notes and known gaps

Warming ONLY with a sensitivity or lambda given (the sensitivity is uncertain - never assumed); CO2e ONLY with a GWP given (values differ by IPCC report). Never projects future climate (will / by-a-year / project turns fall through). Narrowed from the start (narrow_v1).
