# Oracle7 Retail Store Operations (#13, tier A)

**id** `retail` - organ `organ_retail_v1.RetailOrgan` composed in front of the frozen head `oracle_release_runtime_w363`.

## Verdict

- decision: **ADMIT** (gate v2)
- held-out domain: specialist 51/51 (false yes 0) vs head 3/51 (false yes 0)
- core capability panel: head 160 -> composed 160 (0 items swept in by the full sweep)
- reasons: none

## Sources and licences

- Standard retail and operations-management formulas (gross margin, markup, inventory turnover, reorder point, Wilson EOQ, break-even) - SBA and OpenStax Principles of Accounting / Introduction to Business (public domain (SBA) / CC-BY 4.0 (OpenStax)) https://openstax.org/details/books/principles-managerial-accounting

## What it takes

- answers: break_even, never_even, eoq, rop, days_inventory, turnover, markup, margin, price_from_markup, price_from_margin, discount, with_tax
- declines (in-domain): underspecified, impossible
- everything else falls through to the head unchanged

## Notes and known gaps

Margin and markup kept apart by the question's own word (the panel asks both of the same numbers, so confusing them is caught). Stacked discounts compound. Dev fix: the scorer read no '$' before the value (organ unchanged). Narrowed from the start (narrow_v1).
