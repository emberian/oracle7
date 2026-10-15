# Oracle7 Sports & Rules (statistics) (#72, tier B)

**id** `sports` - organ `organ_sports_v1.SportsOrgan` composed in front of the frozen head `oracle_release_runtime_w503`.

## Verdict

- decision: **ADMIT** (gate v2)
- held-out domain: specialist 19/19 (false yes 0) vs head 0/19 (false yes 1)
- core capability panel: head 160 -> composed 160 (0 items swept in by the full sweep)
- reasons: none

## Sources and licences

- MLB official statistics glossary (AVG, OBP, SLG, ERA, WHIP), NFL passer rating formula, basketball true shooting (published formulas) (facts (formulas)) https://www.mlb.com/glossary
- Wikipedia sports-statistics articles (formula cross-check) (CC-BY-SA 4.0 (store ships share-alike)) https://en.wikipedia.org/wiki/Passer_rating

## What it takes

- answers: avg, obp, slg, era, whip, passer_rating, ts_pct, win_pct, games_behind
- declines (in-domain): impossible
- everything else falls through to the head unchanged

## Notes and known gaps

Formulas named in every answer; innings in box-score thirds (6.2 = 6 2/3); no betting odds or predictions. Games-behind order-free (absolute value) and the panel puts the leader first and last (panel rule). Narrowed from the start (narrow_v1).
