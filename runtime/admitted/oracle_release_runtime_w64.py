#!/usr/bin/env python3
"""oracle_release_runtime_w64 - CORRECTNESS RELEASE: cutting two shared failure channels.

The coupling test found what the shape metric could not. Two operators had a live
common-mode channel, meaning a single wrong edit would break both implementations
identically, they would agree, and the check would pass while the answer was wrong:

    unit_convert   both sides read the same table of absolute factors, so one
                   mistyped factor is mistyped in both and agreement proves nothing
    days_between   both sides read the same month lengths and the same leap rule

Nine of eleven operators were already clean. These two were not, and the fix is not
to write more careful code. It is to give the second implementation its own DATA,
shaped differently, so that a wrong number in one has no counterpart in the other.

    unit_convert   the reference now composes a CHAIN of step ratios (1 km is 1000
                   m, 1 m is 100 cm) instead of reading absolute factors. Different
                   numbers, different shape, and a typo in a step affects only
                   conversions crossing that step rather than mirroring a typo in
                   an absolute factor.

    days_between   the reference now carries CUMULATIVE days-to-start-of-month,
                   written out rather than summed from lengths, and decides leap
                   years by counting the three divisibility rules arithmetically
                   rather than by evaluating a boolean expression the other side
                   also evaluates.

The claim is falsifiable in the obvious way: rerun the coupling test and the live
channel count must go to zero. If it does not, this file is wrong and the numbers
say so.

Hand-authored 2026-08-28. Judged by the gate.
"""

from __future__ import annotations

from fractions import Fraction

from oracle_release_runtime_w63 import OracleReleaseRuntimeW63
from oracle_operator_specs_v1 import SPECS as _HOST_TABLE, OutOfFragment

# ── independent DATA for the unit reference: step ratios, not absolute factors ──
_STEPS = {
    'length': [('mm', 'cm', Fraction(1, 10)), ('cm', 'm', Fraction(1, 100)),
               ('m', 'km', Fraction(1, 1000)), ('inch', 'cm', Fraction(254, 100)),
               ('inches', 'cm', Fraction(254, 100)),
               ('foot', 'inch', Fraction(12)), ('feet', 'inch', Fraction(12)),
               ('yard', 'feet', Fraction(3)), ('yards', 'feet', Fraction(3)),
               ('mile', 'yard', Fraction(1760)), ('miles', 'yard', Fraction(1760))],
    'mass': [('mg', 'g', Fraction(1, 1000)), ('g', 'kg', Fraction(1, 1000)),
             ('kg', 'tonne', Fraction(1, 1000)),
             ('ounce', 'g', Fraction(28349523125, 1000000000)),
             ('ounces', 'g', Fraction(28349523125, 1000000000)),
             ('pound', 'ounce', Fraction(16)), ('pounds', 'ounce', Fraction(16))],
    'time': [('second', 'minute', Fraction(1, 60)),
             ('seconds', 'minute', Fraction(1, 60)),
             ('minute', 'hour', Fraction(1, 60)),
             ('minutes', 'hour', Fraction(1, 60)),
             ('hour', 'day', Fraction(1, 24)), ('hours', 'day', Fraction(1, 24)),
             ('day', 'week', Fraction(1, 7)), ('days', 'week', Fraction(1, 7))],
}
_SYN = {'seconds': 'second', 'minutes': 'minute', 'hours': 'hour', 'days': 'day',
        'weeks': 'week', 'inches': 'inch', 'feet': 'foot', 'yards': 'yard',
        'miles': 'mile', 'pounds': 'pound', 'ounces': 'ounce'}


def _edges():
    g = {}
    for fam in _STEPS:
        for a, b, r in _STEPS[fam]:
            a, b = _SYN.get(a, a), _SYN.get(b, b)
            g.setdefault(a, {})[b] = r
            g.setdefault(b, {})[a] = Fraction(1) / r
    return g


_G = _edges()


def _unit_ref_chain(a):
    """Walk from src to dst through step ratios. No absolute factor is consulted."""
    src, dst = _SYN.get(a['src'], a['src']), _SYN.get(a['dst'], a['dst'])
    if src == dst:
        return Fraction(a['qty'])
    seen, frontier = {src: Fraction(1)}, [src]
    while frontier:
        nxt = []
        for u in frontier:
            for v, r in _G.get(u, {}).items():
                if v in seen:
                    continue
                seen[v] = seen[u] * r
                nxt.append(v)
        frontier = nxt
    if dst not in seen:
        raise OutOfFragment('no chain of steps from %s to %s' % (src, dst))
    return Fraction(a['qty']) * seen[dst]


# ── independent DATA for the date reference: cumulative days, counted leap rule ──
_CUM = (0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334)


def _leaps_before(y):
    """How many leap years strictly before year y. Counting, not a boolean test."""
    return (y - 1) // 4 - (y - 1) // 100 + (y - 1) // 400


def _is_leap_counted(y):
    """Leap iff the count changes when this year is included. A different question."""
    return _leaps_before(y + 1) - _leaps_before(y) == 1


def _days_ref_cumulative(a):
    def serial(y, m, d):
        days = 365 * (y - 1) + _leaps_before(y)
        days += _CUM[m - 1]
        if m > 2 and _is_leap_counted(y):
            days += 1
        return days + d
    return abs(serial(*a['b']) - serial(*a['a']))


for _spec in _HOST_TABLE:
    if _spec['name'] == 'unit_convert':
        _spec['ref'] = _unit_ref_chain
        _spec['independence'] = ('measured: absolute factors against a composed '
                                 'chain of step ratios, no shared table')
    elif _spec['name'] == 'days_between':
        _spec['ref'] = _days_ref_cumulative
        _spec['independence'] = ('measured: a day-number formula over month lengths '
                                 'against cumulative offsets with a counted leap '
                                 'rule, no shared table')


class OracleReleaseRuntimeW64(OracleReleaseRuntimeW63):
    """Same operators; two shared failure channels cut."""
