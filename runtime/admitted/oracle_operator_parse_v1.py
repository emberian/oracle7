#!/usr/bin/env python3
"""PARSE BY ELIMINATION - readings as potentials, ablated against declared bounds.

The worst defect of 2026-08-28 was not a wrong computation. Two independent
implementations of `combinations` both returned 792 for "how many ways to choose 12
from 5", which is an impossible question, and they agreed because the PARSE handed
both of them a different and possible problem. Verification cannot reach that.
Checking an answer two ways says nothing about whether the question was read
correctly.

The cause, stated precisely, was an unrecorded choice among readings. The surface
admits more than one assignment of its numbers to the operator's arguments, the
code silently collapsed to one by a number-order heuristic, and the choice left no
trace, so nothing downstream could question it. Worse, the heuristic reached for
the reading that still computed, which is exactly backwards: the ability to produce
an answer was doing the work that evidence should have done.

Ben's reading of this, and it is a better one than mine: parsing is representation
ablated against its potentials. That makes it the same move as everything else here
rather than a special problem. The candidate readings are the potentials. The
surface cues and the operator's own declared fragment are the ablations. What
survives is the parse.

    one survivor    that is the reading, and the eliminations are its warrant
    many survivors  genuine ambiguity, DETECTED rather than silently resolved
    zero survivors  decline, naming the constraint that killed the last one

It needs no second method. Unlike the fn/ref pairing, elimination certifies itself:
the trace shows what died and what killed it, and a reader can check that.

Note what does most of the work. The operator's DECLARED BOUNDS are the strongest
eliminator, stronger than any syntactic cue, because a fragment that knows what it
cannot do can rule out readings on that basis alone. The discipline of making every
operator state its own frontier, which was built for honest refusal, turns out to
be the thing that makes parsing decidable. That was not the intention.
"""

from __future__ import annotations

import re

from oracle_operator_specs_v1 import NotOurs, OutOfFragment


class Ambiguous(OutOfFragment):
    """More than one reading survived. Say so; do not pick a favourite.

    Subclasses OutOfFragment so the existing host declines on it with no change to
    the host at all, which is the point: this is a spec-level discipline and it
    fits the machinery that is already there.
    """


class Reading:
    """One candidate assignment of a surface to an operator's arguments."""

    __slots__ = ('args', 'because', 'killed_by', 'eliminated')

    def __init__(self, args, because):
        self.args = args
        self.because = because
        self.killed_by = None
        self.eliminated = []

    def __repr__(self):
        state = 'killed by %s' % self.killed_by if self.killed_by else 'survives'
        return '<%s | %s | %s>' % (self.args, self.because, state)


def eliminate(readings, constraints, nothing_here='no reading of that at all'):
    """Ablate the potentials. Returns the single survivor or raises with the reason.

    `constraints` is a list of (name, predicate). A reading is killed by the FIRST
    constraint it fails, and which one is recorded, because "declined" without a
    reason is the thing this project refuses everywhere else.
    """
    if not readings:
        raise NotOurs(nothing_here)

    for r in readings:
        for name, ok in constraints:
            try:
                passed = ok(r.args)
            except Exception:                          # noqa: BLE001
                passed = False
            if not passed:
                r.killed_by = name
                break

    alive = [r for r in readings if r.killed_by is None]

    if len(alive) == 1:
        # carry the whole ablation, not just the winner. A reading that survived is
        # only warranted by what died beside it, and an answer that shows the
        # survivor without the eliminations is asking to be trusted again.
        alive[0].eliminated = [(r.because, r.killed_by) for r in readings
                               if r.killed_by]
        return alive[0]

    if not alive:
        # every reading died; report the one that got furthest, since its
        # constraint is the frontier the question actually ran into
        last = readings[-1]
        raise OutOfFragment(last.killed_by or 'no reading survived')

    raise Ambiguous(
        'that has %d readings I cannot choose between (%s) and nothing in the '
        'sentence or in my own limits rules any of them out'
        % (len(alive), '; '.join(r.because for r in alive[:3])))


# ── readings for the operator that actually failed ───────────────────────────
_FROM = re.compile(r'(\d+)\s+(?:things?\s+|items?\s+)?(?:from|out of|of)\s+(\d+)', re.I)
_CHOOSE_IDIOM = re.compile(r'(\d+)\s*(?:choose|c)\s*(\d+)', re.I)
_NUM = re.compile(r'\d+')


def combination_readings(surface):
    """Every assignment the surface licenses, each with the cue that licenses it."""
    out = []
    m = _CHOOSE_IDIOM.search(surface)
    if m:
        out.append(Reading({'n': int(m.group(1)), 'k': int(m.group(2))},
                           'the "n choose k" idiom puts the total first'))
        return out                       # the idiom is unambiguous; nothing else

    m = _FROM.search(surface)
    if m:
        out.append(Reading({'k': int(m.group(1)), 'n': int(m.group(2))},
                           '"%s from %s" takes the smaller count first'
                           % (m.group(1), m.group(2))))
        return out                       # "from" fixes the order; do not guess past it

    ns = [int(x) for x in _NUM.findall(surface)]
    if len(ns) >= 2:
        a, b = ns[0], ns[1]
        out.append(Reading({'n': a, 'k': b}, 'first number as the total'))
        out.append(Reading({'n': b, 'k': a}, 'second number as the total'))
    return out


def parse_combinations(surface):
    """Enumerate, ablate, and return the survivor with its warrant."""
    want = ('perm' if re.search(r'\bpermutation|arrangement|order matters\b',
                                surface, re.I) else 'comb')
    readings = combination_readings(surface)
    survivor = eliminate(
        readings,
        [('you cannot choose more things than there are',
          lambda a: a['k'] <= a['n']),
         ('I keep this exact and that is past where I will',
          lambda a: a['n'] <= 400),
         ('counts have to be whole and not negative',
          lambda a: a['k'] >= 0 and a['n'] >= 0)],
        nothing_here='no pair of counts here')
    args = dict(survivor.args)
    args['want'] = want
    args['_reading'] = survivor.because
    args['_eliminated'] = list(getattr(survivor, 'eliminated', []))
    return args
