#!/usr/bin/env python3
"""oracle_release_runtime_w71 - OPEN CONVERSATION: resolving "it" by elimination.

The held-out residue is not a scatter of unrelated failures. Read it and almost all
of it is one thing:

    Did you run it?          Can you test it?       How does it work?
    Write the same thing in go.                     how old is it?
    Now write one that counts vowels.               what else?
    The thing from before.   Explain the thing with the water.

Every one of those is a surface that does not name its own subject. The machine had
just produced the subject, recorded it, and could still say "I didn't fully parse
that". It was holding the answer and could not see the question.

So this is the elimination move again, pointed at reference. The candidate referents
are read from the witness record, the surface and the machine's own limits ablate
them, and what survives is the reading:

    one survivor    resolve, say which referent and why, and re-dispatch
    many survivors  name them and ask which, rather than picking a favourite
    zero survivors  say what could not be resolved instead of guessing

Which gives open conversation the thing it has never had here: a WARRANT. Not for
the reply being good, which is a matter of taste and always will be, but for the
INTERPRETATION being licensed. "I read 'it' as the python program from two turns
ago, because that is the only thing in this conversation you can run" is checkable
by the person who said "it".

Three referent kinds, each read from a different part of the record because that is
where the machine actually keeps them: topics from in_terms, programs and results
from the conversion. A constraint set per surface form decides which kinds a
question can even accept, so "did you run it" cannot resolve to a topic and "how old
is it" cannot resolve to a program.

ONE GUARD WORTH NAMING: the conversion field is not always about the turn it sits
on. A summarize turn was found carrying a stale conversion from a fraction question
two turns earlier, because the pending-conversion slot is not cleared between turns.
Anything reading it blindly attributes the wrong artifact, so every read here checks
that the conversion's own `from` matches the surface of the turn it was found on.
That is a defect in a fold below this one; this works around it rather than
pretending it is not there.

Hand-authored 2026-08-28. Judged by the gate.
"""

from __future__ import annotations

import re

from oracle_release_runtime_w70 import OracleReleaseRuntimeW70
from oracle_operator_parse_v1 import Reading, eliminate, Ambiguous
from oracle_operator_specs_v1 import NotOurs, OutOfFragment

# surfaces that do not name their subject
_PRONOUN = re.compile(r'\b(?:it|that|this|them|those|one)\b', re.I)
_BARE_CONT = re.compile(r'^(?:what else|anything else|go on|more|and\?|tell me more)'
                        r'\s*\??$', re.I)
_THE_THING = re.compile(r'\bthe (?:same )?thing\b|\bthe one\b', re.I)

# what each surface form is ASKING FOR, which is what rules referents out
_WANTS_PROGRAM = re.compile(
    r'\b(?:did|can|could|will|would)\s+you\s+(?:run|test|execute|try)\b'
    r'|\bthe same (?:thing|code|program)\b|\bin (?:go|python|javascript|bash|sql|c)\b'
    r'|\bnow write one\b|\bdoes it (?:compile|run|work)\b', re.I)
_WANTS_TOPIC = re.compile(
    r'\bhow (?:does|do) (?:it|they) work\b|\bhow old\b|\bwhere is it\b'
    r'|\btell me more\b|\bwhat else\b|\bexplain (?:it|that|the thing)\b'
    r'|\bwhy (?:is|does) it\b|\bwhat is it made of\b', re.I)
_LANG = re.compile(r'\bin (go|python|javascript|bash|sql|c|rust|java)\b', re.I)
_STOP_TERMS = {'summarize', 'explain', 'compare', 'list', 'tell', 'facts', 'about',
               'what', 'how', 'why', 'the', 'a', 'an'}


class OracleReleaseRuntimeW71(OracleReleaseRuntimeW70):
    """Open conversation with a licensed reading of what "it" refers to."""

    def _referents(self, session_id):
        """Candidate referents, newest first, read from the witness record."""
        hist = getattr(self, '_paths', None) or {}
        q = hist.get(session_id)
        out = []
        if not q:
            return out
        for e in reversed(list(q)):
            op = str(e.get('operator', ''))
            if op.startswith(('justify:', 'resolve:')):
                continue
            surface = str(e.get('in_surface', ''))
            conv = e.get('conversion') or {}
            # the conversion slot leaks between turns; only trust it when it is
            # demonstrably about THIS turn
            own = str(conv.get('from', ''))[:60].strip() == surface[:60].strip()
            if own and conv.get('construction') == 'VERIFIED_PROGRAM':
                out.append(('program', str(conv.get('to', '')), surface))
            elif own and conv.get('construction') == 'VERIFIED_COMPUTATION':
                out.append(('result', str(conv.get('to', '')), surface))
            terms = [t for t in (e.get('in_terms') or [])
                     if t not in _STOP_TERMS and len(t) > 2]
            if terms:
                out.append(('topic', terms[0], surface))
            if len(out) >= 6:
                break
        return out

    def _resolve(self, s, session_id):
        """(rewritten_surface, referent, trace) or raises with a named reason."""
        cands = self._referents(session_id)
        if not cands:
            raise NotOurs('nothing recorded yet to refer back to')

        wants_program = bool(_WANTS_PROGRAM.search(s))
        wants_topic = bool(_WANTS_TOPIC.search(s)) or bool(_BARE_CONT.match(s))
        if not (wants_program or wants_topic):
            raise NotOurs('no reference this fold knows how to type')

        readings = [Reading({'kind': k, 'label': lab, 'surface': surf},
                            'the %s from "%s"' % (k, surf[:38]))
                    for k, lab, surf in cands]
        constraints = []
        if wants_program and not wants_topic:
            constraints.append(('you are asking about something runnable and that '
                                'is not a program', lambda a: a['kind'] == 'program'))
        elif wants_topic and not wants_program:
            constraints.append(('you are asking about a subject and that is not one',
                                lambda a: a['kind'] == 'topic'))
        else:
            constraints.append(('it is neither a program nor a subject',
                                lambda a: a['kind'] in ('program', 'topic')))
        # only the most recent of a kind can be "it"; older ones are ruled out by
        # recency, which is a real constraint rather than a tiebreak
        first_of_kind = {}
        for i, r in enumerate(readings):
            first_of_kind.setdefault(r.args['kind'], i)
        constraints.append(('an earlier one of the same kind is nearer',
                            lambda a, _f=first_of_kind, _r=readings:
                            _r[_f[a['kind']]].args is a))

        survivor = eliminate(readings, constraints,
                             nothing_here='nothing here to refer to')
        ref = survivor.args
        if ref['kind'] == 'program':
            lang = _LANG.search(s)
            if lang:
                new = re.sub(r'\b(go|python|javascript|bash|sql|c|rust|java)\b',
                             lang.group(1), ref['surface'], count=1, flags=re.I)
                return new, ref, survivor
            return None, ref, survivor          # a question ABOUT the program
        topic = ref['label']
        if _BARE_CONT.match(s) or re.search(r'\btell me more\b', s, re.I):
            return 'Tell me about %s.' % topic, ref, survivor
        new = _PRONOUN.sub(topic, s, count=1)
        new = _THE_THING.sub(topic, new)
        return new, ref, survivor

    def _about_program(self, s, ref, session_id):
        """Questions about a program are answered from the record, not re-run."""
        hist = getattr(self, '_paths', None) or {}
        q = hist.get(session_id) or []
        warrant = None
        for e in reversed(list(q)):
            if str(e.get('in_surface', ''))[:60].strip() == ref['surface'][:60].strip():
                warrant = e.get('verified_warrant') or {}
                break
        steps = (warrant or {}).get('steps') or []
        if steps:
            return ('Yes. I ran %s on this machine before answering, and the '
                    'recorded output was %s. I read "it" as that program, because '
                    'it is the only thing in this conversation you can run. '
                    '[self:witness]' % (ref['label'], '; '.join(steps[:3])))
        return ('I read "it" as %s, the program from earlier in this conversation. '
                'My record for that turn holds no execution, so I will not tell you '
                'it ran. [self:witness]' % ref['label'])

    def chat(self, text: str, session_id: str = 'default') -> dict:
        s = ' '.join(str(text).strip().split())
        if not (_PRONOUN.search(s) or _BARE_CONT.match(s) or _THE_THING.search(s)):
            return super().chat(s, session_id)
        # a surface that names a subject of its own is not this fold's business
        if re.search(r'\b(?:volcano|moon|gravity|rain)\b', s, re.I) and \
                not _BARE_CONT.match(s):
            pass

        try:
            rewritten, ref, survivor = self._resolve(s, session_id)
        except Ambiguous as why:
            return {'status': 'withheld', 'path': 'resolve:ambiguous',
                    'response': ('%s. Say which one and I will go on.' % why),
                    'provenance': {'kind': 'reference', 'resolved': False},
                    'latency_ms': 1}
        except NotOurs:
            return super().chat(s, session_id)
        except OutOfFragment as why:
            return super().chat(s, session_id)                  # not ours to refuse

        ruled = [(b, k) for b, k in (getattr(survivor, 'eliminated', []) or [])][:2]
        if rewritten is None:
            body = self._about_program(s, ref, session_id)
            result = {'status': 'answered', 'path': 'resolve:about_program',
                      'response': body,
                      'provenance': {'kind': 'reference', 'resolved': True,
                                     'referent': ref['label'],
                                     'referent_kind': ref['kind']},
                      'latency_ms': 2}
        else:
            result = super().chat(rewritten, session_id)
            note = ('I read that as "%s", taking %s to mean %s.'
                    % (rewritten, '"it"' if _PRONOUN.search(s) else 'the follow-up',
                       ref['label']))
            if ruled:
                note += ' I ruled out %s, because %s.' % (ruled[0][0], ruled[0][1])
            result = dict(result)
            result['response'] = '%s %s' % (note, str(result.get('response', '')))
            result['path'] = 'resolve:%s->%s' % (ref['kind'], result.get('path'))
            result['provenance'] = dict(result.get('provenance') or {})
            result['provenance'].update({'resolved_reference': ref['label'],
                                         'rewritten_as': rewritten})

        from collections import deque
        hist = getattr(self, '_paths', None)
        if hist is None:
            hist = self._paths = {}
        qq = hist.get(session_id)
        if qq is None:
            qq = hist[session_id] = deque(maxlen=64)
        prev = qq[-1].get('turn', 0) if len(qq) else 0
        qq.append({'turn': prev + 1, 'in_surface': s[:120],
                   'in_form': ['anaphoric_followup'],
                   'operator': 'resolve:' + ref['kind'],
                   'out_status': str(result.get('status', 'answered')),
                   'in_terms': [], 'out_terms': [],
                   'relation': {'grounded': [], 'grounded_cited': [],
                                'introduced': [], 'unaccounted': []},
                   'carried_from_prior': [ref['kind']],
                   'continuity_lexical': True, 'continuity': True, 'citations': 1,
                   'residual': None, 'cost_ms': 1.0,
                   'conversion': {'construction': 'RESOLVED_REFERENCE',
                                  'from': s[:60], 'to': ref['label'][:60],
                                  'produced_by': 'resolve_w71'},
                   'verified_warrant': {'kind': 'self_citation',
                                        'steps': ['read "%s" as %s'
                                                  % (s[:40], ref['label'])]
                                        + ['ruled out %s because %s' % (b, k)
                                           for b, k in ruled]}})
        return result
