# Oracle7 Carbon Capture & Climate Technology (#93, tier B)

**id** `carboncapture` - organ `organ_carboncapture_v1.CarbonCaptureOrgan` composed in front of the frozen head `oracle_release_runtime_w503`.

## Verdict

- decision: **ADMIT** (gate v2)
- held-out domain: specialist 14/14 (false yes 0) vs head 2/14 (false yes 0)
- core capability panel: head 160 -> composed 160 (0 items swept in by the full sweep)
- reasons: none

## Sources and licences

- EPA Greenhouse Gas Emissions from a Typical Passenger Vehicle (8,887 g CO2/gal gasoline, 10,180 g/gal diesel) (public domain (US government)) https://www.epa.gov/greenvehicles/greenhouse-gas-emissions-typical-passenger-vehicle
- DOE / NETL carbon capture: capture rate, energy intensity; molar masses C 12.011, CO2 44.01 (public domain (US government)) https://netl.doe.gov/carbon-management/carbon-capture

## What it takes

- answers: c_to_co2, co2_to_c, fuel_co2, co2_per_mile, captured, capture_energy
- declines (in-domain): impossible
- everything else falls through to the head unchanged

## Notes and known gaps

EPA emission factors named; capture rate and energy intensity only as given. No offset / credit pricing (falls through). Narrowed from the start (narrow_v1).
