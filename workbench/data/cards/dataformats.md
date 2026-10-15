# Oracle7 Data Formats (#60, tier A)

**id** `dataformats` - organ `organ_formats_v1.FormatsOrgan` composed in front of the frozen head `oracle_release_runtime_w363`.

## Verdict

- decision: **ADMIT** (gate v2)
- held-out domain: specialist 93/93 (false yes 0) vs head 3/93 (false yes 0)
- core capability panel: head 161 -> composed 161 (1 items swept in by the full sweep)
- reasons: none

## Sources and licences

- RFC 8259 (JSON), RFC 4648 (base64), RFC 3986 (URL percent-encoding), FIPS 180-4 (SHA), ISO 8601 dates - via the Python standard library's reference implementations (IETF Trust / public domain (NIST) / PSF) https://www.rfc-editor.org/

## What it takes

- answers: json_valid, json_invalid, b64_decode, b64_encode, hash, url_decode, url_encode, base, weekday
- declines (in-domain): b64_invalid, base_invalid, date_invalid
- everything else falls through to the head unchanged

## Notes and known gaps

Exact computation by the standard library. Panel: base conversions via format(), weekdays via Zeller's congruence (independent of the organ's datetime), JSON valid/broken by construction. Dev caught a dangerous bug (a fragment of truncated JSON judged valid) - fixed before the held-out run. First dev gate FAILED (core 159 < 160): the organ took one core item ('Convert 2821 to hexadecimal') and answered 'B05' where the core convention is 'b05'. Fixed by adopting lowercase hex (Python's and the core's convention) and making the panel scorer compare hex case-insensitively; gate unchanged, dev re-run.
