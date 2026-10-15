#!/usr/bin/env python3
"""oracle_release_runtime_w480 - ORGAN DISPATCH: the first two organs built outside the chain are connected to it.

Until now none of the 226 admitted folds reached the typed relation store, the three-tree runtime, or the textbook
store; they sat beside the model. This fold is the dispatcher's first form: after the chain has produced its turn,
each organ whose preconditions hold may answer where the chain did not, or where the chain answered through a route
that the organ's own measurements show is weaker for that request shape.

1. MATH ORGAN (math_organ_v1, textbook_store_v1). A mathematical request (a directive - solve, simplify, factor,
   expand, evaluate, differentiate, integrate, limit, decompose - over an expression, not a word problem) is solved
   with exact moves and an INDEPENDENT check (substitute back / expand back / differentiate back / random-point
   equivalence / numeric agreement); nothing is released unless the check passes. The textbook's own method for the
   directive is cited ([tb:<id>]). Measured on OpenStax exercises held out BY MODULE, run once, frozen (sha a646833f):
   1,113 right / 191 wrong / 179 abstained of 1,483 (precision 85%); a 'return the input' mutant scores 75.
   Released when the chain did not answer, or answered a mathematical request through a non-mathematical route.
2. RELATION ORGAN (oracle_tritree_v1 over relstore relations_v1, rules A+B). A factual request answered by typed
   Wikidata relations found by the three-tree search, corroborated by a sentence of the subject's own article.
   Sealed: 32 right / 2 wrong alone on TriviaQA 6000-6999; with the pipeline 47/8 against the pipeline's 25/6.
   Released when the chain did not answer, or answered through a route family the training comparison
   (head_vs_organ_v1, 1,400 training questions) shows the organ beats there. Where the organ answered: chain
   clarified 28 -> organ right 20 (chain 0); compose route 7 -> organ 6, chain 3; factoid route 3 -> 3 and 3 (tie,
   so the chain keeps it). RELATION_OUTRANKS = compose only.
Every organ call runs under a time budget; an organ that errs or times out leaves the chain's turn unchanged.

3. THE VESSEL STORE MOVES TO AN INDEXED STORE (carried from w478, which the gate rejected as no_gain: the gate has no
   latency column, so a pure speed fix is invisible to it). MEASURED (profile_chain_v1, 16 mixed turns, daemon env):
   71% of turn time was JSON encoding - w175 loaded and rewrote self_loop/vessels.json (236,140 vessels, 122 MB) on
   every unanswered turn: 16-20 s per such turn, growing with every refusal. Same semantics, one indexed row per turn
   (vessels.sqlite3, WAL); measurement sessions keep w179's in-memory store; until the store is migrated every call
   falls through to w175's JSON path. vessels.json stays as a snapshot for its readers (vessels_sync_v1.py).
   16 mixed turns: 142.5 s -> 8.7 s, identical replies.
4. DIALOGUE ORGAN (organ_dialogue_v1). Social moves (hello, how are you, goodbye) and questions about the
   conversation itself (what did I just ask, what did you say, what were we talking about, what have I asked, you did
   not answer me) are answered from the session's own record with the turn cited ([session:turn N]); it never invents
   a turn, and says plainly when a question is still open and why. Only where the chain did not answer.
GATE EVIDENCE (precheck_candidate_v1 on panel v20, the gate's own instrument): capability 620 -> 755, no column
worse, repeat_rate 0.400 -> 0.398; false_yes 22 -> 23 from ONE item (MATH-500 guard "Evaluate $(1+2i)6-3i$"): the
organ's answer 6 + 9i is correct, but it was read with the linear reader by luck - the organ now declines typeset
(LaTeX) input until a LaTeX reader exists. Diff of the v19 precheck found the organ pre-empting the chain's own
operation routes (op:*, lcm, base, roman) and echoing bare numbers; both closed (never over op/algebra/compute routes;
no expression -> no answer; named operations it does not hold -> decline).
Parent: the serving tip, named. Methods _c480_ (organs) and _c478_ (vessels).
"""

from __future__ import annotations

import importlib
import json
import os
import re
import sqlite3
import threading
import time

from oracle_release_runtime_w354 import OracleReleaseRuntimeW354 as _Base

try:
    import math_organ_v1 as _math
except Exception:  # noqa: BLE001
    _math = None
try:
    import organ_dialogue_v1 as _dlg
except Exception:  # noqa: BLE001
    _dlg = None
try:
    os.environ.setdefault("TT_RULES", "A,B")
    import oracle_tritree_v1 as _tt
except Exception:  # noqa: BLE001
    _tt = None

_w175 = importlib.import_module('oracle_release_runtime_w175')
_an = importlib.import_module('oracle_release_runtime_an')
content_terms = _an.content_terms
VESSEL_DB = _w175.VESSELS.with_suffix('.sqlite3')
_LOCK = threading.Lock()

NOT_ANSWERED = ('declined', 'withheld', 'unresolved', 'clarify', 'clarification', 'refused', 'error')
# the chain's own mathematical routes carry their own fragments and phrasing: the organ never pre-empts them
MATH_PATHS = ('op', 'compute', 'algebra', 'deduce', 'math', 'arith', 'calc', 'code', 'game')
# route families where the relation organ's answer replaces the chain's (from head_vs_organ_v1 on training windows)
RELATION_OUTRANKS = ('compose',)
BUDGET_S = 4.0


def _run(fn, *a):
    """call an organ under a time budget; None on error or timeout (a runaway call is abandoned, the turn is not)"""
    box = {}

    def go():
        try:
            box['r'] = fn(*a)
        except Exception:  # noqa: BLE001
            box['r'] = None
    t = threading.Thread(target=go, daemon=True)
    t.start()
    t.join(BUDGET_S)
    return box.get('r')


class OracleReleaseRuntimeW480(_Base):

    def _c480_math(self):
        o = getattr(self, '_c480_m', None)
        if o is None and _math is not None:
            try:
                o = self._c480_m = _math.MathOrgan()
            except Exception:  # noqa: BLE001
                o = self._c480_m = False
        return o or None

    def _c480_rel(self):
        o = getattr(self, '_c480_r', None)
        if o is None and _tt is not None:
            try:
                o = self._c480_r = _tt.TriTree()
            except Exception:  # noqa: BLE001
                o = self._c480_r = False
        return o or None

    @staticmethod
    def _c480_answered(res) -> bool:
        return isinstance(res, dict) and str(res.get('status')) == 'answered'

    def _c480_dialogue(self):
        o = getattr(self, '_c480_d', None)
        if o is None and _dlg is not None:
            o = self._c480_d = _dlg.DialogueOrgan()
        return o

    def chat(self, text: str, session_id: str = "default") -> dict:
        res = super().chat(text, session_id)
        if not isinstance(res, dict):
            return res
        out = self._c480_dispatch(text, session_id, res)
        dlg = self._c480_dialogue()
        if dlg is not None:
            try:
                dlg.log(session_id, text, out)             # the conversation's own state, for discourse questions
            except Exception:  # noqa: BLE001
                pass
        return out

    def _c480_dispatch(self, text, session_id, res):
        path = str(res.get('path', ''))
        fam = re.split(r'[|>:]', path)[0] if path else ''
        answered = self._c480_answered(res)
        # 0. DIALOGUE - social moves and questions about the conversation itself, from the session's own record;
        # a question scoped to THIS conversation ("what have I asked so far") is the dialogue organ's, not the register's
        session_scoped = _dlg is not None and _dlg.SO_FAR.search(text or "") and fam == 'vessel'
        if not answered or session_scoped:
            dlg = self._c480_dialogue()
            a = _run(dlg.answer, text, session_id) if dlg else None
            if a:
                return self._c480_dialogue_reply(res, a)
        # 1. MATH - where the chain did not answer, or answered a mathematical request through a NON-mathematical route
        # ("Factor x^2 - 5x + 6" -> document_runtime "-3"); never over the chain's own operation routes (op:*, algebra,
        # compute), which the gate's diff showed must not be pre-empted
        if _math is not None and (not answered or not any(fam.startswith(p) for p in MATH_PATHS))                 and _math.directive_of(text) and _math.extract_math(text):
            org = self._c480_math()
            a = _run(org.answer, text) if org else None
            if a:
                return self._c480_math_reply(res, a, fam)
        # 2. RELATIONS
        if not answered or fam in RELATION_OUTRANKS:
            org = self._c480_rel()
            a = _run(org.answer, text) if org else None
            if a:
                return self._c480_rel_reply(res, a, fam)
        return res

    def _c480_dialogue_reply(self, res, a):
        out = dict(res)
        out.update({'status': 'answered', 'path': 'organ:dialogue>%s' % a['kind'], 'response': a['response'],
                    'references': [{'id': 'session:turn %d' % t, 'text': 'this conversation, turn %d' % t,
                                    'role': 'discourse'} for t in a.get('turns') or []],
                    'provenance': {'kind': 'organ_dialogue', 'move': a['kind'], 'turns': a.get('turns') or [],
                                   'parent_path': str(res.get('path', '')), 'parent_status': res.get('status')}})
        return out

    def _c480_math_reply(self, res, a, fam):
        m = a.get('method') or {}
        cite = ' [%s]' % m['id'] if m.get('id') else ''
        method = (' Method: %s, %s (%s).%s' % (m.get('title') or m.get('section'), m.get('section') or '',
                                               m.get('book') or '', cite)) if m else ''
        response = '[ev:derived] %s. In steps: %s. Checked: %s.%s' % (a['answer'], '; then '.join(a.get('steps') or []),
                                                                      a['check'], method)
        out = dict(res)
        out.update({'status': 'answered', 'path': 'organ:math>%s' % a['directive'], 'response': response.strip(),
                    'references': ([{'id': m['id'], 'text': '%s - %s' % (m.get('book'), m.get('title')), 'role': 'method'}]
                                   if m.get('id') else []),
                    'provenance': {'kind': 'organ_math', 'directive': a['directive'], 'check': a['check'],
                                   'parent_path': str(res.get('path', '')), 'parent_status': res.get('status')}})
        return out

    def _c480_rel_reply(self, res, a, fam):
        sent = a.get('sentence') or ''
        ev = [e for e in a.get('evidence') or [] if e]
        cites = ' '.join('[%s]' % e for e in ev if not str(e).startswith('wd:'))
        facts = '; '.join(e for e in ev if str(e).startswith('wd:'))
        response = '[ev:direct] %s. %s %s (typed relations: %s)' % (a['answer'], sent, cites, facts)
        out = dict(res)
        out.update({'status': 'answered', 'path': 'organ:relation>%s' % '>'.join(a.get('trace') or []),
                    'response': ' '.join(response.split()),
                    'references': [{'id': e, 'text': sent if not str(e).startswith('wd:') else e, 'role': 'relation'}
                                   for e in ev],
                    'provenance': {'kind': 'organ_relation', 'trace': a.get('trace'), 'expanded': a.get('expanded'),
                                   'parent_path': str(res.get('path', '')), 'parent_status': res.get('status')}})
        return out

    # ================================================================ vessels (from w478)

    def _c478_db(self):
        c = getattr(self, '_c478_conn', None)
        if c is None:
            c = sqlite3.connect(str(VESSEL_DB), timeout=15, check_same_thread=False)
            c.execute('PRAGMA journal_mode=WAL')
            c.execute('PRAGMA busy_timeout=15000')
            c.execute('CREATE TABLE IF NOT EXISTS vessel (key TEXT PRIMARY KEY, id TEXT, weight REAL, first_ts REAL, '
                      'last_ts REAL, named INTEGER, data TEXT)')
            c.execute('CREATE INDEX IF NOT EXISTS vessel_weight ON vessel(weight DESC, first_ts)')
            c.execute('CREATE TABLE IF NOT EXISTS meta (k TEXT PRIMARY KEY, v TEXT)')
            self._c478_conn = c
        return c

    def _c478_ready(self) -> bool:
        if self._measuring():
            return False
        try:
            r = self._c478_db().execute("SELECT v FROM meta WHERE k='imported'").fetchone()
            return bool(r and r[0] == '1')
        except Exception:  # noqa: BLE001
            return False

    # ------------------------------------------------------------ reception (w175 semantics, one row)
    def _receive(self, surface: str, session_id: str, result: dict) -> tuple[dict, bool]:
        if not self._c478_ready():
            return super()._receive(surface, session_id, result)
        key = _w175._norm(surface)
        now = time.time()
        is_person = not str(session_id).startswith(('loop-', 'stimuli', 'probe'))
        db = self._c478_db()
        with _LOCK:
            db.execute('BEGIN IMMEDIATE')
            try:
                row = db.execute('SELECT data FROM vessel WHERE key=?', (key,)).fetchone()
                if row is None:
                    nxt = int((db.execute("SELECT v FROM meta WHERE k='next'").fetchone() or ['1'])[0])
                    slot, question = _w175._slot_for(surface)
                    v = {'id': 'v%04d' % nxt, 'surface': surface[:160], 'first_ts': now, 'last_ts': now,
                         'count': 0, 'person_asks': 0, 'sessions': [], 'failed': [], 'slot': slot,
                         'question': question, 'attempts': [], 'residue': [], 'name': None}
                    db.execute("INSERT OR REPLACE INTO meta VALUES ('next', ?)", (str(nxt + 1),))
                    reinforced = False
                else:
                    v = json.loads(row[0])
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
                db.execute('INSERT OR REPLACE INTO vessel VALUES (?,?,?,?,?,?,?)',
                           (key, v['id'], v['weight'], v['first_ts'], v['last_ts'], 1 if v.get('name') else 0,
                            json.dumps(v)))
                db.execute('COMMIT')
            except Exception:
                db.execute('ROLLBACK')
                raise
        self._event('reinforce' if reinforced else 'open', vessel=v['id'], surface=v['surface'][:80],
                    weight=v['weight'], count=v['count'], session=str(session_id)[:40], failed=failed)
        if reinforced:
            try:
                with open(_w175.REQUESTS, 'a', encoding='utf-8') as f:
                    f.write(json.dumps({'vessel': v['id'], 'surface': v['surface'], 'weight': v['weight'],
                                        'count': v['count'], 'slot': v['slot'], 'question': v['question'],
                                        'failed': v['failed'],
                                        'ts': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}) + '\n')
            except Exception:  # noqa: BLE001
                pass
        return v, reinforced

    # ------------------------------------------------------------ register (w175 text, indexed read)
    def _register(self, s: str, session_id: str) -> dict:
        if not self._c478_ready():
            return super()._register(s, session_id)
        db = self._c478_db()
        held = db.execute('SELECT COUNT(*) FROM vessel').fetchone()[0]
        vs = [json.loads(r[0]) for r in db.execute('SELECT data FROM vessel ORDER BY weight DESC, first_ts LIMIT 3')]
        q = self._paths_q(session_id)
        prev = q[-1].get('turn', 0) if len(q) else 0
        touched = [e.get('vessel') for e in q if e.get('vessel')]
        if not vs:
            body = 'I hold no unnamed shapes yet; every question so far was answered or was never kept [vessel:none].'
            cited_ids = []
        else:
            parts = []
            for v in vs:
                parts.append('"%s" [vessel:%s], weight %s, asked %d times, what I lack is %s'
                             % (v['surface'], v['id'], v.get('weight', 0), v.get('count', 0), v.get('question', 'a bound')))
            body = ('I hold %d unnamed shape%s that I cannot yet name. The heaviest: %s. Weight decides what I weave next; '
                    'a shape is named only when a route carries it with declared bounds.'
                    % (held, '' if held == 1 else 's', '; '.join(parts)))
            cited_ids = [v['id'] for v in vs]
        result = {'status': 'answered', 'path': 'vessel:register', 'response': body,
                  'provenance': {'kind': 'vessel_register', 'vessels': cited_ids, 'held': held}}
        rec = {'turn': prev + 1, 'in_surface': s[:120], 'in_form': ['vessel_register'],
               'operator': 'vessel:register', 'out_status': 'answered',
               'in_terms': sorted(content_terms(s)), 'out_terms': [], 'relation': {},
               'carried_from_prior': ['vessel:' + t for t in touched[-3:]],
               'continuity_lexical': bool(touched), 'continuity': bool(prev and touched),
               'citations': 0, 'residual': None, 'cost_ms': 0.0,
               'verified_warrant': {'kind': 'vessel_register',
                                    'steps': ['query vessels.sqlite3', 'order by weight desc',
                                              'report top %d of %d' % (len(vs), held)]}}
        self._recite(rec, s, body)
        q.append(rec)
        self._event('register', session=str(session_id)[:40], held=held, cited=cited_ids)
        return result
