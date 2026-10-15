# Oracle7 Water Quality & Treatment (#6, tier B)

**id** `water` - organ `organ_water_v1.WaterOrgan` composed in front of the frozen head `oracle_release_runtime_w363`.

## Verdict

- decision: **ADMIT** (gate v2)
- held-out domain: specialist 47/47 (false yes 0) vs head 3/47 (false yes 0)
- core capability panel: head 160 -> composed 160 (0 items swept in by the full sweep)
- reasons: none

## Sources and licences

- EPA / state operator-certification formulas: pounds formula (8.34 lb/gal), CT, dose = demand + residual, C1V1 = C2V2 (public domain (US government)) https://www.epa.gov/dwreginfo
- Exact grain (64.79891 mg) and US gallon (3.785411784 L) definitions (NIST) (public domain (NIST)) https://www.nist.gov/pml/owm/si-units

## What it takes

- answers: gpg_to_mgl, mgl_to_gpg, pounds_product, pounds, ct, dose, dilution, ph, h_conc
- declines (in-domain): underspecified, judgement, impossible
- everything else falls through to the head unchanged

## Notes and known gaps

Treatment and unit arithmetic only; never says water is safe to drink (declined: needs a lab test against the local standard). Dilution reads the stronger concentration as the stock (a dilution cannot concentrate). Narrowed from the start (narrow_v1). Dev fix: a lookahead refused 'N liters of M ppm'.
