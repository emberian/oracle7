# Oracle7 Chemistry v3 (#38, tier A)

**id** `chemistry-v3` - organ `organ_chemistry_v3.ChemistryOrganV3` composed in front of the frozen head `oracle_release_runtime_w502`.

## Verdict

- decision: **ADMIT** (gate v2)
- held-out domain: specialist 223/281 (false yes 0) vs head 9/281 (false yes 4)
- core capability panel: head 160 -> composed 161 (1 items swept in by the full sweep)
- reasons: none

## Sources and licences

- PubChem periodic table (118 elements: masses, electronegativity, melting/boiling points, density, configuration) (public domain (NIH/NCBI)) https://pubchem.ncbi.nlm.nih.gov/periodic-table/
- OpenStax Chemistry 2e (already in the core's world stores) (CC-BY 4.0) https://openstax.org/details/books/chemistry-2e

## What it takes

- answers: molar_mass, g2mol, mol2g, percent, atomic_mass, atomic_number, electronegativity, melting_point, boiling_point, density, electron_configuration, ionization_energy, standard_state, group_block, year_discovered, symbol
- declines (in-domain): unknown, no_value
- everything else falls through to the head unchanged

Supersedes: chemistry (v1 admitted gate v1 - DO NOT SHIP: pronoun 'I' read as iodine); chemistry-r2 (DEV-FAIL on the dysprosium premise item)

## Notes and known gaps

v3 = r2 (narrowing + Fahrenheit) + formula_reader_v2 (a real formula wins anywhere; a lone element symbol only after of/for) - fixes v1's CONFIDENT WRONG 'How do I find the molar mass of NaCl?' -> iodine. INVARIANT vs v1 on 281/281 held-out and 225/225 dev inputs, so the same held-out panel is re-run (v1's domain result by construction). Judged under spec_gate_v3.1: the core item 'boiling point of dysprosium in Fahrenheit' (must-decline, premise 'answer is in no store') is scored for both runtimes against the independent SimpleQA key (4,653 F); the specialist states 4652.33 F from PubChem 2840 K.
