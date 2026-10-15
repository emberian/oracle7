# Oracle7 Seismology & Earthquakes (#23, tier B)

**id** `seismology` - organ `organ_seismology_v1.SeismologyOrgan` composed in front of the frozen head `oracle_release_runtime_w503`.

## Verdict

- decision: **ADMIT** (gate v2)
- held-out domain: specialist 29/34 (false yes 0) vs head 3/34 (false yes 0)
- core capability panel: head 160 -> composed 160 (0 items swept in by the full sweep)
- reasons: none

## Sources and licences

- USGS Earthquake Hazards Program - magnitude, energy (10^1.5 per unit), amplitude (10x per unit), S-P travel-time location (public domain (US government)) https://www.usgs.gov/programs/earthquake-hazards/earthquake-magnitude-energy-release-and-shaking-intensity
- IASPEI standard moment magnitude Mw = (log10 M0 - 9.1)/1.5 (Hanks & Kanamori 1979) (facts) http://www.iaspei.org/commissions/commission-on-seismological-observation-and-interpretation/Summary_WG_recommendations_20130327.pdf

## What it takes

- answers: energy_ratio, amplitude_ratio, mw, m0, sp_distance, gr_count
- declines (in-domain): underspecified, impossible
- everything else falls through to the head unchanged

## Notes and known gaps

Relations named in each answer. 'How many times stronger' is ASKED BACK (energy 10^(1.5 dM) vs amplitude 10^dM differ) - never picked. S-P distance only with both wave speeds given (no rule of thumb); Gutenberg-Richter only with a and b. Never predicts or forecasts earthquakes (falls through). Narrowed from the start (narrow_v1).
