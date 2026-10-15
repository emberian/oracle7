# Oracle7 Thermodynamics & Energy (#43, tier A)

**id** `thermo` - organ `organ_thermo_v1.ThermoOrgan` composed in front of the frozen head `oracle_release_runtime_w363`.

## Verdict

- decision: **ADMIT** (gate v2)
- held-out domain: specialist 50/50 (false yes 0) vs head 3/50 (false yes 1)
- core capability panel: head 160 -> composed 160 (0 items swept in by the full sweep)
- reasons: none

## Sources and licences

- Gas constant R = 8.314462618 J/(mol K) and Stefan-Boltzmann constant (exact / exact-derived, 2019 SI; CODATA) (public (BIPM/NIST)) https://physics.nist.gov/cuu/Constants/
- Specific heats and latent heats of common materials (OpenStax University Physics vol. 2, Table 1.3 and 1.4 values, stated in every answer) (CC-BY 4.0) https://openstax.org/details/books/university-physics-volume-2

## What it takes

- answers: carnot, gas_pressure, gas_volume, gas_moles, gas_temperature, radiated_power, latent_fusion, latent_vapor, sensible_heat
- declines (in-domain): underspecified, impossible
- everything else falls through to the head unchanged

## Notes and known gaps

Exact constants; the table value used is named in every answer; materials outside the table are declined unless a specific heat is given. Kelvin conversion shown. Panel formulas written independently in thermo_panel_v1.py.
