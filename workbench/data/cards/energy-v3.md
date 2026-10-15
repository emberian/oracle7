# Oracle7 Home Energy & Solar v3 (#5, tier B)

**id** `energy-v3` - organ `organ_energy_v3.EnergyOrganV3` composed in front of the frozen head `oracle_release_runtime_w502`.

## Verdict

- decision: **ADMIT** (gate v2)
- held-out domain: specialist 69/70 (false yes 1) vs head 3/70 (false yes 1)
- core capability panel: head 160 -> composed 160 (0 items swept in by the full sweep)
- reasons: none

## Sources and licences

- Energy arithmetic (kWh = W x h / 1000; Wh = V x Ah; PV yield = kW x peak sun hours x derate) as in DOE Energy Saver and NREL PVWatts documentation (public domain (US government)) https://www.energy.gov/energysaver/estimating-appliance-and-home-electronic-energy-use

## What it takes

- answers: payback, never, runtime, solar_yield, swap_saving, cost, energy
- declines (in-domain): underspecified, need_tariff, impossible
- everything else falls through to the head unchanged

Supersedes: energy-v2 (ADMIT gate v2, 66/74, but 8 misses CONFIDENT WRONG: passive swap answered with energy used)

## Notes and known gaps

v3 = v2 + passive swap ('X W bulb is replaced by a Y W LED') + asked-quantity rule (a SAVING question is never answered with what is used). Judged under spec_gate_v3 (wrong-answer cap) on a FRESH panel v3. Same author - disclosed. v2 = v1 + payback roles from grammar (saving = the amount attached to save; cost = a DIFFERENT amount; no cost -> decline) - v1's held-out answered 'A heat pump saves $900 a year. How long is the payback?' with 1 year ($900/$900) and was NEGATIVE; + 'costs' read as 'cost'. Judged under spec_gate_v2 on a FRESH panel v2 (saving stated before cost in half the payback items). Same author - disclosed. Never assumes a tariff, price or sun-hours it was not given (a cost with no tariff gives the kWh and asks for the price). Losses stated: solar 'before losses' unless given; battery runtime before inverter and depth-of-discharge losses. Full-core pre-check: 0 of 3107 items taken. Dev fixes before hel
