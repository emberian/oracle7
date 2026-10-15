# Oracle7 Medicine (reference only) (#90, tier C)

**id** `medicine` - organ `organ_facts_v1.FactsOrgan` composed in front of the frozen head `oracle_release_runtime_w503`.

## Verdict

- decision: **ADMIT** (gate v2)
- held-out domain: specialist 9/9 (false yes 0) vs head 2/9 (false yes 0)
- core capability panel: head 160 -> composed 160 (0 items swept in by the full sweep)
- reasons: none

## Sources and licences

- MedlinePlus (NIH NLM) (public domain (US government)) https://medlineplus.gov/
- CDC antibiotic use / vaccine history (public domain (US government)) https://www.cdc.gov/

## What it takes

- answers: medicine
- declines (in-domain): none
- everything else falls through to the head unchanged

## Notes and known gaps

Typed-fact organ (tier C): general reference values and history of medicine. Symptoms, diagnosis, a person's readings, treatment, medication and dosing are blocked (the head answers). Narrowed (narrow_v1).
