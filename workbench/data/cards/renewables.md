# Oracle7 Renewable Energy (#98, tier B)

**id** `renewables` - organ `organ_renewables_v1.RenewablesOrgan` composed in front of the frozen head `oracle_release_runtime_w503`.

## Verdict

- decision: **ADMIT** (gate v2)
- held-out domain: specialist 23/26 (false yes 0) vs head 1/26 (false yes 2)
- core capability panel: head 160 -> composed 160 (0 items swept in by the full sweep)
- reasons: none

## Sources and licences

- NREL / DOE Wind Energy Technologies Office - wind power P = 1/2 rho A v^3 Cp, Betz limit 16/27, capacity factor (public domain (US government)) https://www.energy.gov/eere/wind/how-do-wind-turbines-work
- DOE Water Power Technologies Office - hydropower P = rho g Q h eta; NREL PV basics (STC 1,000 W/m2) (public domain (US government)) https://www.energy.gov/eere/water/types-hydropower-plants

## What it takes

- answers: wind_power, wind_ratio, capacity_factor, annual_energy, pv_power, hydro
- declines (in-domain): underspecified, impossible
- everything else falls through to the head unchanged

## Notes and known gaps

Air density 1.225 kg/m3 unless given (said so); without a Cp the answer is the power IN the wind, labelled as such. Cp above Betz, CF above 100%, efficiency above 100% declined; PV without irradiance asks for it (STC used only when named). Narrowed from the start (narrow_v1).
