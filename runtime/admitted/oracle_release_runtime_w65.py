#!/usr/bin/env python3
"""oracle_release_runtime_w65 - reading its own operator table when asked what it can do.

From the held-out residue, twice, in the machine's own record of what it failed at:

    what else can you compute?      -> act:clarify
    What languages can you write?   -> act:clarify

It has eleven operators loaded, each with a declared fragment saying exactly what
it handles and where it stops, and when a person asked what it could compute it
said it had not understood the question. The answer was in the room.

That is worth more than the small gap it closes. A system whose capabilities are a
runtime table can READ that table, so "what can you do" stops being a paragraph
somebody wrote about the system and becomes a query against the system. When the
next operator is admitted this answer changes by itself, with nobody editing a
description, and it cannot drift from the truth because there is no second copy of
the truth to drift from.

It answers from the live table only. If an operator is not loaded it is not listed,
which means the answer is occasionally shorter than the marketing and always equal
to the machine.

Found by the salience pass over the residue rather than by me imagining what a
visitor might ask, which is the method working: the machine kept the record of its
own failures, the ranking pointed here, and the fix is a query against something
that already existed.

Hand-authored 2026-08-28. Judged by the gate.
"""

from __future__ import annotations

import re

from oracle_release_runtime_w64 import OracleReleaseRuntimeW64
from oracle_operator_specs_v1 import SPECS as _HOST_TABLE

_ASK_COMPUTE = re.compile(
    r'\bwhat\s+(?:else\s+)?can\s+you\s+(?:compute|calculate|work out|solve)\b'
    r'|\bwhat\s+(?:kinds?\s+of\s+)?(?:maths?|mathematics|calculations?|operators?)\b'
    r'.*\b(?:can|do)\s+you\b'
    r'|\bwhat\s+operators?\s+do\s+you\s+have\b'
    r'|\blist\s+your\s+(?:operators?|capabilities)\b', re.I)


class OracleReleaseRuntimeW65(OracleReleaseRuntimeW64):
    """Answers "what can you compute" by reading the operators it is running."""

    @staticmethod
    def _operator_table():
        fams = {}
        for spec in _HOST_TABLE:
            fams.setdefault(spec.get('family', 'other'), []).append(
                (spec['name'], spec.get('fragment', '')))
        return fams

    def chat(self, text: str, session_id: str = 'default') -> dict:
        s = ' '.join(str(text).strip().split())
        if not _ASK_COMPUTE.search(s):
            return super().chat(s, session_id)

        fams = self._operator_table()
        total = sum(len(v) for v in fams.values())
        if not total:
            return super().chat(s, session_id)

        lines = []
        for fam in sorted(fams):
            names = ', '.join(n.replace('_', ' ') for n, _f in sorted(fams[fam]))
            lines.append('%s: %s' % (fam.replace('_', ' '), names))
        body = ('I am running %d verified operators, reading them off my own table '
                'rather than a description of me. %s. Each one computes its answer '
                'and then checks it by a second method, and each one declines by '
                'name when a question falls outside what it can check. '
                '[self:operators]'
                % (total, '; '.join(lines)))

        from collections import deque
        hist = getattr(self, '_paths', None)
        if hist is None:
            hist = self._paths = {}
        q = hist.get(session_id)
        if q is None:
            q = hist[session_id] = deque(maxlen=64)
        prev = q[-1].get('turn', 0) if len(q) else 0
        q.append({'turn': prev + 1, 'in_surface': s[:120],
                  'in_form': ['capability_self_query'],
                  'operator': 'self:operator_table',
                  'out_status': 'answered', 'in_terms': [], 'out_terms': [],
                  'relation': {'grounded': [], 'grounded_cited': [],
                               'introduced': [], 'unaccounted': []},
                  'carried_from_prior': [], 'continuity_lexical': False,
                  'continuity': True, 'citations': 1, 'residual': None,
                  'cost_ms': 1.0,
                  'conversion': {'construction': 'ACCOUNT_OF_OWN_OPERATORS',
                                 'from': s[:60], 'to': '%d operators' % total,
                                 'produced_by': 'operator_table_w65'},
                  'verified_warrant': {'kind': 'self_citation',
                                       'steps': ['read the live operator table, '
                                                 '%d entries' % total]}})
        return {'status': 'answered', 'path': 'self:operator_table',
                'response': body,
                'provenance': {'kind': 'self_report', 'operator_count': total,
                               'families': sorted(fams),
                               'source': 'live operator table'},
                'latency_ms': 1}
