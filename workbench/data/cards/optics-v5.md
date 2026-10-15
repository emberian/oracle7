# Oracle7 Optics & Light v5 (#48, tier A)

**id** `optics-v5` - organ `organ_optics_v5.OpticsOrganV5` composed in front of the frozen head `oracle_release_runtime_w503`.

## Verdict

- decision: **ADMIT** (gate v2)
- held-out domain: specialist 51/65 (false yes 0) vs head 2/65 (false yes 1)
- core capability panel: head 160 -> composed 160 (0 items swept in by the full sweep)
- reasons: none

## Sources and licences

- SI defining constants h, c, e (exact since 2019, BIPM SI Brochure 9th ed.) (public (BIPM)) https://www.bipm.org/en/publications/si-brochure
- Refractive indices at 589 nm for water, diamond, air (stated in every answer) (facts) https://refractiveindex.info/

## What it takes

- answers: photon_energy, frequency, wavelength, lens_power, image_distance, magnification, at_focus, critical_angle, no_critical, medium_speed, tir, refraction_angle, index
- declines (in-domain): underspecified, impossible
- everything else falls through to the head unchanged

Supersedes: optics-v3 (standing; ADMIT gate v2, held-out 53/67). optics-v4 NEGATIVE (gate v3, 4 wrong) - DO NOT SHIP.

## Notes and known gaps

v5 = v3 + v4's object-distance phrasing + 'how fast light travels inside/through' read as speed in the medium, WITHOUT the family numbers rule. optics-v4 was NEGATIVE under gate v3 (held-out 61/65, 4 WRONG > cap 1): the numbers rule turned v3's safe declines into silence and the head (2/65 in optics) answered 'how fast light travels' with a dictionary definition of 'fast'. LAW: the numbers rule is only safe where the head answers the domain's numeric turns. Judged under spec_gate_v3.1 on a FRESH panel v5 (seeds 5050505/505050505). Same author - disclosed.
