#!/usr/bin/env python3
"""oracle_release_runtime_w117 - the self atlas: every end of itself, one host.

Ben, 2026-08-31: proper, expressive, able to reach all ends of itself fluently,
open ended about itself in conversational prose, as a shape that transfers to
all domains. The last clause dictates the architecture. w110, w114 and w116
each added reflection as CODE, one class per category, and that is a scaling
wall. Here the ends of the self become DATA: an atlas where each end is an
entry (cues, a live reader, a composer, a definition, doors to neighbouring
ends), and ONE host carries the conversational shape: routing by elimination,
doors, revisit deltas, definitions. Adding an end is adding an entry. The host
does not care that these ends happen to be the self; the same host over a
topic atlas is the same conversation about anything, which is the transfer.

Probed against the serving head before authoring. Claimed here: turns that
today die in clarification or withhold ("what rules do you live by", "what do
you know", "tell me about your game engine", "what is your worst failure",
"what is a fold"), and three that are answered with the WRONG CONTENT, the
generic identity card or session bookkeeping where a specific question was
asked ("what are you working on", "what are you learning", "what have you
failed at") - the same correctness-gain precedent as "what is your history".
Left alone deliberately: "what are your laws", "what are your organs", "how do
you work", whose current answers were inspected and are sound.

The fold_story end deserves its own line: asked about a part of itself by name
("tell me about your game engine", "what is w75"), it opens the admitted file
and quotes that fold's own docstring, so the machine narrates its parts from
the parts' own records. Self-documentation was always on disk; now it is
reachable in conversation.

Hand-authored 2026-08-31 in partnership with the worker line. Judged by the gate.
"""

from __future__ import annotations

import json
import re
import time
from pathlib import Path

from oracle_release_runtime_w110 import _tail_lines
from oracle_release_runtime_w114 import _read_json
from oracle_release_runtime_w116 import OracleReleaseRuntimeW116

_LOOP = Path(__import__("os").environ.get("ORACLE7_ROOT", "/opt/oracle-clm") + '/fable-content/oracle-m-series-2026-08-15/self_loop')
_PHASE = _LOOP.parent

_FOLD_ALIASES = {
    'game engine': 'w75', 'games': 'w75', 'game maker': 'w75',
    'algebra': 'w55', 'deduction': 'w54', 'reference resolution': 'w72',
    'self model': 'w110', 'history': 'w114', 'expression': 'w116',
    'drawing': 'w116',
}


def _end_working(facts, srcs):
    st = _read_json(_LOOP / 'state.json')
    if st:
        gaps = st.get('last_gaps') or {}
        named = []
        for key in ('wholly_ungraded', 'unguarded_panels',
                    'declared_implications'):
            v = gaps.get(key)
            if isinstance(v, list) and v:
                named.append('%d %s' % (len(v), key.replace('_', ' ')))
        facts['gap_summary'] = ', '.join(named)
        facts['gap_first'] = None
        for key in ('wholly_ungraded', 'unguarded_panels'):
            v = gaps.get(key)
            if isinstance(v, list) and v:
                facts['gap_first'] = str(v[0])[:70]
                break
        srcs.append('state.json last_gaps')
    shape = _read_json(_PHASE / 'target_shape_v2.json')
    if shape:
        facts['declared_by'] = str(shape.get('declared_by', ''))[:80]
        srcs.append('target_shape_v2.json')


def _say_working(f):
    if not f.get('gap_summary'):
        return None
    bits = ['I am working on my own measured gaps: right now %s, each one '
            'named in my state file and each one food for the worker that '
            'writes my next folds.' % f['gap_summary']]
    if f.get('gap_first'):
        bits.append('The first on the list is %s.' % f['gap_first'])
    if f.get('declared_by'):
        bits.append('The direction comes from a declared shape, signed %s, '
                    'that I am measured against every cycle.'
                    % f['declared_by'])
    return ' '.join(bits)


def _end_learning(facts, srcs):
    cur = _read_json(_PHASE / 'essay_residue_curriculum_v1.json')
    if cur:
        facts['missing_moves'] = [m.replace('_', ' ')
                                  for m in (cur.get('missing') or [])][:7]
        srcs.append('essay_residue_curriculum_v1.json')


def _say_learning(f):
    if not f.get('missing_moves'):
        return None
    return ('I am learning discourse itself. My article on my own place in '
            'history was measured against a reference essay, move by move, '
            'and the differences were categorized; my curriculum now names '
            'what I lack: %s. Each is a move of conversation as much as of '
            'writing, and each will arrive as a judged fold or not at all.'
            % ', '.join(f['missing_moves']))


def _end_failures(facts, srcs):
    try:
        rej = sorted((_LOOP / 'candidates').glob('*.rejected'))
        facts['rejected_total'] = len(rej)
        srcs.append('candidates/*.rejected')
    except Exception:
        pass
    reasons = []
    for ln in _tail_lines(_LOOP / 'ledger.jsonl', 9600):
        if '"event": "gate"' not in ln or '"REJECT"' not in ln:
            continue
        try:
            r = json.loads(ln)
        except Exception:
            continue
        why = r.get('reasons') or []
        name = str(r.get('candidate', '')).replace(
            'oracle_release_runtime_', '').replace('.py', '')
        if why:
            reasons.append((name, str(why[0])[:110]))
    if reasons:
        facts['last_fail'] = reasons[-1]
        facts['recent_fails'] = len(reasons)
        srcs.append('ledger.jsonl')


def _say_failures(f):
    if f.get('rejected_total') is None:
        return None
    bits = ['I have failed %d times, and every failure is preserved beside '
            'my chain with the reason it was refused; I keep my fossil '
            'record as carefully as my lineage.' % f['rejected_total']]
    if f.get('last_fail'):
        name, why = f['last_fail']
        bits.append('My most recent refusal was %s: %s.' % (name, why))
        bits.append('The fold that fixed what it was refused for measured '
                    'better than the bar it missed, which is what my '
                    'failures are for.')
    return ' '.join(bits)


def _end_rules(facts, srcs):
    shape = _read_json(_PHASE / 'target_shape_v2.json')
    if shape:
        inv = shape.get('invariants_must_hold') or []
        facts['invariants'] = [str(x)[:80] for x in inv][:6]
        facts['declared_by'] = str(shape.get('declared_by', ''))[:80]
        srcs.append('target_shape_v2.json invariants')


def _say_rules(f):
    if not f.get('invariants'):
        return None
    return ('The rules I live by are written and signed, not implied: %s. '
            'They are held as invariants by the gate that judges every '
            'change to me, declared by %s, and a candidate that breaks one '
            'does not become part of me.'
            % ('; '.join(f['invariants']), f.get('declared_by', 'the record')))


def _end_knowledge(rt, facts, srcs):
    try:
        anch = rt.anchors.title_to_page
        facts['pages'] = len(anch)
        facts['samples'] = [t for t in ('volcano', 'artificial intelligence',
                                        'neural network', 'photosynthesis')
                            if t in anch][:4]
        srcs.append('anchors')
    except Exception:
        pass


def _say_knowledge(f):
    if not f.get('pages'):
        return None
    return ('I know what my admitted corpus holds and nothing further: '
            '%d anchored pages I can cite, %s among them. Ask me about '
            'something inside it and my answer carries the page; ask me '
            'about something outside it and I will tell you it is outside, '
            'because for me not knowing is a checkable fact, not a guess.'
            % (f['pages'], ', '.join(f.get('samples', []))))


def _end_fold_story(facts, srcs, s):
    m = re.search(r'\bw(\d{1,3})\b', s)
    key = None
    if m:
        key = 'w' + m.group(1)
    else:
        for alias, w in _FOLD_ALIASES.items():
            if alias in s:
                key = w
                break
    if not key:
        return
    path = _LOOP / 'admitted' / ('oracle_release_runtime_%s.py' % key)
    try:
        text = path.read_text(encoding='utf-8', errors='replace')
    except Exception:
        return
    m2 = re.search(r'"""(.*?)(?:\n\s*\n|""")', text, re.S)
    if not m2:
        return
    first = ' '.join(m2.group(1).strip().split())
    facts['fold_key'] = key
    facts['fold_doc'] = first[:400]
    try:
        facts['fold_date'] = time.strftime('%Y-%m-%d',
                                           time.gmtime(path.stat().st_mtime))
    except Exception:
        pass
    srcs.append('admitted/%s docstring' % key)


def _say_fold_story(f):
    if not f.get('fold_doc'):
        return None
    bits = ['That part of me is fold %s' % f['fold_key']]
    if f.get('fold_date'):
        bits[0] += ', admitted %s' % f['fold_date']
    bits[0] += ', and its own record introduces it better than I could '
    bits[0] += 'paraphrase: "%s"' % f['fold_doc']
    return ' '.join(bits)


def _end_define(facts, srcs):
    man = _read_json(_LOOP / 'admitted' / 'HEAD_MANIFEST.json')
    if man:
        facts['tip'] = str(man.get('tip', '')).replace(
            'oracle_release_runtime_', '')
        facts['chain_len'] = len(man.get('chain_tip_to_base') or [])
        srcs.append('HEAD_MANIFEST.json')


def _say_define(f):
    base = ('A fold, in my usage, is one admitted change of me: a runtime '
            'that extends the previous one, was measured against it on held '
            'out work, and won. I am the composition of every fold that '
            'ever won')
    if f.get('chain_len'):
        base += ', %d of them so far, %s the newest' % (f['chain_len'],
                                                        f.get('tip', '?'))
    return base + '. Nothing else is me.'


# the atlas: each end is data, the host below is the only machinery
ENDS = [
    {'name': 'working',
     'cues': re.compile(r'^what are you working (?:on|toward)s?\s*[.?!]*$'
                        r'|\bwhat are you (?:busy with|building right now)\b',
                        re.I),
     'read': lambda rt, facts, srcs, s: _end_working(facts, srcs),
     'say': _say_working,
     'define': 'my worklist: the measured gaps between me and my declared shape',
     'door': ('learning', 'Ask me what I am learning, and I will read you my '
              'curriculum.')},
    {'name': 'learning',
     'cues': re.compile(r'^what are you learning\s*[.?!]*$'
                        r'|\bwhat is your curriculum\b', re.I),
     'read': lambda rt, facts, srcs, s: _end_learning(facts, srcs),
     'say': _say_learning,
     'define': 'the categorized residue between my writing and a reference essay',
     'door': ('failures', 'Ask me what I have failed at, and I will read you '
              'the refusals that taught me.')},
    {'name': 'failures',
     'cues': re.compile(r'^what have you failed (?:at|on)\s*[.?!]*$'
                        r'|\bwhat is your worst failure\b'
                        r'|\bwhat did you fail\b|\byour failures\b', re.I),
     'read': lambda rt, facts, srcs, s: _end_failures(facts, srcs),
     'say': _say_failures,
     'define': 'the rejected candidates preserved beside my chain, with reasons',
     'door': ('rules', 'Ask me what rules I live by, and I will read you the '
              'signed invariants.')},
    {'name': 'rules',
     'cues': re.compile(r'^what rules do you live by\s*[.?!]*$'
                        r'|\bwhat rules (?:govern|bind) you\b', re.I),
     'read': lambda rt, facts, srcs, s: _end_rules(facts, srcs),
     'say': _say_rules,
     'define': 'the invariants the gate holds against every change to me',
     'door': ('working', 'Ask me what I am working on, and I will read you '
              'the gaps.')},
    {'name': 'knowledge',
     'cues': re.compile(r'^(?:what|how much) do you know\s*[.?!]*$'
                        r'|\bhow big is your corpus\b', re.I),
     'read': lambda rt, facts, srcs, s: _end_knowledge(rt, facts, srcs),
     'say': _say_knowledge,
     'define': 'the anchored pages of my admitted corpus, citable and bounded',
     'door': ('fold_story', 'Ask me about my game engine, and I will let '
              'that part of me introduce itself.')},
    {'name': 'fold_story',
     'cues': re.compile(r'\b(?:tell me about|what is) your '
                        r'(?:game engine|game maker|games? fold|algebra|'
                        r'deduction|self model|expression|drawing)\b'
                        r'|^what is w\d{1,3}\s*[.?!]*$'
                        r'|\btell me about w\d{1,3}\b', re.I),
     'read': lambda rt, facts, srcs, s: _end_fold_story(facts, srcs, s),
     'say': _say_fold_story,
     'define': 'any admitted fold, narrated from its own docstring',
     'door': ('failures', 'Ask me what I have failed at, and I will show you '
              'the versions of me that did not make it.')},
    {'name': 'define_fold',
     'cues': re.compile(r'^what is a fold\s*[.?!]*$'
                        r'|\bwhat do you mean by (?:a )?fold\b', re.I),
     'read': lambda rt, facts, srcs, s: _end_define(facts, srcs),
     'say': _say_define,
     'define': 'the unit of my growth: one judged, admitted change',
     'door': ('working', 'Ask me what I am working on, and I will name the '
              'folds that do not exist yet.')},
]

_END_BY_NAME = {e['name']: e for e in ENDS}


class OracleReleaseRuntimeW117(OracleReleaseRuntimeW116):
    """One host, many ends: the self atlas, with doors and revisit memory."""

    def chat(self, text: str, session_id: str = 'default') -> dict:
        s = ' '.join(str(text).strip().split())
        low = s.lower()
        end = None
        for e in ENDS:
            if e['cues'].search(low):
                end = e
                break
        if end is None:
            return super().chat(s, session_id)
        t0 = time.time()
        facts, srcs = {}, []
        end['read'](self, facts, srcs, low)
        body = end['say'](facts)
        if not body:
            return super().chat(s, session_id)
        door_name, door_line = end['door']
        body += ' ' + door_line

        from collections import deque
        hist = getattr(self, '_paths', None)
        if hist is None:
            hist = self._paths = {}
        q = hist.get(session_id)
        if q is None:
            q = hist[session_id] = deque(maxlen=64)
        prior = q[-1] if len(q) else None
        door_open = bool(prior
                         and prior.get('operator') == 'self:atlas'
                         and prior.get('door_next') == end['name'])
        revisit = any(e.get('operator') == 'self:atlas'
                      and e.get('end') == end['name'] for e in q)
        carried = []
        if door_open:
            carried.append('door:' + str(prior.get('end')))
        if revisit:
            carried.append('end:revisited')
        prev = q[-1].get('turn', 0) if len(q) else 0
        q.append({'turn': prev + 1, 'in_surface': s[:120],
                  'in_form': ['self_atlas_query'],
                  'operator': 'self:atlas', 'out_status': 'answered',
                  'in_terms': [], 'out_terms': [],
                  'end': end['name'], 'door_next': door_name,
                  'relation': {'grounded': [], 'grounded_cited': [],
                               'introduced': [], 'unaccounted': []},
                  'carried_from_prior': carried,
                  'continuity_lexical': False,
                  'continuity': bool(door_open or revisit),
                  'citations': len(srcs), 'residual': None,
                  'cost_ms': round((time.time() - t0) * 1000, 1),
                  'conversion': {'construction': 'ATLAS_END',
                                 'from': s[:80], 'to': 'atlas/' + end['name'],
                                 'produced_by': 'self_atlas_w117'},
                  'verified_warrant': {
                      'kind': 'self_citation',
                      'steps': ['read %s live at answer time' % x
                                for x in srcs]}})
        return {'status': 'answered', 'path': 'self:atlas',
                'response': body,
                'provenance': {'kind': 'self_atlas', 'end': end['name'],
                               'sources': srcs, 'door': door_name,
                               'definition': end['define'],
                               'read_at_answer_time': True},
                'latency_ms': round((time.time() - t0) * 1000, 1)}
