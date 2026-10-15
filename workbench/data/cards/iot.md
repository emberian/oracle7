# Oracle7 Sensor Networks & IoT (#94, tier B)

**id** `iot` - organ `organ_iot_v1.IotOrgan` composed in front of the frozen head `oracle_release_runtime_w503`.

## Verdict

- decision: **ADMIT** (gate v2)
- held-out domain: specialist 27/27 (false yes 0) vs head 2/27 (false yes 1)
- core capability panel: head 160 -> composed 160 (0 items swept in by the full sweep)
- reasons: none

## Sources and licences

- NIST IoT and measurement publications; ideal ADC transfer (LSB = Vref / 2^n), Nyquist-Shannon sampling, duty-cycle average current (public domain (US government) / facts) https://www.nist.gov/programs-projects/nist-cybersecurity-iot-program

## What it takes

- answers: adc_voltage, adc_code, adc_lsb, avg_current, battery_life, nyquist, data_rate, storage_day
- declines (in-domain): underspecified, impossible
- everything else falls through to the head unchanged

## Notes and known gaps

Ideal ADC convention LSB = Vref / 2^n (named; some datasheets use 2^n - 1). Battery life is ideal (no self-discharge / derating), said so. Radio link budgets are left to spacecomms (#95). Narrowed from the start (narrow_v1).
