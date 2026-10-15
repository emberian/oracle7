#!/usr/bin/env python3
"""oracle_release_runtime_w59 - THE OPERATOR HOST: one disciplined runtime, many
operators, none of them hand-written as folds.

Every capability so far arrived as its own module, and every defect found in those
modules today lived in the same shared boilerplate rather than in any of their
reasoning. A missing witness record made a turn invisible to the gate. A missing
relevance guard let the deduction fold swallow whole conversations. A self-report
read a file instead of reading itself. A justification fold checked one warrant
field and told a visitor that a properly sourced answer should not be trusted.
Four folds, four instances of the same class of mistake, because each one
reimplemented the parts that are not the interesting part.

So this module holds no capability of its own. It is a HOST. The operators are
declarative specs in oracle_operator_specs_v1, and the host supplies exactly once:

    dispatch      the first spec whose trigger matches and whose parse succeeds
    verification  fn computes the answer, ref recomputes it by a different method,
                  and NOTHING is reported unless the two agree
    decline       a named boundary, in the operator's own words
    passthrough   when the surface is not this operator's business, the chain
                  answers exactly as it would if the host were not installed
    witness       one recording path, so no operator can be invisible to the gate

Adding a capability is now adding a spec, and a spec cannot forget the discipline
because it never implements it.

The verification step is the reason to build it this way rather than as a library
of helpers. An operator that computed and reported would be a faster way to be
wrong. Here the answer has to survive being computed twice by different routes,
and when the two disagree the host says so and withholds, which is a state the
previous hand-written folds had no way to even be in.

Six operators arrive with this host: unit conversion, gcd and lcm, base
conversion, descriptive statistics, sequence continuation, roman numerals. The
count is not the point. The point is that the seventh costs a spec.

Hand-authored 2026-08-28. Judged by the gate.
"""

from __future__ import annotations

from fractions import Fraction

from oracle_release_runtime_w58 import OracleReleaseRuntimeW58
from oracle_operator_specs_v1 import SPECS, NotOurs, OutOfFragment


def _same(a, b):
    """Do two independently computed answers agree? Types must not paper over it."""
    if a is None or b is None:
        return False
    if isinstance(a, str) or isinstance(b, str):
        return str(a).strip().lower() == str(b).strip().lower()
    try:
        return Fraction(a) == Fraction(b)
    except (TypeError, ValueError):
        return str(a) == str(b)


class OracleReleaseRuntimeW59(OracleReleaseRuntimeW58):
    """Runs declarative operators, and reports only what two methods agree on."""

    def _witness_op(self, session_id, surface, spec, steps, status, warrant=None):
        from collections import deque
        hist = getattr(self, '_paths', None)
        if hist is None:
            hist = self._paths = {}
        q = hist.get(session_id)
        if q is None:
            q = hist[session_id] = deque(maxlen=64)
        prev = q[-1].get('turn', 0) if len(q) else 0
        q.append({'turn': prev + 1, 'in_surface': str(surface)[:120],
                  'in_form': [spec['family']],
                  'operator': 'op:%s' % spec['name'],
                  'out_status': status, 'in_terms': [], 'out_terms': [],
                  'relation': {'grounded': [], 'grounded_cited': [],
                               'introduced': [], 'unaccounted': []},
                  'carried_from_prior': [], 'continuity_lexical': False,
                  'continuity': True, 'citations': 0, 'residual': None,
                  'cost_ms': 1.0,
                  'conversion': {'construction': 'VERIFIED_COMPUTATION',
                                 'from': str(surface)[:80],
                                 'to': (steps[-1][:60] if steps else spec['name']),
                                 'produced_by': 'op_%s_w59' % spec['name']},
                  'verified_warrant': warrant})

    def chat(self, text: str, session_id: str = 'default') -> dict:
        s = ' '.join(str(text).strip().split())

        for spec in SPECS:
            if not spec['trigger'].search(s):
                continue
            try:
                args = spec['parse'](s)
            except NotOurs:
                continue                      # not this operator, keep looking
            except OutOfFragment as why:
                return self._decline(session_id, s, spec, why)

            try:
                value, steps = spec['fn'](args)
            except NotOurs:
                continue
            except OutOfFragment as why:
                return self._decline(session_id, s, spec, why)
            except Exception:                 # noqa: BLE001 - a crash is not an answer
                continue

            try:
                check = spec['ref'](args)
            except Exception:                 # noqa: BLE001
                check = None

            if not _same(value, check):
                # The interesting failure. Two methods, one answer each, and they
                # do not match, so the honest report is the disagreement itself.
                self._witness_op(session_id, s, spec, steps, 'withheld')
                return {'status': 'withheld', 'path': 'op:%s:unverified' % spec['name'],
                        'response': ('I worked that out two ways and got two '
                                     'different answers, %s and %s, so one of my '
                                     'methods is wrong and I do not yet know which. '
                                     'I am not going to pick the one I like.'
                                     % (value, check)),
                        'provenance': {'kind': 'computation', 'verified': False,
                                       'operator': spec['name'],
                                       'disagreement': [str(value), str(check)]},
                        'latency_ms': 2}

            body = spec['render'](args, value, steps)
            trace = ' '.join('%s.' % st for st in steps[:6])
            warrant = {'kind': spec['warrant'], 'steps': list(steps)}
            self._witness_op(session_id, s, spec, steps, 'answered', warrant)
            pending = getattr(self, '_pending_conversion', None)
            if pending is None:
                pending = self._pending_conversion = {}
            pending[session_id] = {'construction': 'VERIFIED_COMPUTATION',
                                   'from': s[:80], 'to': str(value)[:60],
                                   'produced_by': 'op_%s_w59' % spec['name']}
            return {'status': 'answered', 'path': 'op:%s' % spec['name'],
                    'response': ('%s %s I checked it by a second method that '
                                 'agrees.' % (body, trace)).strip(),
                    'provenance': {'kind': 'computation', 'verified': True,
                                   'operator': spec['name'],
                                   'family': spec['family'],
                                   'steps': list(steps),
                                   'independence': spec['independence'],
                                   'checked_by': 'independent reimplementation'},
                    'latency_ms': 2}

        return super().chat(s, session_id)

    def _decline(self, session_id, surface, spec, why):
        self._witness_op(session_id, surface, spec, [], 'withheld')
        return {'status': 'withheld',
                'path': 'op:%s:out_of_fragment' % spec['name'],
                'response': ('%s. What I do handle is %s. I could give you a '
                             'plausible looking answer, but I would have no way to '
                             'check it, so I will not.'
                             % (str(why).rstrip('.'), spec['fragment'])),
                'provenance': {'kind': 'computation', 'verified': False,
                               'operator': spec['name'], 'reason': str(why),
                               'fragment': spec['fragment']},
                'latency_ms': 1}
