# Oracle7 Genetics v2 (#35, tier A)

**id** `genetics-v2` - organ `organ_genetics_v2.GeneticsOrganV2` composed in front of the frozen head `oracle_release_runtime_w503`.

## Verdict

- decision: **ADMIT** (gate v2)
- held-out domain: specialist 15/20 (false yes 0) vs head 1/20 (false yes 0)
- core capability panel: head 160 -> composed 160 (0 items swept in by the full sweep)
- reasons: none

## Sources and licences

- OpenStax Biology 2e ch. 12 (Mendel's experiments, Punnett squares, dihybrid crosses) and ch. 19 (Hardy-Weinberg) (CC-BY 4.0) https://openstax.org/details/books/biology-2e
- NIH NHGRI Talking Glossary of Genomic and Genetic Terms (public domain (US government)) https://www.genome.gov/genetics-glossary

## What it takes

- answers: genotype_prob, phenotype_prob, pheno_ratio, geno_ratio, hw_carrier, hw_p2, hw_p, hw_q
- declines (in-domain): impossible, underspecified
- everything else falls through to the head unchanged

Supersedes: genetics (v1 NEGATIVE under gate v3: 2 wrong from head fallthrough)

## Notes and known gaps

v2 = v1 + crosses answered before the Hardy-Weinberg branch (v1's HW trigger intercepted 'what fraction ... recessive trait' crosses and returned nothing), 'of a population' / 'shows a recessive', bare 'what is q', and recognise-then-decline for HW. v1 NEGATIVE under gate v3: held-out 16/20 vs 1/20 but 2 WRONG - the head's answers on turns v1 fell silent on. Fresh panel v2 (seeds 353535/35353535). Same author - disclosed.
