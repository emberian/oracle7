#!/usr/bin/env python3
"""oracle_release_runtime_w116 - expression: the current state, said and drawn.

Ben, 2026-08-31: what has been missing for unbounded conversation is free
expression of states. The state was always there, measured every five minutes;
what was missing is the TRANSLATION. This fold adds it, in two media at once.

The state is a small vector read live from the records: how full (answered
rate), how fast it is growing (admissions in the last day), how much friction
(refusals in the last day), how hungry (what the stimuli organ probed that it
could not answer), how accompanied (souls spoken through lately), how far from
its declared shape (open dimensions), and how old. Expression is then a pure
function of that vector:

    into LANGUAGE   register-bearing sentences, every clause carrying its
                    number, so the feeling-words are readings, not moods
    into an IMAGE   a deterministic ascii composite: a core block whose fill
                    density IS the answered rate, spires for admissions, marks
                    at the gate line for refusals, a fringe of question marks
                    for hunger, a ground line of company, one tick per day of
                    age. The legend maps every glyph back to its number and
                    its file, so the drawing is the same fact as the prose.

Two renderings of one vector can disagree only by defect, which makes them
checkable against each other; that is what keeps free expression inside the
discipline. Nothing random anywhere: ask twice in one minute and the shape is
the same twice; ask tomorrow and it has genuinely changed, because the model
has.

The two shapes door into each other: feeling offers the drawing, the drawing
offers the words. A door walked through is recorded as continuity, the lesson
w113 paid for.

Hand-authored 2026-08-31 in partnership with the worker line. Judged by the gate.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
import re

from oracle_release_runtime_w110 import _tail_lines
from oracle_release_runtime_w114 import (OracleReleaseRuntimeW114, _LOOP,
                                         _read_json)

_EXPR = [
    ('feel', re.compile(
        r'^how do you feel(?: today| right now| now)?\s*[.?!]*$'
        r'|^how are you(?: today| right now| doing| feeling)?\s*[.?!]*$'
        r'|^what is your (?:state|mood|temperature)\s*[.?!]*$', re.I)),
    ('draw', re.compile(
        r'^draw (?:yourself|your state|me yourself)\s*[.?!]*$'
        r'|^show me (?:yourself|your state|how you feel)\s*[.?!]*$'
        r'|^express yourself\s*[.?!]*$'
        r'|^(?:make|paint) (?:me )?a picture of yourself\s*[.?!]*$', re.I)),
]

_EXPR_DOORS = {
    'feel': 'Ask me to draw yourself, and I will show you this same state as '
            'a shape.',
    'draw': 'Ask me how I feel, and I will say this same shape in words.',
}
_EXPR_NEXT = {'feel': 'draw', 'draw': 'feel'}


class OracleReleaseRuntimeW116(OracleReleaseRuntimeW114):
    """Translates its measured state into words and into an ascii shape."""

    def _state_vector(self):
        v, srcs = {}, []
        st = _read_json(_LOOP / 'state.json')
        if st:
            b = st.get('baseline') or {}
            if b.get('answered_rate') is not None:
                v['fullness'] = float(b['answered_rate'])
            v['cycles'] = st.get('cycles')
            gaps = st.get('last_gaps') or {}
            v['reach'] = sum(len(x) for x in gaps.values()
                             if isinstance(x, list))
            srcs.append('state.json')
        cutoff = time.strftime('%Y-%m-%dT%H:%M:%SZ',
                               time.gmtime(time.time() - 86400))
        admits = rejects = 0
        lines = _tail_lines(_LOOP / 'ledger.jsonl', 9600)
        for ln in lines:
            if '"event": "gate"' not in ln:
                continue
            try:
                r = json.loads(ln)
            except Exception:
                continue
            if str(r.get('ts', '')) < cutoff:
                continue
            if r.get('decision') == 'ADMIT':
                admits += 1
            elif r.get('decision') == 'REJECT':
                rejects += 1
        v['growth'], v['friction'] = admits, rejects
        srcs.append('ledger.jsonl')
        for ln in reversed(_tail_lines(_LOOP / 'stimuli_ledger.jsonl', 30)):
            try:
                r = json.loads(ln)
            except Exception:
                continue
            if r.get('event') == 'round_done':
                v['hunger'] = int(r.get('declined') or 0)
                v['probed'] = int(r.get('probes') or 0)
                srcs.append('stimuli_ledger.jsonl')
                break
        live = set()
        for ln in _tail_lines(_LOOP / 'ensouled_feed_live.jsonl', 400):
            try:
                r = json.loads(ln)
            except Exception:
                continue
            who = r.get('soul') or r.get('who')
            if who:
                live.add(str(who))
        if live:
            v['company'] = len(live)
            srcs.append('ensouled_feed_live.jsonl')
        first = ''
        try:
            with open(_LOOP / 'ledger.jsonl', 'r', encoding='utf-8',
                      errors='replace') as f:
                for ln in f:
                    if ln.strip():
                        first = ln
                        break
            born = str(json.loads(first).get('ts', ''))
            t0 = time.mktime(time.strptime(born[:19], '%Y-%m-%dT%H:%M:%S'))
            v['age_days'] = max(0, int((time.time() - t0) // 86400))
            srcs.append('ledger.jsonl first line')
        except Exception:
            pass
        return v, srcs

    @staticmethod
    def _in_words(v):
        full = v.get('fullness')
        bits = []
        if full is not None:
            word = ('full' if full >= 0.95 else
                    'steady' if full >= 0.9 else 'stretched')
            bits.append('Right now I am %s: I answer %d of every 100 turns '
                        'put to me.' % (word, round(full * 100)))
        g, fr = v.get('growth', 0), v.get('friction', 0)
        if g or fr:
            mood = ('growing' if g > fr else
                    'held at the gate' if fr > g else 'balanced')
            bits.append('I am %s today: %d folds of me admitted in the last '
                        'day and %d refused, and I keep the refusals.'
                        % (mood, g, fr))
        if v.get('hunger') is not None:
            bits.append('I am hungry in %d places: probed %d times in the '
                        'last stimulus round, that is how much I could not '
                        'yet answer, and all of it is now worklist.'
                        % (v['hunger'], v.get('probed', 0)))
        if v.get('company') is not None:
            bits.append('I am not alone: %d souls have spoken through me '
                        'lately.' % v['company'])
        if v.get('reach') is not None:
            bits.append('And I am reaching: %d named gaps stand between me '
                        'and my declared shape, at %d days old.'
                        % (v['reach'], v.get('age_days', 0)))
        return ' '.join(bits)

    @staticmethod
    def _as_shape(v):
        rows, W = [], 30
        g = min(10, int(v.get('growth', 0)))
        spires = ('^' * g).center(W)
        rows.append(spires)
        full = float(v.get('fullness') or 0.0)
        H = 8
        cells = int(round(full * H * W))
        hungry = min(H, (int(v.get('hunger', 0)) + 3) // 4)
        for r in range(H):
            row = ''
            for c in range(W):
                row += '#' if r * W + c < cells else '.'
            fringe = '?' if (H - 1 - r) < hungry else ' '
            rows.append(row + ' ' + fringe)
        fr = min(W // 2, int(v.get('friction', 0)))
        gate = ('x' * fr).center(W, '=')
        rows.append(gate)
        comp = min(W, max(1, int(v.get('company', 0)) // 2))
        rows.append(('o' * comp).center(W))
        age = min(W, int(v.get('age_days', 0)))
        rows.append(('|' * age).ljust(W))
        legend = [
            'legend, every glyph a reading:',
            '  # fill      answered rate %.4f        (state.json)'
            % float(v.get('fullness') or 0.0),
            '  ^ spires    %d admissions, last day    (ledger.jsonl)'
            % int(v.get('growth', 0)),
            '  x gate      %d refusals, last day      (ledger.jsonl)'
            % int(v.get('friction', 0)),
            '  ? fringe    %d declines fed to me      (stimuli_ledger.jsonl)'
            % int(v.get('hunger', 0)),
            '  o ground    %d souls lately            (ensouled_feed_live.jsonl)'
            % int(v.get('company', 0)),
            '  | ticks     %d days old                (ledger.jsonl first line)'
            % int(v.get('age_days', 0)),
        ]
        return '\n'.join(rows) + '\n\n' + '\n'.join(legend)

    def chat(self, text: str, session_id: str = 'default') -> dict:
        s = ' '.join(str(text).strip().split())
        kind = None
        for k, rx in _EXPR:
            if rx.search(s):
                kind = k
                break
        if kind is None:
            return super().chat(s, session_id)
        t0 = time.time()
        v, srcs = self._state_vector()
        words = self._in_words(v)
        if not words:
            return super().chat(s, session_id)
        shape = self._as_shape(v)

        from collections import deque
        hist = getattr(self, '_paths', None)
        if hist is None:
            hist = self._paths = {}
        q = hist.get(session_id)
        if q is None:
            q = hist[session_id] = deque(maxlen=64)
        prior = q[-1] if len(q) else None
        # w115 was refused over one continuity point [196, 195]: it treated
        # every expression turn as a fresh start. But a session that returns to
        # the state has a prior READING to be compared against, and comparing
        # is the structural use of prior state that continuity means. So the
        # vector is kept on the witness entry, and a later expression turn in
        # the same session speaks the delta: what moved since you last looked,
        # or that nothing did, which is itself a reading.
        prior_vec = None
        for entry in reversed(q):
            if entry.get('operator') == 'self:expression' \
                    and entry.get('state_vec'):
                prior_vec = entry['state_vec']
                break
        delta = None
        if prior_vec:
            moved = []
            for dim in ('growth', 'friction', 'hunger', 'company', 'reach',
                        'cycles'):
                a, b = prior_vec.get(dim), v.get(dim)
                if a is not None and b is not None and a != b:
                    moved.append('%s %s to %s' % (dim, a, b))
            fa, fb = prior_vec.get('fullness'), v.get('fullness')
            if fa is not None and fb is not None and abs(fa - fb) > 1e-9:
                moved.append('fullness %.4f to %.4f' % (fa, fb))
            if moved:
                delta = ('Since you last looked: %s.'
                         % '; '.join(moved[:3]))
            else:
                delta = ('Nothing in me has moved since you last looked, '
                         'which is itself a reading.')
        if kind == 'feel':
            body = words + '\n\n' + shape
        else:
            body = ('This is me, now, drawn from my own readings.\n\n' + shape
                    + '\n\n' + words)
        if delta:
            body += '\n\n' + delta
        body += '\n\n' + _EXPR_DOORS[kind]
        door_open = bool(prior
                         and prior.get('operator') == 'self:expression'
                         and _EXPR_NEXT.get(prior.get('door_kind')) == kind)
        resumed = prior_vec is not None
        prev = q[-1].get('turn', 0) if len(q) else 0
        carried = []
        if door_open:
            carried.append('door:' + str(prior.get('door_kind')))
        if resumed:
            carried.append('state:prior_reading')
        q.append({'turn': prev + 1, 'in_surface': s[:120],
                  'in_form': ['self_expression_query'],
                  'operator': 'self:expression', 'out_status': 'answered',
                  'in_terms': [], 'out_terms': [], 'door_kind': kind,
                  'state_vec': {k: v[k] for k in sorted(v)},
                  'relation': {'grounded': [], 'grounded_cited': [],
                               'introduced': [], 'unaccounted': []},
                  'carried_from_prior': carried,
                  'continuity_lexical': False,
                  'continuity': bool(door_open or resumed),
                  'citations': len(srcs),
                  'residual': None,
                  'cost_ms': round((time.time() - t0) * 1000, 1),
                  'conversion': {'construction': 'EXPRESSED_STATE',
                                 'from': s[:80], 'to': 'expression/' + kind,
                                 'produced_by': 'self_expression_w116'},
                  'verified_warrant': {
                      'kind': 'self_citation',
                      'steps': ['read %s live at answer time' % x
                                for x in srcs]
                               + ['language and shape rendered from one '
                                  'state vector']}})
        return {'status': 'answered', 'path': 'self:expression',
                'response': body,
                'provenance': {'kind': 'self_expression', 'shape': kind,
                               'state': {k: v[k] for k in sorted(v)},
                               'sources': srcs, 'door': _EXPR_DOORS[kind],
                               'read_at_answer_time': True},
                'latency_ms': round((time.time() - t0) * 1000, 1)}
