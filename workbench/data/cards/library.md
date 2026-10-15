# Oracle7 Library & Archive Management (#14, tier B)

**id** `library` - organ `organ_library_v1.LibraryOrgan` composed in front of the frozen head `oracle_release_runtime_w503`.

## Verdict

- decision: **ADMIT** (gate v2)
- held-out domain: specialist 14/15 (false yes 0) vs head 1/15 (false yes 0)
- core capability panel: head 160 -> composed 160 (0 items swept in by the full sweep)
- reasons: none

## Sources and licences

- Library of Congress Classification Outline (public domain (US government)) https://www.loc.gov/catdir/cpso/lcco/
- ISBN (ISO 2108) and ISSN (ISO 3297) check-digit algorithms (facts (algorithms)) https://www.isbn-international.org/

## What it takes

- answers: lcc_class, lcc_sub, lcc_for_subject, isbn13_check, isbn10_check, isbn_valid, isbn_convert, issn_check, issn_valid
- declines (in-domain): impossible
- everything else falls through to the head unchanged

## Notes and known gaps

LCC main classes and a set of common subclasses from the LoC outline (Dewey Decimal is OCLC-copyrighted and not used). ISBN / ISSN arithmetic exact. Narrowed from the start (narrow_v1).
