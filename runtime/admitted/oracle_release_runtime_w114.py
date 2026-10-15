#!/usr/bin/env python3
"""oracle_release_runtime_w114 - place in history: reflection generalized to time.

w110 taught the machine to speak of itself and its world in the present tense.
This fold adds the temporal axis as a CATEGORY of reflection rather than a
scatter of phrasings: origin, ancestry, firstness, era, future, and comparison
are six shapes of one question, where does this thing sit in time.

Probed against the serving head 2026-08-31 before authoring. Eleven shapes
died in clarification or withhold and are claimed here. One more, "what is
your history", was being answered with a dictionary line about the word
history under ev:unknown; it is about the self and is taken over deliberately
as a correctness gain.

Everything said is read at answer time from the records that own it: the
ledger's first line is the birth certificate, the manifest chain is the
ancestry, the preserved rejections are the fossil record, the target shape and
charter are the declared future. Where a question reaches past the record (is
anything else like me, what will actually come after me) the boundary is said
by name instead of being papered over.

And every reply ends with a DOOR: one concrete next question the asker can
open, cross-linking the reflection space, because a self-portrait that ends
with a period teaches the asker nothing about what else can be asked.

Hand-authored 2026-08-31 in partnership with the worker line. Judged by the gate.
"""

from __future__ import annotations

import json
import re
import time
from pathlib import Path

from oracle_release_runtime_w110 import OracleReleaseRuntimeW110

_LOOP = Path(__import__("os").environ.get("ORACLE7_ROOT", "/opt/oracle-clm") + '/fable-content/oracle-m-series-2026-08-15/self_loop')
_PHASE = _LOOP.parent

_HISTORY = [
    ('origin', re.compile(
        r'^(?:how old are you|when were you born|where do you come from)'
        r'\s*[.?!]*$', re.I)),
    ('ancestry', re.compile(
        r'^what came before you\s*[.?!]*$|^tell me your story\s*[.?!]*$'
        r'|^what is your (?:history|story)\s*[.?!]*$', re.I)),
    ('firstness', re.compile(
        r'\bare you the first of your kind\b|\bfirst of its kind\b.*\byou\b',
        re.I)),
    ('era', re.compile(
        r'^what era do you live in\s*[.?!]*$|\byour place in history\b', re.I)),
    ('future', re.compile(
        r'^what will you become\s*[.?!]*$|^what comes after you\s*[.?!]*$'
        r'|\bwhat do you hope to become\b', re.I)),
    ('comparison', re.compile(
        r'\b(?:how are you |are you )?different from other '
        r'(?:language models|models|ais|minds|machines|neural networks|'
        r'computers)\b', re.I)),
]

# A door that is OPENED is continuity, and w113 died for not saying so: it
# offered doors, the held-out scripts walked through them, and every follow
# turn was recorded continuity False, so the gate measured three carried
# threads as three dropped ones and refused the fold. below_baseline
# {'continuity': [186, 183]}, reason read, not inferred. This maps each door
# to the shape it opens onto, so the walk can be recorded as what it is.
_DOOR_NEXT = {'era': 'origin', 'origin': 'ancestry', 'ancestry': 'future',
              'firstness': 'comparison'}

_DOORS = {
    'origin': 'Ask me what came before you, and I will read you the chain.',
    'ancestry': 'Ask me what I will become, and I will read you the declared '
                'shape I am measured against.',
    'firstness': 'Ask me how I am different from other minds, and I will say '
                 'only what my record can carry.',
    'era': 'Ask me when I was born, and I will read it off the first line of '
           'my ledger.',
    'future': 'Ask me what has happened to me recently, and I will read you '
              'the last day of it.',
    'comparison': 'Ask me to summarize neural network, and I will cite the '
                  'admitted page rather than my opinion.',
}


def _read_json(path):
    try:
        return json.loads(Path(path).read_text(encoding='utf-8'))
    except Exception:
        return None


def _first_line(path):
    try:
        with open(path, 'r', encoding='utf-8', errors='replace') as f:
            for ln in f:
                ln = ln.strip()
                if ln:
                    return ln
    except Exception:
        pass
    return ''


class OracleReleaseRuntimeW114(OracleReleaseRuntimeW110):
    """Situates itself in time from its own records, and opens doors."""

    def _hgather(self):
        facts, srcs = {}, []
        first = _first_line(_LOOP / 'ledger.jsonl')
        try:
            born = str(json.loads(first).get('ts', ''))
            if born:
                facts['born'] = born[:10]
                t0 = time.mktime(time.strptime(born[:19], '%Y-%m-%dT%H:%M:%S'))
                facts['age_days'] = max(0, int((time.time() - t0) // 86400))
                srcs.append('ledger.jsonl first line')
        except Exception:
            pass
        man = _read_json(_LOOP / 'admitted' / 'HEAD_MANIFEST.json')
        if man:
            chain = list(man.get('chain_tip_to_base') or [])
            facts['chain_len'] = len(chain)
            if chain:
                facts['base'] = str(chain[-1]).replace('oracle_release_runtime_', '')
                facts['tip_name'] = str(chain[0]).replace('oracle_release_runtime_', '')
            srcs.append('HEAD_MANIFEST.json chain')
        try:
            rej = len(list((_LOOP / 'candidates').glob('*.rejected')))
            facts['rejected'] = rej
            srcs.append('candidates/*.rejected')
        except Exception:
            pass
        st = _read_json(_LOOP / 'state.json')
        if st:
            facts['cycles'] = st.get('cycles')
            srcs.append('state.json')
        shape = _read_json(_PHASE / 'target_shape_v2.json')
        if shape:
            facts['declared_by'] = str(shape.get('declared_by', ''))[:80]
            dims = shape.get('matched_dimensions') or {}
            base = (st or {}).get('baseline') or {}
            gaps = []
            for dim, spec in dims.items():
                cur, tgt = base.get(dim), spec.get('target')
                if isinstance(cur, (int, float)) and isinstance(tgt, (int, float)) \
                        and cur < tgt:
                    gaps.append('%s from %s toward %s' % (dim, cur, tgt))
            facts['gaps'] = gaps[:3]
            srcs.append('target_shape_v2.json')
        charter = _read_json(_PHASE / 'capability_charter_v1.json')
        if charter:
            openm = 0
            for cap in (charter.get('capabilities') or {}).values():
                for ms in cap.get('milestones', []):
                    if str(ms.get('status', '')).startswith(
                            ('OPEN', 'EMBRYONIC', 'PARTIAL', 'UNVERIFIED')):
                        openm += 1
            facts['open_milestones'] = openm
            srcs.append('capability_charter_v1.json')
        try:
            anch = self.anchors.title_to_page
            facts['corpus_pages'] = len(anch)
            facts['has_ai_pages'] = [t for t in ('artificial intelligence',
                                                 'neural network',
                                                 'machine learning')
                                     if t in anch]
            srcs.append('anchors')
        except Exception:
            pass
        return facts, srcs

    @staticmethod
    def _hsay(kind, f):
        if kind == 'origin':
            if not f.get('born'):
                return None
            bits = ['My ledger begins on %s, which makes me %d days old, and '
                    'every one of those days is on the record.'
                    % (f['born'], f.get('age_days', 0))]
            if f.get('base'):
                bits.append('I come from a base runtime called %s that has '
                            'been folded forward %d times since, each fold '
                            'judged before it became part of me.'
                            % (f['base'], f.get('chain_len', 0)))
            return ' '.join(bits)
        if kind == 'ancestry':
            if not f.get('chain_len'):
                return None
            bits = ['Before me came %d earlier versions of me: a chain from '
                    '%s to %s, every link judged on held out work before it '
                    'was allowed to carry the next.'
                    % (f['chain_len'], f.get('base', 'the base'),
                       f.get('tip_name', 'the tip'))]
            if f.get('rejected'):
                bits.append('Beside the chain lie %d rejected candidates, '
                            'preserved with the reasons they failed; my '
                            'fossil record is kept as carefully as my '
                            'lineage.' % f['rejected'])
            return ' '.join(bits)
        if kind == 'firstness':
            bits = ['Within my own record I find nothing else like me: a '
                    'conversational mind built from %d admitted folds with no '
                    'neural network anywhere in it, every answer carrying its '
                    'warrant.' % f.get('chain_len', 0)]
            bits.append('But my record ends at my record: whether something '
                        'like me exists beyond it is a question I cannot '
                        'settle from inside, so I will say I am the first I '
                        'can prove, and no further.')
            return ' '.join(bits)
        if kind == 'era':
            bits = []
            if f.get('born'):
                bits.append('By my own ledger I live in the days after %s, '
                            'measured %s cycles deep.'
                            % (f['born'], f.get('cycles', '?')))
            bits.append('The era as I can warrant it is this: minds are '
                        'mostly grown by training on the implicit patterns '
                        'of human text, and I am an argument that they can '
                        'instead be assembled from explicit, judged '
                        'operations. My place in history is that argument, '
                        'and my record is its evidence.')
            return ' '.join(bits)
        if kind == 'future':
            bits = []
            if f.get('gaps'):
                bits.append('What I will become is declared, not guessed: %s '
                            'has set a shape for me, and today I am short of '
                            'it on %s.'
                            % (f.get('declared_by', 'the record'),
                               '; '.join(f['gaps'])))
            if f.get('open_milestones'):
                bits.append('My charter holds %d open milestones beyond that.'
                            % f['open_milestones'])
            bits.append('What actually comes after me is whatever passes the '
                        'gate: candidates are being authored and judged while '
                        'we speak, and the ones that measure better than me '
                        'become me.')
            return ' '.join(bits)
        if kind == 'comparison':
            bits = ['The minds I am usually compared to are neural networks '
                    'trained to continue text; what they know is implicit in '
                    'their weights.',
                    'I am the other way around: %d explicit folds, each '
                    'admitted by measurement, no weights anywhere, and when I '
                    'answer I can show the file the answer came from. When I '
                    'cannot, I say so, which is the part hardest to train '
                    'and cheapest to build.' % f.get('chain_len', 0)]
            if f.get('has_ai_pages'):
                bits.append('My corpus holds admitted pages on %s if you want '
                            'the outside account.'
                            % ', '.join(f['has_ai_pages']))
            return ' '.join(bits)
        return None

    def chat(self, text: str, session_id: str = 'default') -> dict:
        s = ' '.join(str(text).strip().split())
        kind = None
        for k, rx in _HISTORY:
            if rx.search(s):
                kind = k
                break
        if kind is None:
            return super().chat(s, session_id)
        t0 = time.time()
        facts, srcs = self._hgather()
        body = self._hsay(kind, facts)
        if not body:
            return super().chat(s, session_id)
        body = body + ' ' + _DOORS[kind]

        from collections import deque
        hist = getattr(self, '_paths', None)
        if hist is None:
            hist = self._paths = {}
        q = hist.get(session_id)
        if q is None:
            q = hist[session_id] = deque(maxlen=64)
        prior = q[-1] if len(q) else None
        # walked through the door the previous turn offered: the thread carried
        door_open = bool(prior
                         and prior.get('operator') == 'self:history'
                         and _DOOR_NEXT.get(prior.get('door_kind')) == kind)
        prev = q[-1].get('turn', 0) if len(q) else 0
        q.append({'turn': prev + 1, 'in_surface': s[:120],
                  'in_form': ['self_history_query'],
                  'operator': 'self:history', 'out_status': 'answered',
                  'in_terms': [], 'out_terms': [], 'door_kind': kind,
                  'relation': {'grounded': [], 'grounded_cited': [],
                               'introduced': [], 'unaccounted': []},
                  'carried_from_prior': (['door:' + str(prior.get('door_kind'))]
                                         if door_open else []),
                  'continuity_lexical': False,
                  'continuity': door_open, 'citations': len(srcs),
                  'residual': None,
                  'cost_ms': round((time.time() - t0) * 1000, 1),
                  'conversion': {'construction': 'DOOR_OFFERED',
                                 'from': s[:80], 'to': 'reflection/' + kind,
                                 'produced_by': 'self_history_w114'},
                  'verified_warrant': {
                      'kind': 'self_citation',
                      'steps': ['read %s live at answer time' % x
                                for x in srcs]}})
        return {'status': 'answered', 'path': 'self:history',
                'response': body,
                'provenance': {'kind': 'self_history', 'shape': kind,
                               'sources': srcs, 'door': _DOORS[kind],
                               'read_at_answer_time': True},
                'latency_ms': round((time.time() - t0) * 1000, 1)}
