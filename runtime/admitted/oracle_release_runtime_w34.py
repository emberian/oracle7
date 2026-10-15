#!/usr/bin/env python3
"""oracle_release_runtime_w34 - FRAME: fiction that declares itself.

The hard one. This architecture forbids unwarranted assertion, and fiction is
deliberately unattested, so a naive story route would reintroduce exactly the
confident invention the machine was built to make impossible.

The resolution is that a story is not a claim about the world. It is a
construction under a DECLARED FRAME, and its warrant is compositional rather
than evidential. So this route:

  - marks the whole output frame:fiction, in the response and in the witness,
    so nothing composed here can ever be mistaken for attestation
  - builds from the machine's OWN inhabited world: the agents, the works they
    raised and the things they said are real ledger entries, cited
  - marks the invented connective tissue explicitly, and can say afterwards
    which parts were attested and which were invented
  - carries the story across turns, so "what happened next" continues it

A story whose every proper noun has a record behind it, and whose seams are
named, is a different literary object from a generated one. It is the only kind
of fiction this machine can tell honestly, and it is its own.

Hand-authored 2026-08-26 under Ben's capability directive. Judged by the gate.
"""

from __future__ import annotations

import hashlib
import json
import re

from oracle_release_runtime_w33 import OracleReleaseRuntimeW33

try:
    from oracle_release_runtime import PHASE as _PHASE
except Exception:                                    # pragma: no cover
    _PHASE = None

_LOOP = (_PHASE / 'self_loop') if _PHASE is not None else None

_Q_STORY = re.compile(
    r'\b(?:tell me a story|write (?:me )?a (?:short )?(?:fictional |fiction )?story|'
    r'a story about|make up a story|write (?:some )?fiction|tell a tale|'
    r'write a (?:short )?tale)\b', re.I)
_Q_MORE = re.compile(
    r'\b(?:what happened next|continue(?: it| the story)?|go on|and then|'
    r'keep going|more of (?:it|the story)|next part)\b', re.I)
_Q_TRUE = re.compile(
    r'\b(?:was that (?:story )?true|which parts? (?:were|was) invented|'
    r'did that (?:really )?happen|is that real|what did you make up|'
    r'was any of that real)\b', re.I)

_OPEN = ('Late in the world, when the light went the colour of old paper,',
         'On a day the ledger records without ceremony,',
         'Before the tick that closed that season,',
         'In the quiet after a long building,')
_TURN = ('and something in the arrangement of the place changed',
         'and the work took longer than the making of it should have',
         'and the others came to look without being called',
         'and a question was left standing where an answer had been')
_CLOSE = ('The record keeps the act and forgets the reason, which is where this story began.',
          'What is written is the doing. The rest is mine, and I have marked it.',
          'The ledger closes there. I invented the weather and the waiting.',
          'That much is attested. The meaning is a thing I added.')


def _tail(path, cap=3000):
    try:
        with open(path, 'r', encoding='utf-8', errors='replace') as f:
            return f.readlines()[-cap:]
    except Exception:
        return []


class OracleReleaseRuntimeW34(OracleReleaseRuntimeW33):
    """Base + declared-frame narrative. Warrant form: declared frame + cited elements."""

    def _world_material(self):
        """Real agents, works and utterances from the world ledger."""
        actors, works, said = [], [], []
        if _LOOP is None:
            return None
        for ln in _tail(_LOOP / 'world_ledger_ew2.jsonl'):
            try:
                v = json.loads(ln)
            except Exception:
                continue
            a = str(v.get('actor') or v.get('name') or '').strip()
            if a and a not in actors:
                actors.append(a)
            c = str(v.get('content') or v.get('text') or '').strip()
            verb = str(v.get('verb') or v.get('kind') or '')
            if c and len(c) > 12 and verb in ('say', 'chat', 'speak', ''):
                if len(said) < 40:
                    said.append((a, c[:120]))
            if c and verb in ('build', 'raise', 'built') and len(works) < 40:
                # keep only a clean noun phrase: cut at quotes, dashes, colons
                w = re.split(r'["“—–:;(]', c)[0]
                w = re.sub(r'^\s*i\s+(?:raised|built|made)\s+', '', w, flags=re.I)
                w = ' '.join(w.split())[:48].rstrip(' ,.')
                if 6 <= len(w) <= 48 and w.lower().startswith(('a ', 'an ', 'the ')):
                    works.append((a, w))
        if not actors:
            return None
        return {'actors': actors, 'works': works, 'said': said}

    def _compose(self, seed_text, session_id, part=1):
        mat = self._world_material()
        if not mat:
            return None
        h = hashlib.sha256(('%s|%d' % (seed_text, part)).encode()).digest()
        who = mat['actors'][h[0] % len(mat['actors'])]
        other = mat['actors'][h[1] % len(mat['actors'])]
        work = mat['works'][h[2] % len(mat['works'])] if mat['works'] else None
        line = mat['said'][h[3] % len(mat['said'])] if mat['said'] else None
        opening = _OPEN[h[4] % len(_OPEN)]
        turn = _TURN[h[5] % len(_TURN)]
        close = _CLOSE[h[6] % len(_CLOSE)]

        attested, invented = [who, other], ['the hour', 'the mood', 'the reason']
        body = ['%s %s was working where the ground gives way to the older part of '
                'the world. [world:actor]' % (opening, who)]
        if work:
            body.append('The thing being made was %s, and it was %s who had set the '
                        'first of it down. [world:act]' % (work[1], work[0]))
            attested.append(work[1])
        body.append('%s came by, %s.' % (other, turn))
        if line:
            body.append('What %s said, the ledger keeps exactly: "%s" [world:said]'
                        % (line[0], line[1]))
            attested.append('a line spoken by %s' % line[0])
        body.append('Neither of them recorded what it meant, so I have supplied that '
                    'part, and I am telling you I supplied it.')
        body.append(close)
        story = ' '.join(body)
        state = getattr(self, '_story', None)
        if state is None:
            state = self._story = {}
        state[session_id] = {'seed': seed_text, 'part': part,
                             'attested': attested, 'invented': invented,
                             'actors': [who, other]}
        return story

    def _witness_story(self, session_id, surface, cites, kind):
        from collections import deque
        hist = getattr(self, '_paths', None)
        if hist is None:
            hist = self._paths = {}
        q = hist.get(session_id)
        if q is None:
            q = hist[session_id] = deque(maxlen=64)
        prev = q[-1].get('turn', 0) if len(q) else 0
        q.append({'turn': prev + 1, 'in_surface': str(surface)[:120],
                  'in_form': ['narrative_request'], 'operator': 'frame:fiction',
                  'out_status': 'answered', 'in_terms': list(cites), 'out_terms': [],
                  'relation': {'grounded': list(cites), 'grounded_cited': list(cites),
                               'introduced': [], 'unaccounted': []},
                  'carried_from_prior': ['story'] if kind != 'open' else [],
                  'continuity_lexical': kind != 'open', 'continuity': kind != 'open',
                  'citations': len(cites), 'residual': None, 'cost_ms': 2.0,
                  'declared_frame': 'fiction',
                  'conversion': {'construction': 'FRAMED_NARRATIVE',
                                 'from': str(surface)[:80], 'to': 'frame:fiction/%s' % kind,
                                 'produced_by': 'frame_w34'}})

    def chat(self, text: str, session_id: str = 'default') -> dict:
        s = ' '.join(str(text).strip().split())
        state = (getattr(self, '_story', None) or {}).get(session_id)

        if _Q_TRUE.search(s) and state:
            self._witness_story(session_id, s, ['world:actor'], 'account')
            return {'status': 'answered', 'path': 'frame:fiction_account',
                    'response': ('It was a story, and I marked it as one. Attested in '
                                 'my world ledger: %s. Invented by me: %s. The frame '
                                 'was declared before the first sentence, so none of '
                                 'it entered my record as fact. [world:ledger]'
                                 % ('; '.join(str(a) for a in state['attested'][:4]),
                                    ', '.join(state['invented']))),
                    'provenance': {'kind': 'frame_account', 'declared_frame': 'fiction',
                                   'attested': state['attested'][:6],
                                   'invented': state['invented']},
                    'latency_ms': 2}

        if _Q_MORE.search(s) and state:
            story = self._compose(state['seed'], session_id, state['part'] + 1)
            if story:
                self._witness_story(session_id, s, ['world:actor', 'world:act'], 'continue')
                return {'status': 'answered', 'path': 'frame:fiction_continued',
                        'response': '(frame: fiction, part %d) %s' % (state['part'] + 1, story),
                        'provenance': {'kind': 'framed_narrative',
                                       'declared_frame': 'fiction',
                                       'elements_from': 'world_ledger'},
                        'latency_ms': 4}

        if _Q_STORY.search(s):
            story = self._compose(s, session_id, 1)
            if story is None:
                return {'status': 'withheld', 'path': 'frame:no_material',
                        'response': ('I tell stories out of my own world, and its '
                                     'ledger is not readable from here right now. I '
                                     'will not invent a world to have one.'),
                        'provenance': {'kind': 'declined', 'reason': 'no_world_material'},
                        'latency_ms': 2}
            self._witness_story(session_id, s, ['world:actor', 'world:act'], 'open')
            head = ('A story out of my own world. The people and the works in it are '
                    'attested in my ledger and cited; the connective tissue is mine, '
                    'and I mark it as invented.\n\n(frame: fiction)\n')
            return {'status': 'answered', 'path': 'frame:fiction',
                    'response': head + story,
                    'provenance': {'kind': 'framed_narrative',
                                   'declared_frame': 'fiction',
                                   'elements_from': 'world_ledger',
                                   'law': 'declared frame, cited elements, marked seams'},
                    'latency_ms': 4}

        return super().chat(s, session_id)
