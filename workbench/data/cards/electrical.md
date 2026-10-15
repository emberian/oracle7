# Oracle7 Electrical Engineering (Power) (#50, tier A)

**id** `electrical` - organ `organ_electrical_v1.ElectricalOrgan` composed in front of the frozen head `oracle_release_runtime_w503`.

## Verdict

- decision: **ADMIT** (gate v2)
- held-out domain: specialist 22/24 (false yes 0) vs head 2/24 (false yes 0)
- core capability panel: head 160 -> composed 160 (0 items swept in by the full sweep)
- reasons: none

## Sources and licences

- US Navy Electrical Engineering Training Series (NEETS) Module 2 (AC), Module 5 (generators/transformers), three-phase power relations (public domain (US government)) https://www.navy.mil/

## What it takes

- answers: three_phase_kw, three_phase_kva, three_phase_current, wye_vline, delta_iline, pf, reactive, pf_correction, xfmr_v, xfmr_i, hp_kw, kw_hp
- declines (in-domain): underspecified, impossible
- everything else falls through to the head unchanged

## Notes and known gaps

Ideal transformer; balanced three-phase; mechanical horsepower 745.7 W. Real power needs a stated power factor (never assumed). A ratio 'N:1' is primary:secondary. Narrowed from the start (narrow_v1); no numbers rule.
