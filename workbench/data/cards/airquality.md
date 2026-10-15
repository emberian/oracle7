# Oracle7 Air Quality & Atmosphere (#7, tier B)

**id** `airquality` - organ `organ_airquality_v1.AirQualityOrgan` composed in front of the frozen head `oracle_release_runtime_w503`.

## Verdict

- decision: **ADMIT** (gate v2)
- held-out domain: specialist 30/38 (false yes 0) vs head 2/38 (false yes 1)
- core capability panel: head 160 -> composed 160 (0 items swept in by the full sweep)
- reasons: none

## Sources and licences

- EPA AQI breakpoint table (AQS code table; 2024 PM2.5 revision), verified 2026-09-29 (public domain (US government)) https://aqs.epa.gov/aqsweb/documents/codetables/aqi_breakpoints.html
- EPA Technical Assistance Document for the Reporting of Daily Air Quality - the AQI (truncation rules, interpolation) (public domain (US government)) https://document.airnow.gov/technical-assistance-document-for-the-reporting-of-daily-air-quailty.pdf

## What it takes

- answers: aqi, overall, category
- declines (in-domain): impossible
- everything else falls through to the head unchanged

## Notes and known gaps

Standard averaging periods assumed and stated (PM 24-hour, O3/CO 8-hour, SO2/NO2 1-hour); ozone in ppb converted to ppm. Beyond-the-AQI, 8-hour ozone above 0.200 ppm and 1-hour SO2 above 304 ppb declined (other tables apply); hourly PM (NowCast) not computed. No personal health advice (should I / is it safe for me turns fall through). Panel computes its own expectations from the verified table. Narrowed from the start (narrow_v1).
