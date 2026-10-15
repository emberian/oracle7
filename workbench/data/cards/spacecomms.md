# Oracle7 Delay-Tolerant Networking & Space Communications (#95, tier B)

**id** `spacecomms` - organ `organ_spacecomms_v1.SpaceCommsOrgan` composed in front of the frozen head `oracle_release_runtime_w363`.

## Verdict

- decision: **ADMIT** (gate v2)
- held-out domain: specialist 36/36 (false yes 0) vs head 0/36 (false yes 2)
- core capability panel: head 160 -> composed 160 (0 items swept in by the full sweep)
- reasons: none

## Sources and licences

- Exact constants: c = 299,792,458 m/s (SI), 1 AU = 149,597,870,700 m (IAU 2012 Resolution B2) (public (BIPM / IAU)) https://www.iau.org/static/resolutions/IAU2012_English.pdf
- Free-space path loss (Friis) as used in NASA DSN link design (DSN Telecommunications Link Design Handbook 810-005) (public domain (NASA/JPL)) https://deepspace.jpl.nasa.gov/dsndocs/810-005/
- Delay-tolerant networking bundle protocol context: IETF RFC 9171 (IETF Trust) https://www.rfc-editor.org/rfc/rfc9171

## What it takes

- answers: fspl, transfer_time, bits_in_flight, round_trip, light_time
- declines (in-domain): underspecified
- everything else falls through to the head unchanged

## Notes and known gaps

Distances between bodies are never assumed (they change as the planets move); a question naming only two bodies is declined. MB/GB are bytes and Mb/Gb bits, read from the original case. Transfer times exclude protocol overhead, said so.
