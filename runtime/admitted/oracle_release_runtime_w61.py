#!/usr/bin/env python3
"""oracle_release_runtime_w61 - five more operators, and not one line of new discipline.

This module exists to test a claim rather than to add a capability, though it adds
five. When the operator host was admitted the claim was that a further capability
would cost a spec entry and nothing else. Here is the whole of this runtime's
behaviour:

    it registers five specs into the table the host already iterates

There is no dispatch here, no verification, no refusal handling, no witness
recording, no passthrough logic, and no chat method. All of that lives once in the
host and is inherited unchanged. If the claim had been false, this file would have
had to reimplement some part of it, and the diff is the evidence either way.

The five: combinations and permutations, prime factorisation, days between two
dates, integer square root, and arithmetic on two fractions. Each carries a second
implementation by a genuinely different method, because that is the joint where
this design would rot first if an author wrote the same algorithm twice and called
the agreement a check. Pascal's triangle against a multiplicative formula. A sieve
against trial division. Walking the calendar month by month against a day-number
formula. Binary search against Newton's method.

ONE DEBT, recorded because it is a real design flaw in the host rather than a
detail: the host iterates a module-level SPECS list, so extending the operator set
means appending to that list rather than overriding a method. It works and it is
idempotent, but a host that exposed the table through a hook would be cleaner, and
the next host revision should do that.

Hand-authored 2026-08-28. Judged by the gate.
"""

from __future__ import annotations

from oracle_release_runtime_w59 import OracleReleaseRuntimeW59
from oracle_operator_specs_v1 import SPECS as _HOST_TABLE
from oracle_operator_specs_v2 import NEW_SPECS

_registered = {s['name'] for s in _HOST_TABLE}
for _spec in NEW_SPECS:
    if _spec['name'] not in _registered:
        _HOST_TABLE.append(_spec)
        _registered.add(_spec['name'])


class OracleReleaseRuntimeW61(OracleReleaseRuntimeW59):
    """Eleven operators on the host that was written for six."""

    OPERATOR_COUNT = len(_HOST_TABLE)
