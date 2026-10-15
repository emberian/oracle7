# Oracle7 Food Safety & Cold Chain v2 (#3, tier B)

**id** `coldchain-v2` - organ `organ_coldchain_v2.ColdChainOrganV2` composed in front of the frozen head `oracle_release_runtime_w503`.

## Verdict

- decision: **ADMIT** (gate v2)
- held-out domain: specialist 29/30 (false yes 0) vs head 2/30 (false yes 0)
- core capability panel: head 160 -> composed 160 (0 items swept in by the full sweep)
- reasons: none

## Sources and licences

- FDA Food Code 2022 (sections 3-401.11, 3-403.11, 3-501.14, 3-501.16, 3-501.17, 3-501.19) (public domain (US government)) https://www.fda.gov/food/fda-food-code/food-code-2022

## What it takes

- answers: cooling_check, cold_hold, hot_hold, cook_temp, reheat, tphc, tphc_rule, date_mark, date_rule, danger_zone
- declines (in-domain): none
- everything else falls through to the head unchanged

Supersedes: coldchain (ADMIT gate v2, held-out 18/30; 12 misses safe - not taken)

## Notes and known gaps

v2 = v1 + cooling checks in free word order ('Rice went from 135 F down to 70 F over 3 hours', 'After reaching 70 F, a stock cooled to 41 F within 5 hours'), named foods as food context, 'hamburgers' read as the singular v1's table knows (panel v2 dev), and the family numbers rule. Judged under spec_gate_v3.1 on a FRESH panel v2 (seeds 3003003/30030030). Same author - disclosed.
