# Oracle7 SQL & Databases (#53, tier A)

**id** `sql` - organ `organ_sql_v1.SqlOrgan` composed in front of the frozen head `oracle_release_runtime_w363`.

## Verdict

- decision: **ADMIT** (gate v2)
- held-out domain: specialist 61/61 (false yes 0) vs head 2/61 (false yes 0)
- core capability panel: head 160 -> composed 160 (0 items swept in by the full sweep)
- reasons: none

## Sources and licences

- SQLite (public domain) - the answer is SQLite's own execution of the user's statements (public domain) https://sqlite.org/copyright.html

## What it takes

- answers: valid, invalid, scalar, rows, error
- declines (in-domain): needs_data, runaway, setup_error
- everything else falls through to the head unchanged

## Notes and known gaps

Answers by execution in a sandboxed in-memory SQLite (authorizer denies ATTACH/extensions/PRAGMA writes; step budget; 1 MB value and 20k SQL limits). Panel results computed in Python over the generated rows, including SQL semantics (SUM of no rows is NULL, COUNT(col) skips NULLs). Dev fixes before held-out: concept questions ('What does SELECT mean?') are not executed; query errors classified as query errors.
