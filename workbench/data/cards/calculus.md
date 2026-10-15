# Oracle7 Algebra & Calculus (#44, tier A)

**id** `calculus` - organ `organ_calculus_v1.CalculusOrgan` composed in front of the frozen head `oracle_release_runtime_w363`.

## Verdict

- decision: **ADMIT** (gate v2)
- held-out domain: specialist 62/62 (false yes 0) vs head 2/62 (false yes 0)
- core capability panel: head 160 -> composed 160 (0 items swept in by the full sweep)
- reasons: none

## Sources and licences

- Power rule for derivatives and antiderivatives; fundamental theorem of calculus (OpenStax Calculus vol. 1) (CC-BY 4.0) https://openstax.org/details/books/calculus-volume-1

## What it takes

- answers: derivative, derivative_at, antiderivative, definite
- declines (in-domain): underspecified
- everything else falls through to the head unchanged

## Notes and known gaps

CALCULUS ONLY: the core already owns equation solving (v23 algebra 164 + open_math solve items), so the organ never takes 'solve', LaTeX, or any non-polynomial. Exact rational arithmetic. Panel computed with its own coefficient-list arithmetic; scorer has its own polynomial reader. Dev caught a CONFIDENT WRONG bug before held-out: 'antiderivative' contains 'derivative' and was answered as a derivative - fixed.
