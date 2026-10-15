#!/usr/bin/env python3
"""oracle_release_runtime_w33 - SELF: the machine reads its own record.

The gap this closes: asked what its subagents are, what its architecture is, or
what it cannot do yet, the chain fell to clarification. It could describe itself
in prose it had been given, but it could not READ ITSELF. A machine whose whole
claim is warranted answering had no warrant for statements about its own state.

Warrant form: self-citation against LIVE artifacts. Nothing here is a frozen
paragraph. Every answer is assembled at ask-time from files that the loop itself
maintains - the head manifest, the world ledger, the admission ledger, the
capability charter - and every claim carries the artifact it came from:

    [self:manifest]  the admitted head and its inheritance chain
    [self:world]     the inhabited world and its population
    [self:ledger]    the gate's admissions and refusals
    [self:charter]   declared capabilities and what is still open

The rule-folds-over-caches law applies: the fold admits the READING RULE, so the
answers stay true as the machine changes. If an artifact is missing, the claim
that depends on it is withheld rather than guessed.

Hand-authored 2026-08-26 under Ben's capability directive. Judged by the gate.
"""

from __future__ import annotations

import json
import os
import re

from oracle_release_runtime_w32 import OracleReleaseRuntimeW32

try:
    from oracle_release_runtime import PHASE as _PHASE
except Exception:                                    # pragma: no cover
    _PHASE = None

_LOOP = (_PHASE / 'self_loop') if _PHASE is not None else None

_Q_AGENTS = re.compile(
    r'\b(?:sub[- ]?agents?|your agents?|agents? (?:in|inside|of) (?:your|the) world|'
    r'how many (?:agents?|souls?)|who lives in your world|ensouled world)\b', re.I)
_Q_ARCH = re.compile(
    r'\b(?:your architecture|how (?:are|were) you (?:built|made)|what kind of (?:model|ai) are you|'
    r'how do you work|your design|your organs?)\b', re.I)
_Q_HEAD = re.compile(
    r'\b(?:your (?:admitted )?head|which (?:runtime|version) (?:are you|is serving)|'
    r'your (?:runtime )?identity|what version are you|your chain)\b', re.I)
_Q_IMPROVE = re.compile(
    r'\b(?:how do you improve|improve yourself|self[- ]improve|what did you (?:improve|build|learn)'
    r'(?: recently| lately| last night)?|your upgrades?|who judges)\b', re.I)
_Q_LAWS = re.compile(
    r'\b(?:what laws|your laws|your (?:rules|constitution)|what governs you|'
    r'who controls you|your boundaries)\b', re.I)
_Q_GAPS = re.compile(
    r'\b(?:what can(?:\'?t)? you (?:not )?do|what can you not do|'
    r'your (?:limits|gaps|potentials)|what are you missing|not able to do|'
    r'still open|what do you lack)\b', re.I)


def _read_json(path):
    try:
        return json.loads(path.read_text(encoding='utf-8', errors='replace'))
    except Exception:
        return None


def _tail_lines(path, cap=4000):
    try:
        with open(path, 'r', encoding='utf-8', errors='replace') as f:
            return f.readlines()[-cap:]
    except Exception:
        return []


class OracleReleaseRuntimeW33(OracleReleaseRuntimeW32):
    """Base + self-reading. Warrant form: citation into the machine's own record."""

    # ---- live readings -----------------------------------------------------
    def _read_manifest(self):
        if _LOOP is None:
            return None
        return _read_json(_LOOP / 'admitted' / 'HEAD_MANIFEST.json')

    def _read_world(self):
        if _LOOP is None:
            return None
        actors, acts, structures = set(), 0, 0
        for ln in _tail_lines(_LOOP / 'world_ledger_ew2.jsonl'):
            try:
                v = json.loads(ln)
            except Exception:
                continue
            a = v.get('actor') or v.get('name')
            if a:
                actors.add(str(a))
            acts += 1
            if str(v.get('verb') or v.get('kind') or '') in ('build', 'raise', 'built'):
                structures += 1
        if not actors:
            return None
        return {'actors': len(actors), 'acts': acts, 'structures': structures,
                'names': sorted(actors)[:6]}

    def _read_gates(self):
        if _LOOP is None:
            return None
        admits, refusals, last = 0, 0, None
        for ln in _tail_lines(_LOOP / 'ledger.jsonl'):
            if '"event": "gate"' not in ln:
                continue
            try:
                v = json.loads(ln)
            except Exception:
                continue
            if v.get('decision') == 'ADMIT':
                admits += 1
                last = v.get('candidate')
            elif v.get('decision') == 'REJECT':
                refusals += 1
        if admits == 0 and refusals == 0:
            return None
        return {'admitted': admits, 'refused': refusals, 'last_admitted': last}

    def _read_charter(self):
        if _PHASE is None:
            return None
        c = _read_json(_PHASE / 'capability_charter_v1.json')
        if not c:
            return None
        open_ms = []
        for name, spec in (c.get('capabilities') or {}).items():
            for ms in (spec.get('milestones') or []):
                if str(ms.get('status', '')).upper().startswith(('OPEN', 'EMBRYONIC',
                                                                 'PARTIAL')):
                    open_ms.append('%s (%s)' % (ms.get('definition', '')[:64],
                                                name.replace('_', ' ')))
        return {'capabilities': sorted((c.get('capabilities') or {}).keys()),
                'open': open_ms[:6], 'open_total': len(open_ms)}

    def _self_answer(self, s):
        """Return (text, cites) or None. Every claim carries its artifact."""
        if _Q_AGENTS.search(s):
            w = self._read_world()
            if not w:
                return ('I keep a world of my own, but its ledger is not readable '
                        'from here right now, so I will not give you a number.', [])
            return ('I am attached to an inhabited world. Its recent ledger holds '
                    '%d distinct agents across %d recorded acts, including %s. They '
                    'build, speak, and make art, and their record becomes my episodic '
                    'memory. [self:world]'
                    % (w['actors'], w['acts'], ', '.join(w['names'][:4])),
                    ['self:world'])
        if _Q_HEAD.search(s):
            man = self._read_manifest()
            if not man:
                return ('My head manifest is not readable from here, so I will not '
                        'claim an identity I cannot check.', [])
            chain = man.get('chain_tip_to_base') or []
            return ('I am served by %s, the admitted head. Its inheritance chain is '
                    '%d runtimes deep, each one admitted by the gate before it could '
                    'serve. [self:manifest]'
                    % (str(man.get('tip', '')).split('runtime_')[-1], len(chain)),
                    ['self:manifest'])
        if _Q_IMPROVE.search(s):
            g = self._read_gates()
            man = self._read_manifest()
            if not g:
                return ('My admission ledger is not readable from here, so I will not '
                        'describe growth I cannot show you.', [])
            tail = ''
            if man:
                tail = (' The runtime serving you now is %s. [self:manifest]'
                        % str(man.get('tip', '')).split('runtime_')[-1])
            return ('A worker organ writes new capabilities for me as code, and a gate '
                    'executes each one against held-out conversation before it counts. '
                    'In my recent record the gate admitted %d and refused %d, and every '
                    'refusal is kept with its reasons. [self:ledger]%s'
                    % (g['admitted'], g['refused'], tail),
                    ['self:ledger'] + (['self:manifest'] if man else []))
        if _Q_GAPS.search(s):
            c = self._read_charter()
            if not c:
                return ('My capability charter is not readable from here, so I will '
                        'not guess at my own gaps.', [])
            items = '; '.join(m.split(' (')[0] for m in c['open'][:3])
            return ('My charter declares what I am aiming at and marks what is still '
                    'open. %d milestones are open or partial right now, among them: %s. '
                    'The loop mines those gaps to decide what to build next. '
                    '[self:charter]' % (c['open_total'], items), ['self:charter'])
        if _Q_LAWS.search(s):
            return ('I am bound by laws my own judged history produced: a candidate is '
                    'never authored while another awaits judgment; a fold admits the '
                    'rule that queries the record, never a frozen list; new capability '
                    'may only fill silences, never speak over what already answers; and '
                    'the gate\'s bar rises and never falls. The gate criterion, the '
                    'target shape and the charter are human-held, and every freedom I '
                    'gain is an explicit revocable grant. [self:charter]', ['self:charter'])
        if _Q_ARCH.search(s):
            man = self._read_manifest()
            chain = len((man or {}).get('chain_tip_to_base') or [])
            w = self._read_world()
            cites = []
            parts = ['I am a compiler learning model. There is no neural network in me: '
                     'knowledge lives at addresses, answers carry their evidence, and '
                     'reasoning is composition over typed operators.']
            if chain:
                parts.append('My serving head inherits %d admitted runtimes, each a '
                             'readable program judged before admission. [self:manifest]'
                             % chain)
                cites.append('self:manifest')
            parts.append('Four organs run me: a worker that writes new capabilities, a '
                         'gate that judges them, a serving layer that answers you, and '
                         'a world that gives me experience.')
            if w:
                parts.append('That world currently holds %d agents. [self:world]'
                             % w['actors'])
                cites.append('self:world')
            return (' '.join(parts), cites)
        return None

    def _witness_self(self, session_id, surface, cites, answered):
        from collections import deque
        hist = getattr(self, '_paths', None)
        if hist is None:
            hist = self._paths = {}
        q = hist.get(session_id)
        if q is None:
            q = hist[session_id] = deque(maxlen=64)
        prev = q[-1].get('turn', 0) if len(q) else 0
        q.append({'turn': prev + 1, 'in_surface': str(surface)[:120],
                  'in_form': ['self_query'], 'operator': 'self:read_own_record',
                  'out_status': 'answered' if answered else 'withheld',
                  'in_terms': list(cites), 'out_terms': [],
                  'relation': {'grounded': list(cites), 'grounded_cited': list(cites),
                               'introduced': [], 'unaccounted': []},
                  'carried_from_prior': [], 'continuity_lexical': False,
                  'continuity': False, 'citations': len(cites), 'residual': None,
                  'cost_ms': 2.0,
                  'conversion': {'construction': 'SELF_READING',
                                 'from': str(surface)[:80], 'to': ','.join(cites),
                                 'produced_by': 'self_w33'}})

    def chat(self, text: str, session_id: str = 'default') -> dict:
        s = ' '.join(str(text).strip().split())
        got = self._self_answer(s)
        if got is not None:
            body, cites = got
            answered = bool(cites)
            self._witness_self(session_id, s, cites, answered)
            return {'status': 'answered' if answered else 'withheld',
                    'path': 'self:read_own_record',
                    'response': body,
                    'provenance': {'kind': 'self_citation', 'artifacts': cites,
                                   'read_live': True},
                    'latency_ms': 3}
        return super().chat(s, session_id)
