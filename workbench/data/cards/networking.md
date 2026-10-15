# Oracle7 Networking & Protocols (IPv4 addressing) (#55, tier A)

**id** `networking` - organ `organ_networking_v1.NetworkingOrgan` composed in front of the frozen head `oracle_release_runtime_w503`.

## Verdict

- decision: **ADMIT** (gate v2)
- held-out domain: specialist 67/71 (false yes 1) vs head 2/71 (false yes 2)
- core capability panel: head 160 -> composed 160 (0 items swept in by the full sweep)
- reasons: none

## Sources and licences

- RFC 4632 (CIDR), RFC 1918 (private address space), RFC 3021 (/31 point-to-point), RFC 6598 (shared address space) - IETF (IETF Trust (BCP 78: RFC text may be freely used and implemented)) https://www.rfc-editor.org/rfc/rfc4632
- Python standard library ipaddress module (the arithmetic) (PSF License) https://docs.python.org/3/library/ipaddress.html

## What it takes

- answers: mask, prefix, wildcard, hosts, total, network, broadcast, first, last, range, same_subnet, private, subnet_count, prefix_for_hosts
- declines (in-domain): underspecified, impossible, p2p
- everything else falls through to the head unchanged

## Notes and known gaps

IPv4 only (IPv6 falls through to the head). Exact arithmetic via the ipaddress module; the rule is named in every answer. Declines are structural and recognised (missing prefix/mask, octet > 255, non-contiguous mask, prefix > 32, a larger block inside a smaller one), never guessed. Narrowed from the start (narrow_v1).
