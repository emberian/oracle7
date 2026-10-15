# Oracle7 Fleet & Vehicle Arithmetic (#9, tier B)

**id** `fleet` - organ `organ_fleet_v1.FleetOrgan` composed in front of the frozen head `oracle_release_runtime_w363`.

## Verdict

- decision: **ADMIT** (gate v2)
- held-out domain: specialist 54/54 (false yes 0) vs head 2/54 (false yes 1)
- core capability panel: head 160 -> composed 160 (0 items swept in by the full sweep)
- reasons: none

## Sources and licences

- EPA 'Greenhouse Gas Emissions from a Typical Passenger Vehicle' (8,887 g CO2/gal gasoline; 10,180 g/gal diesel) (public domain (US government)) https://www.epa.gov/greenvehicles/greenhouse-gas-emissions-typical-passenger-vehicle
- Exact unit definitions (US gallon 3.785411784 L, mile 1.609344 km, imperial gallon 4.54609 L) and stopping-distance kinematics (OpenStax University Physics) (NIST (PD) / CC-BY 4.0) https://www.nist.gov/pml/owm/si-units

## What it takes

- answers: braking, stopping, to_lpk, to_mpg, co2, trip_cost, trip_litres, trip_gallons
- declines (in-domain): underspecified, need_price, impossible
- everything else falls through to the head unchanged

## Notes and known gaps

Constants stated in every answer. Never assumes a fuel price, a reaction time or a friction coefficient (stopping distance declines without them; braking distance needs only friction). Conversion mpg <-> L/100 km only when no trip distance is given.
