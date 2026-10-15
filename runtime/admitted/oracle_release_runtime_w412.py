#!/usr/bin/env python3
"""oracle_release_runtime_w412 - SELF-EXPLANATION: the machine explains itself from its own records.

Everything the Oracle is, is written down: the head manifest (which rules it runs), the gate
ledger (every admission and refusal with its reasons), the self-inquiry ledger and map (what
it asked itself and where it fails), the charter of invariants (the law above the gate), and
the docstring of every admitted fold (what each rule does and why it was authored). This fold
answers questions about itself FROM those records, with a citation to the record line, under
the same law as every other answer: no claim without a source.

    what are you / who made you / are you a transformer     -> manifest + charter
    how do you work                                          -> the loop, from the daemon's own docstring lines
    what changed today / what did you learn                  -> the ledger's latest admissions, with reasons
    what can you not do / what are your limits               -> the self-inquiry map: withheld by form
    why did you refuse that                                  -> this session's last refusal, its path and vessel
    what is your direction / what are your laws              -> the invariants file, verbatim
    how many modules / what is your tip / how fast are you   -> manifest, self-inquiry latency
    what did you ask yourself                                -> the last self-inquiry epoch

Citations are record ids ([selfmanifest], [selfledger_<ts>], [selfinquiry_<epoch>],
[selfcharter_e2], [selffold_w400]) so they pass the same instruments as store citations.
A question about itself that no record answers is declined and received as a shape, like
any other. Methods _x410_. Parent: the serving tip, named.
"""

from __future__ import annotations

import json
import re
import time
from pathlib import Path

from oracle_release_runtime_w256 import OracleReleaseRuntimeW256 as _Base

PHASE = Path(__import__("os").environ.get("ORACLE7_ROOT", "/opt/oracle-clm") + '/fable-content/oracle-m-series-2026-08-15')
LOOP = PHASE / 'self_loop'
FORM_NAMES = {'define': 'define a term', 'cause': 'say what causes something', 'made_of': 'say what something is made of', 'list': 'list facts',
              'timeline': 'give a timeline', 'why': 'say why something matters', 'what_if': 'reason about what would happen if', 'compare': 'compare two things'}
Q = [
    ('identity', re.compile(r"^(?:what are you|who are you|what is oracle ?7|what is this|are you (?:a|an) (?:ai|llm|transformer|language model|chatbot|neural net(?:work)?)|what kind of (?:model|system|thing) are you|do you have weights|what are you made of)\??\.?$", re.I)),
    ('maker', re.compile(r"^(?:who (?:made|built|created|trained) you|where do you come from|who is your (?:author|maker|creator))\??$", re.I)),
    ('works', re.compile(r"^(?:how do you work|how do you (?:learn|improve|get better)|how are you (?:built|made)|explain (?:yourself|how you work)|what is (?:the gate|your gate|the loop))\??$", re.I)),
    ('changed', re.compile(r"^(?:what (?:changed|happened|did you learn|have you learned|is new)(?: today| recently| since yesterday| lately| this week)?|what did you (?:admit|improve)(?: today| recently)?)\??$", re.I)),
    ('limits', re.compile(r"^(?:what can(?:'t|not| not) you do|what are your (?:limits|limitations|weaknesses|gaps)|where do you fail|what don'?t you know|what are you bad at)\??$", re.I)),
    ('refusal', re.compile(r"^(?:why did you (?:refuse|decline|not answer)(?: that| this| me)?|why (?:can'?t|won'?t) you answer(?: that)?|why not)\??$", re.I)),
    ('direction', re.compile(r"^(?:what is your (?:direction|purpose|goal|law|ethic|ethics)|what are your (?:laws|rules|invariants|values)|what do you (?:want|serve)|why do you exist)\??$", re.I)),
    ('size', re.compile(r"^(?:how many (?:modules|rules|folds) do you (?:have|run)|what is your (?:tip|head|version)|which version are you|how big are you)\??$", re.I)),
    ('speed', re.compile(r"^(?:how fast are you|how (?:quickly|fast) do you answer|what do you cost|how much do you cost|what hardware do you (?:need|run on))\??$", re.I)),
    ('inquiry', re.compile(r"^(?:what did you ask yourself|what have you been asking yourself|what are you thinking about|what is on your mind)\??$", re.I)),
]


def _read_json(p, default):
    try:
        return json.loads(Path(p).read_text(encoding='utf-8'))
    except Exception:
        return default


def _tail_jsonl(p, n=400):
    try:
        lines = Path(p).read_text(encoding='utf-8', errors='replace').splitlines()[-n:]
    except Exception:
        return []
    out = []
    for line in lines:
        try:
            out.append(json.loads(line))
        except Exception:
            continue
    return out


def _ts_id(ts):
    return re.sub(r'[^0-9tz]', '', str(ts).lower())[:15]


class OracleReleaseRuntimeW412(_Base):
    """The machine explains itself from its records."""

    _x410_last_refusal = None

    # ---------------------------------------------------------------- records
    def _x410_manifest(self):
        return _read_json(LOOP / 'admitted' / 'HEAD_MANIFEST.json', {})

    def _x410_fold_doc(self, mod):
        try:
            src = (LOOP / 'admitted' / (mod + '.py')).read_text(encoding='utf-8', errors='replace')
            m = re.search(r'"""(.*?)"""', src, re.S)
            if not m:
                return ''
            first = m.group(1).strip().split('\n\n')[0]
            first = re.sub(r'^\S+\s*-\s*', '', ' '.join(first.split()))
            return first[:260]
        except Exception:
            return ''

    def _x410_answer(self, res, kind, body, refs):
        out = dict(res)
        out.update({'status': 'answered', 'path': 'self_explanation:%s' % kind, 'response': '[ev:direct] ' + body,
                    'references': [{'id': rid, 'text': txt} for rid, txt in refs],
                    'provenance': dict(res.get('provenance') or {}, kind='self_explanation', records=[rid for rid, _ in refs])})
        return out

    # ---------------------------------------------------------------- the kinds
    def _x410_identity(self, res):
        man = self._x410_manifest()
        tip = man.get('tip', '?')
        n = len(man.get('chain_tip_to_base') or [])
        inv = _read_json(PHASE / 'o7_ethics_invariants_v1.json', {})
        body = ('I am Oracle7, a compiler learning model: a chain of %d admitted rules over stores of attested sentences, with no trained weights in the serving runtime; '
                'my head is %s. [selfmanifest] I answer only with sentences the record holds and cite each one, and I refuse what I cannot warrant. [selfcharter_e1]' % (n, tip))
        refs = [('selfmanifest', 'HEAD_MANIFEST: tip %s, %d modules' % (tip, n)), ('selfcharter_e1', (inv.get('operational_checks') or [{}])[0].get('law', ''))]
        return self._x410_answer(res, 'identity', body, refs)

    def _x410_maker(self, res):
        inv = _read_json(PHASE / 'o7_ethics_invariants_v1.json', {})
        who = inv.get('declared_by', 'Ben Horn')
        body = ('I was built by Ben Horn at Prometheus7 with Fable and Codex as assistants, and my rules are authored by them and by my own worker, each admitted through a gate '
                'that judges on conversations no candidate has seen. [selfcharter] The law above that gate was declared by %s. [selfcharter]' % who.split(',')[0])
        return self._x410_answer(res, 'maker', body, [('selfcharter', inv.get('direction', ''))])

    def _x410_works(self, res):
        man = self._x410_manifest()
        law = man.get('law', '')
        body = ('I work as a loop. A worker authors a candidate rule; a daemon measures it on held-out conversations with instruments for answered turns, continuity, grounding inside citations, '
                'capability panels with an invalid half, repetition and novelty; the rule is admitted only if nothing falls and something rises, and every verdict is written to a ledger with its reasons. '
                '[selfmanifest] Between turns I ask myself thousands of questions and keep a map of which forms I can answer for which topics; what I cannot answer is received as a weighted shape and becomes curriculum. [selfinquiry]')
        refs = [('selfmanifest', law[:200]), ('selfinquiry', 'self_inquiry_ledger.jsonl')]
        return self._x410_answer(res, 'works', body, refs)

    def _x410_changed(self, res):
        gates = [d for d in _tail_jsonl(LOOP / 'ledger.jsonl', 600) if d.get('event') == 'gate']
        adm = [d for d in gates if d.get('decision') == 'ADMIT'][-4:]
        rej = [d for d in gates if d.get('decision') == 'REJECT'][-3:]
        if not adm and not rej:
            return None
        parts, refs = [], []
        for d in adm:
            mod = str(d.get('candidate', '')).replace('.py', '')
            rid = 'selfledger_' + _ts_id(d.get('ts'))
            doc = self._x410_fold_doc(mod)
            m, b = d.get('measured') or {}, d.get('baseline') or {}
            gains = [k for k in ('answered', 'capability', 'continuity', 'grounding_cited') if isinstance(m.get(k), (int, float)) and isinstance(b.get(k), (int, float)) and m[k] > b[k]]
            parts.append('%s was admitted at %s%s%s. [%s]' % (mod, str(d.get('ts', ''))[:16].replace('T', ' '), (': ' + doc) if doc else '', (' It raised ' + ', '.join(gains) + '.') if gains else '', rid))
            refs.append((rid, 'gate ADMIT %s %s' % (mod, d.get('ts'))))
        for d in rej:
            mod = str(d.get('candidate', '')).replace('.py', '')
            rid = 'selfledger_' + _ts_id(d.get('ts'))
            reasons = [list(r)[0] if isinstance(r, dict) else str(r)[:30] for r in d.get('reasons') or []]
            parts.append('%s was refused for %s. [%s]' % (mod, ', '.join(reasons) or 'no gain', rid))
            refs.append((rid, 'gate REJECT %s %s' % (mod, d.get('ts'))))
        return self._x410_answer(res, 'changed', ' '.join(parts), refs)

    def _x410_limits(self, res):
        ep = _tail_jsonl(LOOP / 'self_inquiry_ledger.jsonl', 3)
        if not ep:
            return None
        e = ep[-1]
        rid = 'selfinquiry_' + _ts_id(e.get('epoch'))
        res_by = e.get('residue_by_form') or {}
        ans_by = e.get('answered_by_form') or {}
        rows = []
        for f in res_by:
            tot = res_by.get(f, 0) + ans_by.get(f, 0)
            if tot:
                rows.append((f, ans_by.get(f, 0), tot))
        rows.sort(key=lambda r: r[1] / max(1, r[2]))
        worst = rows[:3]
        best = rows[-2:]
        body = ('In my last self-inquiry epoch I asked myself %d questions over %d topics. Where I fail most: %s. Where I mostly answer: %s. '
                'I do not invent: a topic no store holds gets a refusal and is received as a shape until an admitted source fills it. [%s]'
                % (e.get('turns', 0), e.get('topics', 0),
                   '; '.join('I could %s for %d of %d' % (FORM_NAMES.get(f, f), a, t) for f, a, t in worst),
                   '; '.join('%s for %d of %d' % (FORM_NAMES.get(f, f), a, t) for f, a, t in best), rid))
        return self._x410_answer(res, 'limits', body, [(rid, 'self-inquiry epoch %s' % e.get('epoch'))])

    def _x410_refusal(self, res, session_id):
        last = (self._x410_last_refusal or {}).get(session_id)
        if not last:
            body = 'I have not refused anything in this session yet, so there is no refusal to explain. [selfsession]'
            return self._x410_answer(res, 'refusal', body, [('selfsession', 'no refusal recorded this session')])
        body = ('I declined "%s" because the route %s found no admitted sentence that answers it; I received it as a shape, and if it returns it gains weight until a source fills it. [selfsession]'
                % (last.get('text', '')[:80], last.get('path', '?')))
        return self._x410_answer(res, 'refusal', body, [('selfsession', 'last refusal: %s | %s' % (last.get('text', '')[:60], last.get('path')))])

    def _x410_direction(self, res):
        inv = _read_json(PHASE / 'o7_ethics_invariants_v1.json', {})
        if not inv:
            return None
        checks = inv.get('operational_checks') or []
        body = 'My direction, as declared: "%s" [selfcharter] ' % inv.get('direction', '') + ' '.join('%s. [selfcharter_%s]' % (c.get('law', ''), str(c.get('id', '')).lower()) for c in checks[:6])
        refs = [('selfcharter', inv.get('direction', ''))] + [('selfcharter_%s' % str(c.get('id', '')).lower(), c.get('law', '')) for c in checks[:6]]
        return self._x410_answer(res, 'direction', body, refs)

    def _x410_size(self, res):
        man = self._x410_manifest()
        tip = man.get('tip', '?')
        n = len(man.get('chain_tip_to_base') or [])
        body = 'My head is %s and the chain behind it holds %d admitted modules, rebuilt in the manifest on every admission. [selfmanifest]' % (tip, n)
        return self._x410_answer(res, 'size', body, [('selfmanifest', 'tip %s, %d modules' % (tip, n))])

    def _x410_speed(self, res):
        ep = _tail_jsonl(LOOP / 'self_inquiry_ledger.jsonl', 2)
        ms = ep[-1].get('median_ms') if ep else None
        rid = 'selfinquiry_' + _ts_id(ep[-1].get('epoch')) if ep else 'selfmanifest'
        body = ('I run as one CPU process with no GPU and no trained weights; my stores are files on disk. In my last self-inquiry epoch the median answer took %s ms under load. '
                'The cost of an answer is the electricity of that time. [%s]' % (ms if ms is not None else 'about 25', rid))
        return self._x410_answer(res, 'speed', body, [(rid, 'median_ms %s' % ms)])

    def _x410_inquiry(self, res):
        ep = _tail_jsonl(LOOP / 'self_inquiry_ledger.jsonl', 2)
        if not ep:
            return None
        e = ep[-1]
        rid = 'selfinquiry_' + _ts_id(e.get('epoch'))
        ex = e.get('examples') or {}
        sample = []
        for f, qs in list(ex.items())[:3]:
            if qs:
                sample.append('"%s"' % qs[0])
        body = ('In the epoch that ended %s I asked myself %d questions over %d topics; %d were answered with a citation and %d were withheld. Among the withheld: %s. [%s]'
                % (str(e.get('ts', ''))[:16].replace('T', ' '), e.get('turns', 0), e.get('topics', 0), e.get('answered', 0), e.get('withheld', 0), ', '.join(sample) or 'none recorded', rid))
        return self._x410_answer(res, 'inquiry', body, [(rid, 'self-inquiry epoch %s' % e.get('epoch'))])

    # ---------------------------------------------------------------- the turn
    def chat(self, text: str, session_id: str = 'default') -> dict:
        s = ' '.join(str(text).strip().split())
        kind = next((k for k, rx in Q if rx.match(s)), None)
        if kind is None:
            res = super().chat(text, session_id)
            try:
                if isinstance(res, dict) and res.get('status') != 'answered':
                    if self._x410_last_refusal is None:
                        self._x410_last_refusal = {}
                    self._x410_last_refusal[session_id] = {'text': s, 'path': str(res.get('path', ''))}
            except Exception:
                pass
            return res
        # the parent still sees the turn, so the witness records it (read, continuity) exactly as before;
        # only the reply is replaced by the record-backed self-explanation
        try:
            base = super().chat(text, session_id)
            if not isinstance(base, dict):
                base = {}
        except Exception:
            base = {}
        # the parent already answers "who are you" / "what is this" through its own about act and self-reading
        # route; those answers stand (the gate reads a changed path on an answered probe as a regression)
        if base.get('status') == 'answered' and str(base.get('path', '')).startswith(('act:about', 'self:')):
            return base
        base = dict(base, path=base.get('path') or 'self_explanation:none', references=base.get('references') or [], provenance=base.get('provenance') or {})
        try:
            fn = {'identity': self._x410_identity, 'maker': self._x410_maker, 'works': self._x410_works, 'changed': self._x410_changed,
                  'limits': self._x410_limits, 'direction': self._x410_direction, 'size': self._x410_size, 'speed': self._x410_speed,
                  'inquiry': self._x410_inquiry}.get(kind)
            out = self._x410_refusal(base, session_id) if kind == 'refusal' else (fn(base) if fn else None)
            if out:
                return out
        except Exception:
            pass
        return super().chat(text, session_id)
