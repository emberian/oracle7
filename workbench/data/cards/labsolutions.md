# Oracle7 Laboratory Solutions (#15, tier B)

**id** `labsolutions` - organ `organ_labsolutions_v1.LabSolutionsOrgan` composed in front of the frozen head `oracle_release_runtime_w363`.

## Verdict

- decision: **ADMIT** (gate v2)
- held-out domain: specialist 26/27 (false yes 1) vs head 1/27 (false yes 1)
- core capability panel: head 160 -> composed 160 (0 items swept in by the full sweep)
- reasons: none

## Sources and licences

- PubChem Periodic Table of Elements (atomic masses) - molar masses by the chemistry specialist's exact parser (public domain (NIH/NCBI)) https://pubchem.ncbi.nlm.nih.gov/periodic-table/
- Solution-preparation relations (m = MVMW, M1V1 = M2V2, % w/v) - OpenStax Chemistry 2e ch. 3 (CC-BY 4.0) https://openstax.org/details/books/chemistry-2e

## What it takes

- answers: wv_mass, dilution, molarity, mass_needed
- declines (in-domain): underspecified, bad_formula, impossible
- everything else falls through to the head unchanged

## Notes and known gaps

Compounds as formulas only; a name alone is declined. Formula reader v2: real formulas win anywhere; a lone element symbol only as the object of 'of'/'for'. Dev caught a CONFIDENT WRONG inherited from the admitted chemistry organ's reader: 'How many grams of table salt do I need ...' was computed for IODINE (the pronoun 'I'). Panel molar masses computed by the panel's own CSV reader.
