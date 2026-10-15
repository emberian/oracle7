# Oracle7 Meteorology & Weather (#20, tier A)

**id** `meteorology` - organ `organ_weather_v1.WeatherOrgan` composed in front of the frozen head `oracle_release_runtime_w363`.

## Verdict

- decision: **ADMIT** (gate v2)
- held-out domain: specialist 46/46 (false yes 0) vs head 2/46 (false yes 1)
- core capability panel: head 160 -> composed 160 (0 items swept in by the full sweep)
- reasons: none

## Sources and licences

- NWS heat index equation (Rothfusz regression + NWS adjustments) and NWS 2001 wind chill formula (public domain (US government)) https://www.wpc.ncep.noaa.gov/html/heatindex_equation.shtml
- NHC Saffir-Simpson Hurricane Wind Scale (public domain (US government)) https://www.nhc.noaa.gov/aboutsshws.php
- WMO Beaufort scale (knots); Magnus dew-point coefficients 17.62 / 243.12 C; ICAO standard atmosphere troposphere (facts / published constants) https://library.wmo.int/

## What it takes

- answers: heat_index, wind_chill, wc_undefined, dew_point, air_temperature, relative_humidity, saffir_simpson, beaufort, isa_pressure, isa_temperature
- declines (in-domain): underspecified, impossible, out_of_range
- everything else falls through to the head unchanged

## Notes and known gaps

Published formulas and tables only; never a forecast (tomorrow/forecast/will it rain are not taken). Dev caught two CONFIDENT-WRONG classes before held-out: (1) a nearest-word heuristic tied and swapped air temperature and dew point (answered a must-decline) - replaced by the value attached to 'dew point'; (2) a given dew point was recomputed instead of solving for the asked air temperature - now routed by what is given, with Magnus inverted (round trip 30 C -> 18.44 C -> 30 C).
