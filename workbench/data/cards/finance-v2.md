# Oracle7 Personal Finance Arithmetic v2 (#65, tier B)

**id** `finance-v2` - organ `organ_finance_v2.FinanceOrganV2` composed in front of the frozen head `oracle_release_runtime_w503`.

## Verdict

- decision: **ADMIT** (gate v2)
- held-out domain: specialist 64/64 (false yes 0) vs head 3/64 (false yes 1)
- core capability panel: head 160 -> composed 162 (1 items swept in by the full sweep)
- reasons: none

## Sources and licences

- Standard time-value-of-money formulas (compound interest, amortization, APY, sinking fund) as published by the CFPB and Investor.gov calculators (public domain (US government)) https://www.investor.gov/financial-tools-calculators/calculators/compound-interest-calculator

## What it takes

- answers: apy, doubling, loan_interest, loan_payment, savings_goal, simple_interest, compound
- declines (in-domain): underspecified, advice
- everything else falls through to the head unchanged

Supersedes: finance (ADMIT gate v2, held-out 51/64; 13 misses safe declines)

## Notes and known gaps

v2 = v1 + a term written as an adjective ('a 15-year, $250,000 mortgage') and doubles/doubled/doubling as doubling - v1's held-out misses (safe declines) - and the family numbers rule. Arithmetic only; advice, prices and predictions still declined. Judged under spec_gate_v3.1 on a FRESH panel v2 (seeds 656565/65656565). Same author - disclosed.
