# Oracle7 Units & Metrology v3 (#47, tier A)

**id** `units-v3` - organ `organ_units_v3.UnitsOrganV3` composed in front of the frozen head `oracle_release_runtime_w363`.

## Verdict

- decision: **ADMIT** (gate v2)
- held-out domain: specialist 75/75 (false yes 0) vs head 4/75 (false yes 0)
- core capability panel: head 164 -> composed 164 (4 items swept in by the full sweep)
- reasons: none

## Sources and licences

- NIST SP 811 and the SI Brochure: exact definitions of the inch, foot, mile, pound, US gallon, atmosphere, calorie and others (public domain (NIST)) https://www.nist.gov/pml/special-publication-811

## What it takes

- answers: convert, temperature
- declines (in-domain): mismatch, impossible
- everything else falls through to the head unchanged

Supersedes: units-v2 (ADMIT gate v2, 43/74; misses = two-sentence 'I have N X. How many Y is that?')

## Notes and known gaps

v3 = v2 + the two-sentence quantity question joined into v1's canonical order. Judged under spec_gate_v2 on a FRESH panel (new seeds, new phrasings both splits including the class). Same author - disclosed. Earlier notes: v2 = v1 + (1) EXACT rational factors (all definitions are exact): whole results printed whole, fractional results as decimal + exact value - the full-core sweep found v1 answering 12 core conversions in decimals/exponent form where the family's exact form is expected ('470/127', '4384800'); (2) narrowing (narrow_v1): rate word problems not taken; (3) quantity-first phrasing read as a class ('250 g equals how many pounds?'). Judged under spec_gate_v2 on a FRESH panel v2 (new seeds, new phrasings both splits, time units, new mismatch declines). Same author - disclosed. DISCLOSED MEASUREMENT DEFE
