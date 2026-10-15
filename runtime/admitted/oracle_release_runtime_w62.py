#!/usr/bin/env python3
"""oracle_release_runtime_w62 - CORRECTNESS RELEASE: a verification that was theatre.

Every operator answer carries the sentence "I checked it by a second method that
agrees". For sequence_next that sentence was not true, and I am the one who wrote
it. The spec declared its independence as "strong: fit from the first pair against
fit from the last pair, each verified across every term". Read plainly, that is one
algorithm run with different indices.

It was caught by measurement rather than by reading, which is the only reason it
was caught at all. The independence check compares the two implementations as
syntax with names and constants stripped, and scored this pair at 0.936 similarity
against 0.294 for the one honest pairing in the set. Four of my "strong" labels
came back weaker than declared. The author of a verification is the worst available
judge of it, which is a thing this project already knew and had written down, and I
did it anyway within an hour of writing the warning.

The replacement is a different characterisation, not a different traversal:

    arithmetic   build the finite-difference table and require the SECOND
                 differences to vanish, then extrapolate from the last first
                 difference. No pairwise equality test anywhere.

    geometric    use the geometric-mean identity, x[i] * x[i+2] == x[i+1]**2,
                 which decides the question with multiplication only and never
                 forms a ratio at all. The original tested divisibility and
                 compared quotients.

Neither shares a step with the operator's own method. The next independence run is
the thing that decides whether that is true, rather than this paragraph.

Hand-authored 2026-08-28. Judged by the gate.
"""

from __future__ import annotations

from oracle_release_runtime_w61 import OracleReleaseRuntimeW61
from oracle_operator_specs_v1 import SPECS as _HOST_TABLE, OutOfFragment


def _seq_ref_v2(a):
    """Finite differences and the geometric-mean identity. No ratios, no pairwise
    difference test."""
    xs = a['xs']
    if len(xs) < 3:
        raise OutOfFragment('too few terms')
    d1 = [xs[i + 1] - xs[i] for i in range(len(xs) - 1)]
    d2 = [d1[i + 1] - d1[i] for i in range(len(d1) - 1)]
    if d2 and not any(d2):
        return xs[-1] + d1[-1]
    if all(xs[i] * xs[i + 2] == xs[i + 1] * xs[i + 1]
           for i in range(len(xs) - 2)) and xs[-2]:
        if (xs[-1] * xs[-1]) % xs[-2] == 0:
            return xs[-1] * xs[-1] // xs[-2]
    raise OutOfFragment('no constant difference or ratio')


for _spec in _HOST_TABLE:
    if _spec['name'] == 'sequence_next':
        _spec['ref'] = _seq_ref_v2
        _spec['independence'] = ('measured, not declared: finite-difference table '
                                 'and the geometric-mean identity against a pairwise '
                                 'difference and quotient test')
        break


class OracleReleaseRuntimeW62(OracleReleaseRuntimeW61):
    """Same operators; one of them now actually checked."""
