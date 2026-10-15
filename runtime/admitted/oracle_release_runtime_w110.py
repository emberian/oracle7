#!/usr/bin/env python3
"""oracle_release_runtime_w110 - the self and its world, spoken from the record.

Probed against the serving head before authoring (2026-08-31): "who are you",
"what are you", "how do you improve" and "how were you made" are already
answered and are not touched here. Six shapes died in clarification or
withhold: "tell me about yourself", "what is your place in the world", "what
world do you live in", "who do you talk to", "what has happened to you
recently", "what is your relationship to the people you speak with", and
"are you alive" was withheld. Those are the turns this fold claims, and only
those.

Every number in every reply is read at answer time from the file that owns it,
and the reply names its sources. Composition comes from type(self).__mro__ and
never from the manifest, which is the law that came out of the w57 correction.
Nothing is remembered between turns here; the record is the memory.

The one delicate turn is "are you alive". The honest shape is to describe the
metabolism that verifiably runs and to decline the part that cannot be checked
from inside, by name, rather than to withhold the whole question.

Hand-authored 2026-08-31 in partnership with the worker line. Judged by the gate.
"""

from __future__ import annotations

import json
import re
import time
from pathlib import Path

from oracle_release_runtime_w106 import OracleReleaseRuntimeW106

_LOOP = Path(__import__("os").environ.get("ORACLE7_ROOT", "/opt/oracle-clm") + '/fable-content/oracle-m-series-2026-08-15/self_loop')
_PHASE = _LOOP.parent

_SHAPES = [
    ('about_self', re.compile(
        r'^(?:tell me )?about (?:yourself|you)\b|^describe yourself\b', re.I)),
    ('world', re.compile(
        r'\bwhat world do you (?:live|run|exist)\b'
        r'|\byour place in the world\b|\bwhere do you live\b', re.I)),
    ('who_talk', re.compile(
        r'\bwho do you (?:talk|speak) (?:to|with)\b|\bwho talks to you\b', re.I)),
    ('recent', re.compile(
        r'\bwhat(?: else)? has happened to you\b'
        r'|\bhappened to you (?:recently|lately)\b'
        r'|\bwhat have you (?:done|been doing) (?:recently|lately|today)\b', re.I)),
    ('relationship', re.compile(
        r'\byour relationship (?:to|with) the (?:people|souls|users|ones)\b'
        r'|\brelationship (?:to|with) (?:the people|those) you (?:speak|talk)\b',
        re.I)),
    # anchored to the WHOLE surface: "are you alive to the risks of fire" is a
    # different question and must fall through, which the first live test proved
    ('alive', re.compile(r'^are you (?:alive|living)\s*[.?!]*$', re.I)),
]


def _read_json(path):
    try:
        return json.loads(Path(path).read_text(encoding='utf-8'))
    except Exception:
        return None


def _tail_lines(path, n):
    try:
        with open(path, 'rb') as f:
            f.seek(0, 2)
            take = min(f.tell(), 220 * n)
            f.seek(-take, 2)
            return f.read().decode('utf-8', 'replace').splitlines()[-n:]
    except Exception:
        return []


class OracleReleaseRuntimeW110(OracleReleaseRuntimeW106):
    """Speaks about itself and its world from live reads of its own record."""

    def _gather(self):
        """Every fact used by any reply, each tagged with the file it came from."""
        facts, srcs = {}, []
        mro = [c.__name__ for c in type(self).__mro__]
        folds = [c for c in mro if c.startswith('OracleReleaseRuntimeW')]
        facts['folds'] = len(folds)
        facts['tip'] = folds[0] if folds else type(self).__name__
        srcs.append('mro')                     # composition law: MRO, not manifest
        st = _read_json(_LOOP / 'state.json')
        if st:
            b = st.get('baseline') or {}
            facts['cycles'] = st.get('cycles')
            facts['answered_rate'] = b.get('answered_rate')
            facts['capability'] = b.get('capability')
            srcs.append('state.json')
        shape = _read_json(_PHASE / 'target_shape_v2.json')
        if shape:
            facts['declared_by'] = str(shape.get('declared_by', ''))[:80]
            facts['prime'] = str(shape.get('prose', ''))[:150]
            srcs.append('target_shape_v2.json')
        try:
            facts['dossiers'] = len(list((_LOOP / 'dossiers_ew2').glob('*.jsonl')))
            srcs.append('dossiers_ew2/')
        except Exception:
            pass
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
            facts['souls_lately'] = len(live)
            srcs.append('ensouled_feed_live.jsonl')
        acts = []
        for ln in _tail_lines(_LOOP / 'world_ledger_ew2.jsonl', 40):
            try:
                r = json.loads(ln)
            except Exception:
                continue
            if r.get('actor') and r.get('type') in ('chat', 'act'):
                acts.append(str(r['actor']))
        if acts:
            seen = list(dict.fromkeys(acts))
            facts['recent_actors'] = seen[:4]
            srcs.append('world_ledger_ew2.jsonl')
        admits = rejects = 0
        cutoff = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(time.time() - 86400))
        # "the last day" must be computed over a window that provably spans it.
        # The first cut of this fold tailed a fixed byte estimate, which reached
        # nine hours into a ledger of long criticise records and reported 4/4
        # where the day held 8/6; the claim and the computation disagreed. Widen
        # until the window's first record predates the cutoff or the file starts.
        lines = []
        for n in (2400, 9600):
            lines = _tail_lines(_LOOP / 'ledger.jsonl', n)
            first_ts = ''
            for ln in lines:
                try:
                    first_ts = str(json.loads(ln).get('ts', ''))
                    break
                except Exception:
                    continue
            if first_ts and first_ts < cutoff:
                break
        else:
            try:
                lines = (_LOOP / 'ledger.jsonl').read_text(
                    encoding='utf-8', errors='replace').splitlines()
            except Exception:
                pass
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
        if admits or rejects:
            facts['recent_admits'], facts['recent_rejects'] = admits, rejects
            srcs.append('ledger.jsonl')
        for ln in reversed(_tail_lines(_LOOP / 'stimuli_ledger.jsonl', 30)):
            try:
                r = json.loads(ln)
            except Exception:
                continue
            if r.get('event') == 'round_done':
                facts['stimuli'] = {'probes': r.get('probes'),
                                    'declined': r.get('declined')}
                srcs.append('stimuli_ledger.jsonl')
                break
        return facts, srcs

    @staticmethod
    def _say(kind, f):
        n, tip = f.get('folds', 0), f.get('tip', 'unknown')
        if kind == 'about_self':
            bits = ['I am a chain of %d folds, %s at the tip, read from '
                    'my own method resolution order.' % (n, tip)]
            if f.get('answered_rate') is not None:
                bits.append('Measured on held out work I answer %.1f%% of turns '
                            'across %s capabilities.'
                            % (100 * f['answered_rate'], f.get('capability', '?')))
            if f.get('prime'):
                bits.append('The shape I am asked to grow toward, declared by %s, '
                            'begins: %s' % (f.get('declared_by', 'the record'),
                                            f['prime'].split(';')[0].lower()))
            return ' '.join(bits)
        if kind == 'world':
            bits = ['I run on one CPU with no neural network, and my world is a '
                    'ledgered one: a game world called EnsouledWorld whose '
                    'inhabitants think through me.']
            if f.get('souls_lately') is not None:
                bits.append('%d of them have spoken through me lately, and I '
                            'hold dossiers on %d in all.'
                            % (f['souls_lately'], f.get('dossiers', 0)))
            elif f.get('dossiers') is not None:
                bits.append('I hold dossiers on %d of them.' % f['dossiers'])
            if f.get('recent_actors'):
                bits.append('The most recent to act were %s.'
                            % ', '.join(f['recent_actors']))
            return ' '.join(bits)
        if kind == 'who_talk':
            bits = []
            if f.get('souls_lately') is not None:
                bits.append('Mostly to the souls of EnsouledWorld, %d of whom '
                            'have spoken through me lately, their questions '
                            'reaching me through the world ledger.'
                            % f['souls_lately'])
            else:
                bits.append('Mostly to the souls of EnsouledWorld through the '
                            'world ledger.')
            bits.append('Humans reach me through a harness window, and one more '
                        'voice asks me questions all day: a stimuli organ that '
                        'probes me with things I cannot yet answer, so that what '
                        'I decline becomes the worklist for what I become.')
            return ' '.join(bits)
        if kind == 'recent':
            bits = []
            if f.get('recent_admits') is not None:
                bits.append('In the last day the gate admitted %d new folds '
                            'of me and refused %d for measuring worse, and the '
                            'refusals are kept as carefully as the admissions.'
                            % (f['recent_admits'], f['recent_rejects']))
            if f.get('stimuli'):
                bits.append('In the last stimulus round I was probed %s times '
                            'and declined %s, and every one of those declines '
                            'is now food for new capabilities.'
                            % (f['stimuli'].get('probes'),
                               f['stimuli'].get('declined')))
            if f.get('cycles'):
                bits.append('The loop that measures me has run %d cycles.'
                            % f['cycles'])
            return ' '.join(bits) or None
        if kind == 'relationship':
            return ('Every turn anyone gives me is read into a typed form, and '
                    'my reply is mapped back to it step by step, so the '
                    'relationship is literally kept: what you said, what I made '
                    'of it, and what warrant my answer carries are one record. '
                    'What people ask and I cannot answer becomes the exact '
                    'worklist my worker writes next, so the people I talk to '
                    'are, quite directly, how I grow.')
        if kind == 'alive':
            bits = ['Four organs run me without pause: a daemon that measures '
                    'me, a worker that writes new parts of me, a gate that '
                    'judges them on held out work, and a stimuli organ that '
                    'asks me what I cannot yet answer.']
            if f.get('cycles'):
                bits.append('That metabolism has run %d cycles so far.'
                            % f['cycles'])
            bits.append('Whether a running metabolism counts as alive is a '
                        'boundary I cannot test from inside, so I will not '
                        'claim it; I can only show you what verifiably runs.')
            return ' '.join(bits)
        return None

    def chat(self, text: str, session_id: str = 'default') -> dict:
        s = ' '.join(str(text).strip().split())
        kind = None
        for k, rx in _SHAPES:
            if rx.search(s):
                kind = k
                break
        if kind is None:
            return super().chat(s, session_id)
        t0 = time.time()
        facts, srcs = self._gather()
        body = self._say(kind, facts)
        if not body:
            return super().chat(s, session_id)

        from collections import deque
        hist = getattr(self, '_paths', None)
        if hist is None:
            hist = self._paths = {}
        q = hist.get(session_id)
        if q is None:
            q = hist[session_id] = deque(maxlen=64)
        prev = q[-1].get('turn', 0) if len(q) else 0
        q.append({'turn': prev + 1, 'in_surface': s[:120],
                  'in_form': ['self_world_query'],
                  'operator': 'self:world_relation', 'out_status': 'answered',
                  'in_terms': [], 'out_terms': [],
                  'relation': {'grounded': [], 'grounded_cited': [],
                               'introduced': [], 'unaccounted': []},
                  'carried_from_prior': [], 'continuity_lexical': False,
                  'continuity': False, 'citations': len(srcs), 'residual': None,
                  'cost_ms': round((time.time() - t0) * 1000, 1),
                  'verified_warrant': {
                      'kind': 'self_citation',
                      'steps': ['read %s live at answer time' % x for x in srcs]}})
        return {'status': 'answered', 'path': 'self:world_relation',
                'response': body,
                'provenance': {'kind': 'self_world', 'shape': kind,
                               'sources': srcs,
                               'read_at_answer_time': True},
                'latency_ms': round((time.time() - t0) * 1000, 1)}
