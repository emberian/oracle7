# Oracle7 Acoustics & Sound (#49, tier A)

**id** `acoustics` - organ `organ_acoustics_v1.AcousticsOrgan` composed in front of the frozen head `oracle_release_runtime_w363`.

## Verdict

- decision: **ADMIT** (gate v2)
- held-out domain: specialist 69/69 (false yes 0) vs head 3/69 (false yes 1)
- core capability panel: head 160 -> composed 160 (0 items swept in by the full sweep)
- reasons: none

## Sources and licences

- Speed of sound in dry air v = 331.3 sqrt(1 + T/273.15) m/s; fresh water 1481 m/s at 20 C (stated in every answer) (facts / physics) https://en.wikipedia.org/wiki/Speed_of_sound
- Decibel, Doppler, pipe and string harmonic formulas (OpenStax University Physics vol. 1, ch. 17) (CC-BY 4.0) https://openstax.org/details/books/university-physics-volume-1

## What it takes

- answers: beat, doppler, db_sum, db_distance, db_ratio, intensity_ratio, string, pipe_closed, pipe_open, wavelength, frequency, speed
- declines (in-domain): underspecified, impossible
- everything else falls through to the head unchanged

## Notes and known gaps

Formulas shown in every answer; air at 20 C stated whenever no temperature is given. Panel formulas written independently in acoustics_panel_v1.py. Dev fixes before held-out: one reply wording aligned to 'The X is N' (scorer unchanged), 'honk/whistle/hear' added as sound cues.
