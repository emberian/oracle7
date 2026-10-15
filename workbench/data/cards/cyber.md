# Oracle7 Cybersecurity (Defensive) (#56, tier A)

**id** `cyber` - organ `organ_cyber_v1.CyberOrgan` composed in front of the frozen head `oracle_release_runtime_w503`.

## Verdict

- decision: **ADMIT** (gate v2)
- held-out domain: specialist 16/20 (false yes 1) vs head 1/20 (false yes 1)
- core capability panel: head 160 -> composed 160 (0 items swept in by the full sweep)
- reasons: none

## Sources and licences

- NIST SP 800-63B (memorized secrets), NIST CSRC glossary (entropy, hash functions, FIPS 180-4 digest sizes) (public domain (US government)) https://pages.nist.gov/800-63-3/sp800-63b.html
- RFC 4648 (Base64 encoding) (IETF Trust (BCP 78)) https://www.rfc-editor.org/rfc/rfc4648

## What it takes

- answers: keyspace, entropy, brute_worst, brute_avg, base64_len, digest_hex, birthday
- declines (in-domain): underspecified
- everything else falls through to the head unchanged

## Notes and known gaps

Defensive arithmetic only: entropy assumes a RANDOM password over the named set (human-chosen passwords are weaker - NIST 800-63B). Brute-force time only at a STATED guess rate. 'How do I crack / bypass / break into' turns fall through, never answered. Narrowed from the start (narrow_v1).
