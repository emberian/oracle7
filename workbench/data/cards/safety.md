# Oracle7 Occupational Safety Arithmetic (#10, tier B)

**id** `safety` - organ `organ_safety_v1.SafetyOrgan` composed in front of the frozen head `oracle_release_runtime_w363`.

## Verdict

- decision: **ADMIT** (gate v2)
- held-out domain: specialist 45/45 (false yes 0) vs head 4/45 (false yes 0)
- core capability panel: head 160 -> composed 160 (0 items swept in by the full sweep)
- reasons: none

## Sources and licences

- OSHA 29 CFR 1910.95 (occupational noise: Table G-16, Appendix A dose and TWA formulas) (public domain (US government)) https://www.osha.gov/laws-regs/regulations/standardnumber/1910/1910.95
- OSHA 29 CFR 1926.1053(b)(5)(i) (ladder 4-to-1 rule) (public domain (US government)) https://www.osha.gov/laws-regs/regulations/standardnumber/1926/1926.1053
- NIOSH Applications Manual for the Revised NIOSH Lifting Equation (1994, metric) (public domain (US government)) https://www.cdc.gov/niosh/docs/94-110/

## What it takes

- answers: noise_time, noise_dose, twa, ladder, rwl, lifting_index
- declines (in-domain): underspecified, judgement
- everything else falls through to the head unchanged

## Notes and known gaps

Regulation arithmetic only, cited. Never judges whether a specific workplace situation is safe (declined: needs a qualified person on site) - only workplace-context 'is it safe' questions are taken at all. NIOSH frequency and coupling multipliers are table values that must be stated, never assumed. Dev fix before held-out: each NIOSH input read by its own label ('horizontal distance' was readable as the travel distance). Full-core pre-check: 0 of 3107.
