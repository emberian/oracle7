# Oracle7 Microbiology (#33, tier A)

**id** `microbiology-v2` - organ `organ_micro_v2.MicroOrganV2` composed in front of the frozen head `oracle_release_runtime_w503`.

## Verdict

- decision: **ADMIT** (gate v2)
- held-out domain: specialist 13/13 (false yes 0) vs head 1/13 (false yes 0)
- core capability panel: head 160 -> composed 160 (0 items swept in by the full sweep)
- reasons: none

## Sources and licences

- OpenStax Microbiology ch. 9 (microbial growth: binary fission, generation time, viable plate counts, serial dilution) (CC-BY 4.0) https://openstax.org/details/books/microbiology

## What it takes

- answers: growth_n, generations, gen_time, cfu, serial
- declines (in-domain): impossible, underspecified
- everything else falls through to the head unchanged

## Notes and known gaps

v2 of microbiology (v1 NEGATIVE 2026-09-29: a computed growth answer silenced by the narrative filter; 'from N cells to M cells' unread -> head wrongs). Narrative filter skipped for asking turns; reads from-to counts, 'population of N cells', successive / tenfold dilutions; recognise-then-decline. Fresh panel v2.
