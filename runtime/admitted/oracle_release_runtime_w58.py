#!/usr/bin/env python3
"""oracle_release_runtime_w58 - JUSTIFICATION: why did you do that, answered from
the record rather than from a story about the record.

Found by the salience pass over the held-out residue, not by me guessing. Among
the turns the machine could not answer was "Why did you choose that language?",
falling to act:clarify. It had just written a python program, recorded that it
wrote a python program, recorded which fold wrote it and what the execution
printed, and then could not say why python.

That gap matters more than its size. The entire claim of this architecture is
that every answer carries a warrant which can be inspected. If the warrant can
only be inspected by reading a JSON file on a server, it is not a conversational
property, it is a filing system. A machine that can be asked "how did you get
that" and answers from its own witness record is doing the thing the design is
for.

So this fold answers three questions about the PREVIOUS turn, and only from what
the record actually holds:

    why did you choose that      the choice, and what determined it
    how did you get that         the warrant: derivation, computation, execution
    what did you just do         the operator and the construction it built

The discipline, which is the whole point: it reports the reason ONLY when the
record supports it. If you did not name a language, the record shows the request
with no language in it and the output in python, so "you did not name one and
python is my default" is a reading of the record. If you did name one, the reason
is that you asked. And when the record holds no reason at all, it says exactly
that, because the failure mode here is not silence, it is a machine that
confabulates a plausible motive for its own behaviour. That is the one thing this
fold must never do.

It also declines to speak when there is no previous turn, and hands back anything
that is not about the previous turn, so it cannot capture a conversation the way
the deduction fold did before w56.

Hand-authored 2026-08-28. Judged by the gate.
"""

from __future__ import annotations

import re

from oracle_release_runtime_w57 import OracleReleaseRuntimeW57

_WHY_CHOICE = re.compile(
    r'\bwhy\s+(?:did|do)\s+you\s+(?:choose|pick|use|write|go with)\b'
    r'|\bwhy\s+that\s+(?:language|one|approach|way)\b'
    r'|\bwhat\s+made\s+you\s+(?:choose|pick|use)\b', re.I)
_HOW_GOT = re.compile(
    r'\bhow\s+(?:did|do)\s+you\s+(?:get|know|work(?:ed)?\s+that\s+out|arrive|compute|'
    r'calculate|check)\b|\bhow\s+was\s+that\s+(?:checked|verified)\b'
    r'|\bshow\s+(?:me\s+)?(?:your|the)\s+(?:work|steps|working)\b', re.I)
_WHAT_DID = re.compile(
    r'\bwhat\s+did\s+you\s+just\s+do\b|\bwhat\s+(?:route|operator)\s+was\s+that\b'
    r'|\bhow\s+did\s+you\s+answer\s+that\b', re.I)

_LANGS = ('python', 'javascript', 'go', 'bash', 'sql', 'c', 'rust', 'java',
          'ruby', 'typescript')
_WARRANT_NAME = {
    'test_execution': 'I ran it on this machine and compared the output',
    'deduction': 'I derived it, and each step names the rule that licensed it',
    'algebra': 'I solved it and then checked the answer by substituting it back',
    'computation': 'I computed it and kept the trace',
    'citation': 'I cited the source it came from',
    'differential_execution': 'I computed the expected result a second way and '
                              'only answered when the two agreed',
}


class OracleReleaseRuntimeW58(OracleReleaseRuntimeW57):
    """Answers about the previous turn, grounded in that turn's witness record."""

    def _prior_turn(self, session_id):
        """The last recorded turn that was not itself one of these questions."""
        hist = getattr(self, '_paths', None) or {}
        q = hist.get(session_id)
        if not q:
            return None
        for entry in reversed(list(q)):
            if str(entry.get('operator', '')).startswith('justify:'):
                continue
            return entry
        return None

    @staticmethod
    def _choice_reason(prior):
        """Why this output, IF the record shows it. Otherwise None."""
        conv = prior.get('conversion') or {}
        made = str(conv.get('to', ''))
        asked = str(conv.get('from', '') or prior.get('in_surface', '')).lower()
        lang = next((l for l in _LANGS if made.lower().startswith(l + '/')
                     or ('/' + l) in made.lower()), None)
        if not lang:
            return None
        named = next((l for l in _LANGS if re.search(r'\b%s\b' % l, asked)), None)
        if named == lang:
            return ('I used %s because you asked for %s. The record of that turn '
                    'shows your request and the program it produced.' % (lang, named))
        if named is None:
            return ('I used %s because your request did not name a language, and '
                    '%s is what my code fold writes when none is named. That is a '
                    'default, not a judgement that %s was best for the task.'
                    % (lang, lang, lang))
        return ('I used %s although your request mentioned %s. My record shows the '
                'mismatch and does not record a reason for it, so I am telling you '
                'the mismatch rather than explaining it away.' % (lang, named))

    def _justify(self, kind, prior):
        conv = prior.get('conversion') or {}
        vw = prior.get('verified_warrant') or {}
        op = str(prior.get('operator', '') or 'an unrecorded route')
        by = str(conv.get('produced_by', '') or 'an unrecorded fold')

        if kind == 'why_choice':
            reason = self._choice_reason(prior)
            if reason:
                return reason + ' [self:witness]'
            return ('My record for that turn shows the route (%s) and what it built '
                    '(%s), but it does not record a reason for the choice you are '
                    'asking about. I am not going to invent one. [self:witness]'
                    % (op, conv.get('to') or 'no construction recorded'))

        if kind == 'how_got':
            if not vw.get('kind'):
                # Citation is a warrant too, and it lives in a different field. The
                # first version of this fold read only verified_warrant and told a
                # visitor that a properly sourced encyclopedic answer "should not
                # have been presented as settled", which is a machine libelling its
                # own good work. Check every warrant the record can carry.
                cited = list((prior.get('relation') or {}).get('grounded_cited') or [])
                if cited or prior.get('citations'):
                    return ('I did not compute that one, I quoted it. The record for '
                            'that turn carries %d citation%s%s, so the warrant is the '
                            'source rather than a derivation I can replay. '
                            '[self:witness]'
                            % (prior.get('citations') or len(cited),
                               '' if (prior.get('citations') or len(cited)) == 1 else 's',
                               ' covering %s' % ', '.join(str(c) for c in cited[:4])
                               if cited else ''))
                return ('That answer came through %s, and my record for it holds no '
                        'warrant of any kind, neither a citation nor a check I can '
                        'replay. I should not have presented it as settled. '
                        '[self:witness]' % op)
            head = _WARRANT_NAME.get(str(vw['kind']),
                                     'the warrant recorded is of kind %s' % vw['kind'])
            steps = [str(s) for s in (vw.get('steps') or [])]
            if steps:
                return ('%s. The recorded steps were: %s. [self:witness]'
                        % (head, '; then '.join(steps[:6])))
            return '%s, though the record kept no individual steps. [self:witness]' % head

        return ('That turn went through %s, produced by %s. It built a %s, from "%s" '
                'to "%s"%s. [self:witness]'
                % (op, by, conv.get('construction') or 'result',
                   str(conv.get('from', ''))[:60],
                   str(conv.get('to', ''))[:60],
                   ', warranted by %s' % vw['kind'] if vw.get('kind') else
                   ', with no warrant recorded'))

    def chat(self, text: str, session_id: str = 'default') -> dict:
        s = ' '.join(str(text).strip().split())
        if _WHY_CHOICE.search(s):
            kind = 'why_choice'
        elif _HOW_GOT.search(s):
            kind = 'how_got'
        elif _WHAT_DID.search(s):
            kind = 'what_did'
        else:
            return super().chat(s, session_id)

        prior = self._prior_turn(session_id)
        if prior is None:
            return {'status': 'withheld', 'path': 'justify:no_prior_turn',
                    'response': ('You are asking about a previous answer and this is '
                                 'the first turn I have recorded in this session, so '
                                 'there is nothing for me to read.'),
                    'provenance': {'kind': 'justification', 'prior_turn': None},
                    'latency_ms': 1}

        body = self._justify(kind, prior)
        from collections import deque
        hist = getattr(self, '_paths', None)
        if hist is None:
            hist = self._paths = {}
        q = hist.get(session_id)
        if q is None:
            q = hist[session_id] = deque(maxlen=64)
        prev = q[-1].get('turn', 0) if len(q) else 0
        q.append({'turn': prev + 1, 'in_surface': s[:120],
                  'in_form': ['question_about_prior_turn'],
                  'operator': 'justify:' + kind,
                  'out_status': 'answered', 'in_terms': [], 'out_terms': [],
                  'relation': {'grounded': [], 'grounded_cited': [],
                               'introduced': [], 'unaccounted': []},
                  'carried_from_prior': ['witness_record'],
                  'continuity_lexical': True, 'continuity': True, 'citations': 1,
                  'residual': None, 'cost_ms': 1.0,
                  'conversion': {'construction': 'ACCOUNT_OF_PRIOR_TURN',
                                 'from': s[:60],
                                 'to': str(prior.get('operator', ''))[:60],
                                 'produced_by': 'justify_w58'},
                  'verified_warrant': {'kind': 'self_citation',
                                       'steps': ['read the witness record of turn %s'
                                                 % prior.get('turn')]}})
        return {'status': 'answered', 'path': 'justify:' + kind,
                'response': body,
                'provenance': {'kind': 'justification', 'read_turn': prior.get('turn'),
                               'prior_operator': prior.get('operator'),
                               'source': 'witness_record'},
                'latency_ms': 2}
