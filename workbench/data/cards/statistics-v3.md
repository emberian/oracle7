# Oracle7 Statistics v3 (#45, tier A)

**id** `statistics-v3` - organ `organ_stats_v3.StatsOrganV3` composed in front of the frozen head `oracle_release_runtime_w363`.

## Verdict

- decision: **ADMIT** (gate v2)
- held-out domain: specialist 142/144 (false yes 2) vs head 51/144 (false yes 2)
- core capability panel: head 165 -> composed 165 (5 items swept in by the full sweep)
- reasons: none

## Sources and licences

- Standard definitions of descriptive statistics, counting and the binomial distribution (as in the NIST/SEMATECH e-Handbook of Statistical Methods) (public domain (NIST)) https://www.itl.nist.gov/div898/handbook/

## What it takes

- answers: mean, median, mode, range, stdev, variance, combinations, permutations, binomial, z
- declines (in-domain): impossible, too_few
- everything else falls through to the head unchanged

Supersedes: statistics-v2 (ADMIT gate v2, 132/144; misses = 'mean of the data set ...')

## Notes and known gaps

v3 = v2 + 'of the data set / the data / these numbers / the values / the sample' read as 'of'. Judged under spec_gate_v2 on a FRESH panel (new seeds, new phrasings both splits including the class). Same author - disclosed. Earlier notes: v2 = v1 + (1) CONFIDENT-WRONG fix found by the full-core sweep after admission: v1 swapped n and k when k > n ('choose 12 from 5' -> 792); v2 withholds impossible counts and reads argument order from the phrasing; (2) binomial p read as a class (v1 held-out missed 'chance of success is p'). Judged under spec_gate_v2 (full core sweep, per-item no-worse) on a FRESH panel v2 (new seeds and phrasings both splits, impossible counts as must-decline). Same author - disclosed.
