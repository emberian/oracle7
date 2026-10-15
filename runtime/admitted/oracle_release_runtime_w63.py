#!/usr/bin/env python3
"""oracle_release_runtime_w63 - CORRECTNESS RELEASE: the reading now carries a warrant too.

Every answer in this system carries a warrant except one link, and it is the link
that produced the worst defect of the day. The computation was checked two ways.
The reading of the question was not checked at all.

"How many ways to choose 12 from 5" came back as 792. Two independent
implementations agreed, because both were handed a different and possible problem
by a parser that silently picked, out of the readings the surface admits, the one
that still computed. The ability to produce an answer was doing the work that
evidence should have been doing.

This replaces that parser with elimination. The readings are enumerated, the
surface cues and the operator's own declared bounds ablate them, and what survives
is the parse. The trace of what died and what killed it becomes the reading's
warrant, so a reader can check the interpretation the same way they can already
check the arithmetic.

Three outcomes instead of one, which is the whole of the fix:

    one survivor    the reading, with its eliminations recorded
    many survivors  ambiguity, reported rather than resolved by preference
    zero survivors  a decline naming the constraint that killed the last reading

"Choose 12 from 5" now resolves correctly and for the right reason. The cue "X from
Y" fixes the smaller count first, the operator's own bound that you cannot choose
more things than there are kills that reading, nothing survives, and it declines.
The reading it used to take was never licensed by the sentence. It was licensed by
being computable.

No host change. Ambiguous subclasses OutOfFragment, so the existing decline path
carries it, which is the evidence that this belongs to the machinery rather than
being bolted beside it.

Hand-authored 2026-08-28. Judged by the gate.
"""

from __future__ import annotations

from oracle_release_runtime_w62 import OracleReleaseRuntimeW62
from oracle_operator_specs_v1 import SPECS as _HOST_TABLE
from oracle_operator_parse_v1 import parse_combinations

def _render_with_reading(a, v, s):
    """The answer says how the question was read, and what that ruled out."""
    head = ('There are %s %s.'
            % (v, 'arrangements' if a.get('want') == 'perm' else 'combinations'))
    why = a.get('_reading')
    if not why:
        return head
    out = '%s I read that as %d from %d, because %s.' % (head, a['k'], a['n'], why)
    for because, killed in (a.get('_eliminated') or [])[:2]:
        out += ' I ruled out reading it as %s, because %s.' % (because, killed)
    return out


for _spec in _HOST_TABLE:
    if _spec['name'] == 'combinations':
        _spec['parse'] = parse_combinations
        _spec['render'] = _render_with_reading
        _spec['fragment'] = ('choosing k from n, both whole, n up to 400, and I say '
                             'which reading of your sentence I used')
        break


class OracleReleaseRuntimeW63(OracleReleaseRuntimeW62):
    """Same operators; the reading of the question is now evidence, not a guess."""
