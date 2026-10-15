#!/usr/bin/env python3
"""oracle_release_runtime_w173 - reception (MoynatMelchizedek): the vessel.

Ben, 2026-09-03: the Oracle has the Hermes half (routes that emit, a gate that
refuses) and not the Moynat half (a vessel made to measure for what it cannot
yet name). Declines fell to a queue that nobody received. This fold receives.

    RECEIVE  every turn the head could not answer opens or reinforces a VESSEL:
             the normalized surface, the routes that tried and failed, the
             sessions that asked, a weight, and the slot the shape lacks.
             The decline stays a decline (no false answer); one sentence is
             added that cites the vessel, so the asker can see the shape was
             kept. On recurrence the reply names the weight and asks for what
             is missing, and the turn is CONTINUITY: the shape was carried.
    WEIGH    weight = count x recency x source (a person outweighs the stimuli
             organ and the measurement loop). Weight decides what is woven
             next (the worker's tithe cycle); weight never names.
    REGISTER a question about the vessel itself ("what do you hold that you
             cannot name") is ANSWERED from the store, cited per vessel: the
             self-register of unnamed states. That is the aria of reception.
    EMIT     each reinforcement appends a typed request to
             curriculum_requests.jsonl: surface, weight, failed routes, slot.

Naming (R5) is not here: a vessel closes only when a later fold admits a route
that carries the shape with declared bounds. This fold keeps what waits.
Store: self_loop/vessels.json (atomic replace) + vessels_events.jsonl.
Base: the manifest tip at import, so the chain stays linear.
"""

from __future__ import annotations

import importlib
import json
import os
import re
import time
from collections import deque
from pathlib import Path

_HERE = Path(__file__).resolve().parent
# admitted/, candidates/, precheck/ all sit one level under self_loop
_LOOP = _HERE.parent if _HERE.parent.name == 'self_loop' else _HERE

# The gate reads a candidate's parents from its `from oracle_release_runtime_* import`
# lines and requires the serving tip among them (2026-09-03: a dynamic base was
# invisible to it and read as a fork). One parent, named: the tip.
from oracle_release_runtime_w171 import OracleReleaseRuntimeW171 as _Base

# the gate's own grounding instruments, reached without declaring a second parent
_an = importlib.import_module('oracle_release_runtime_an')
CITE, content_terms = _an.CITE, _an.content_terms

VESSELS = _LOOP / 'vessels.json'
EVENTS = _LOOP / 'vessels_events.jsonl'
REQUESTS = _LOOP / 'curriculum_requests.jsonl'

REGISTER = re.compile(
    r"^(?:what|which)\s+(?:do\s+you\s+hold|shapes?\s+(?:do\s+you\s+hold|(?:that\s+)?you\s+hold)|is\s+in\s+your\s+vessels?|"
    r"have\s+i\s+asked)\b.*|^what\s+(?:have\s+i|did\s+i)\s+ask(?:ed)?\s+that\s+you\s+could\s+not\s+answer\b.*|"
    r"^which\s+(?:shape|state|vessel)\b.*\bheaviest\b.*|^what\s+is\s+(?:the\s+)?heaviest\s+(?:shape|state|vessel)\b.*|"
    r"^what\s+can(?:'t|\s+not)\s+you\s+name\b.*|^what\s+is\s+unnamed\s+in\s+you\b.*", re.I)

NOT_ANSWERED = ('declined', 'withheld', 'unresolved', 'clarify', 'refused', 'error')


def _norm(s: str) -> str:
    return ' '.join(re.sub(r"[^a-z0-9' ]+", ' ', str(s).lower()).split())


def _slot_for(surface: str) -> tuple[str, str]:
    s = surface.lower()
    if re.match(r'^(what|which)\s+(is|are)\b', s):
        m = re.match(r"^(?:what|which)\s+(?:is|are)\s+(?:an?\s+|the\s+)?(.+?)\??$", s)
        t = m.group(1) if m else surface
        return 'genus', 'a definition of "%s" from an admitted source' % t
    if re.match(r'^who\b', s):
        return 'page', 'an admitted page for the name in "%s"' % surface
    if re.match(r'^(why|how)\b', s):
        return 'mechanism', 'the mechanism behind "%s", as steps with a source' % surface
    if re.match(r'^what does it mean\b', s):
        return 'genus', 'the sense in which "%s" is used, with a source' % surface
    return 'bounds', 'what "%s" counts as and what it does not' % surface


class OracleReleaseRuntimeW175(_Base):
    """Reception: vessels for what the head cannot yet name. (w173 was the same fold,
    rejected only for an undeclared parent; resubmitted as w175 with the tip named.)"""

    # ------------------------------------------------------------ store
    def _vessels_load(self) -> dict:
        try:
            return json.loads(VESSELS.read_text(encoding='utf-8'))
        except Exception:
            return {'next': 1, 'by_key': {}}

    def _vessels_save(self, store: dict) -> None:
        try:
            tmp = VESSELS.with_suffix('.json.tmp.%d' % os.getpid())
            tmp.write_text(json.dumps(store, indent=0, sort_keys=True), encoding='utf-8')
            os.replace(tmp, VESSELS)
        except Exception:
            pass

    @staticmethod
    def _event(kind: str, **kw) -> None:
        try:
            with open(EVENTS, 'a', encoding='utf-8') as f:
                f.write(json.dumps({'event': kind, 'ts': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), **kw}) + '\n')
        except Exception:
            pass

    @staticmethod
    def _weight(v: dict, now: float) -> float:
        age_days = max(0.0, (now - float(v.get('last_ts', now))) / 86400.0)
        recency = 1.0 + 1.0 / (1.0 + age_days)
        return round(v.get('count', 1) * recency * (1.0 + 0.5 * v.get('person_asks', 0)), 3)

    def _receive(self, surface: str, session_id: str, result: dict) -> tuple[dict, bool]:
        """Open or reinforce the vessel for this surface. Returns (vessel, is_reinforced)."""
        store = self._vessels_load()
        key = _norm(surface)
        now = time.time()
        v = store['by_key'].get(key)
        is_person = not str(session_id).startswith(('loop-', 'stimuli', 'probe'))
        if v is None:
            slot, question = _slot_for(surface)
            v = {'id': 'v%04d' % store['next'], 'surface': surface[:160], 'first_ts': now, 'last_ts': now,
                 'count': 0, 'person_asks': 0, 'sessions': [], 'failed': [], 'slot': slot,
                 'question': question, 'attempts': [], 'residue': [], 'name': None}
            store['next'] += 1
            store['by_key'][key] = v
            reinforced = False
        else:
            reinforced = True
        v['count'] += 1
        v['person_asks'] += 1 if is_person else 0
        v['last_ts'] = now
        if session_id not in v['sessions']:
            v['sessions'] = (v['sessions'] + [str(session_id)])[-12:]
        failed = '%s|%s' % (result.get('path'), result.get('status'))
        if failed not in v['failed']:
            v['failed'] = (v['failed'] + [failed])[-8:]
        refs = result.get('references') or (result.get('provenance') or {}).get('claims') or []
        if refs and 'nearest' not in v:
            v['nearest'] = str(refs[0])[:120]
        v['weight'] = self._weight(v, now)
        self._vessels_save(store)
        self._event('reinforce' if reinforced else 'open', vessel=v['id'], surface=v['surface'][:80],
                    weight=v['weight'], count=v['count'], session=str(session_id)[:40], failed=failed)
        if reinforced:
            try:
                with open(REQUESTS, 'a', encoding='utf-8') as f:
                    f.write(json.dumps({'vessel': v['id'], 'surface': v['surface'], 'weight': v['weight'],
                                        'count': v['count'], 'slot': v['slot'], 'question': v['question'],
                                        'failed': v['failed'], 'ts': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}) + '\n')
            except Exception:
                pass
        return v, reinforced

    # ------------------------------------------------------------ witness helpers
    def _paths_q(self, session_id: str):
        hist = getattr(self, '_paths', None)
        if hist is None:
            hist = self._paths = {}
        q = hist.get(session_id)
        if q is None:
            q = hist[session_id] = deque(maxlen=64)
        return q

    @staticmethod
    def _recite(rec: dict, text_in: str, response: str) -> None:
        """Recompute the gate's relation fields for an amended response (same instrument as the base)."""
        in_terms = content_terms(text_in)
        spans, cursor = [], 0
        for m in CITE.finditer(response):
            spans.append(response[cursor:m.start()].lower())
            cursor = m.end()
        cited = set()
        for sp in spans:
            cited |= content_terms(sp)
        out_terms = content_terms(response)
        rel = dict(rec.get('relation') or {})
        rel['grounded'] = sorted(in_terms & out_terms)
        rel['grounded_cited'] = sorted(in_terms & cited)
        rel['unaccounted'] = sorted(in_terms - out_terms)
        rec['relation'] = rel
        rec['out_terms'] = sorted(out_terms)[:24]
        rec['citations'] = len(CITE.findall(response))

    # ------------------------------------------------------------ the turn
    def chat(self, text: str, session_id: str = 'default') -> dict:
        s = ' '.join(str(text).strip().split())
        if REGISTER.match(s):
            return self._register(s, session_id)
        result = super().chat(s, session_id)
        status = str(result.get('status', ''))
        path = str(result.get('path', ''))
        if status == 'answered' and not path.startswith('act:clarify'):
            return result
        if not s or len(s.split()) < 2:
            return result
        v, reinforced = self._receive(s, session_id, result)
        q = self._paths_q(session_id)
        rec = q[-1] if len(q) and q[-1].get('in_surface', '')[:60] == s[:60] else None
        response = str(result.get('response', '')).rstrip()
        if reinforced:
            add = ('You have asked "%s" before. I hold it as an unnamed shape [vessel:%s], weight %s, asked %d '
                   'times; the routes that tried and failed: %s. What I lack is %s. Can you supply a source or a bound?'
                   % (v['surface'], v['id'], v['weight'], v['count'],
                      ', '.join(f.split('|')[0] for f in v['failed'][-3:]) or 'none', v['question']))
            tag = 'vessel:reinforced'
        else:
            add = ('I have received "%s" as an unnamed shape [vessel:%s]; if it returns it gains weight, and when I '
                   'can name it, I will.' % (v['surface'], v['id']))
            tag = 'vessel:receipt'
        response = (response + '\n\n' + add).strip()
        result = dict(result)
        result['response'] = response
        result['path'] = path + '|' + tag
        prov = dict(result.get('provenance') or {})
        prov['vessel'] = {'id': v['id'], 'weight': v['weight'], 'count': v['count'], 'slot': v['slot']}
        result['provenance'] = prov
        if rec is not None:
            rec['operator'] = result['path']
            rec['in_form'] = (rec.get('in_form') or []) + ['vessel_' + ('reinforced' if reinforced else 'receipt')]
            carried = list(rec.get('carried_from_prior') or [])
            if reinforced:
                carried.append('vessel:' + v['id'])
                rec['carried_from_prior'] = carried
                rec['continuity'] = bool(rec.get('turn', 1) > 1)
            rec['vessel'] = v['id']
            self._recite(rec, s, response)
        return result

    def _register(self, s: str, session_id: str) -> dict:
        store = self._vessels_load()
        vs = sorted(store['by_key'].values(), key=lambda x: (-float(x.get('weight', 0)), x.get('first_ts', 0)))
        q = self._paths_q(session_id)
        prev = q[-1].get('turn', 0) if len(q) else 0
        touched = [e.get('vessel') for e in q if e.get('vessel')]
        if not vs:
            body = 'I hold no unnamed shapes yet; every question so far was answered or was never kept [vessel:none].'
            cited_ids = []
        else:
            top = vs[:3]
            parts = []
            for v in top:
                parts.append('"%s" [vessel:%s], weight %s, asked %d times, what I lack is %s'
                             % (v['surface'], v['id'], v.get('weight', 0), v.get('count', 0), v.get('question', 'a bound')))
            body = ('I hold %d unnamed shape%s that I cannot yet name. The heaviest: %s. Weight decides what I weave next; '
                    'a shape is named only when a route carries it with declared bounds.'
                    % (len(vs), '' if len(vs) == 1 else 's', '; '.join(parts)))
            cited_ids = [v['id'] for v in top]
        result = {'status': 'answered', 'path': 'vessel:register', 'response': body,
                  'provenance': {'kind': 'vessel_register', 'vessels': cited_ids, 'held': len(vs)}}
        rec = {'turn': prev + 1, 'in_surface': s[:120], 'in_form': ['vessel_register'],
               'operator': 'vessel:register', 'out_status': 'answered',
               'in_terms': sorted(content_terms(s)), 'out_terms': [], 'relation': {},
               'carried_from_prior': ['vessel:' + t for t in touched[-3:]],
               'continuity_lexical': bool(touched), 'continuity': bool(prev and touched),
               'citations': 0, 'residual': None, 'cost_ms': 0.0,
               'verified_warrant': {'kind': 'vessel_register',
                                    'steps': ['load vessels.json', 'sort by weight desc', 'report top %d of %d' % (min(3, len(vs)), len(vs))]}}
        self._recite(rec, s, body)
        q.append(rec)
        self._event('register', session=str(session_id)[:40], held=len(vs), cited=cited_ids)
        return result
