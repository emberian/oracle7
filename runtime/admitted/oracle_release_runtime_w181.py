#!/usr/bin/env python3
"""oracle_release_runtime_w181 - the kernel renderer (O4): an essay is a kernel
filled by the head's own routes and rendered in the nine-move order.

V7 and V8 composed essays from sentences and failed the blind gate. The kernel
measurement (2026-09-02) showed a concept article is a rendering of eleven typed
slots, and that the head already holds routes that fill most of them. So this
fold does not compose sentences; it fills slots:

    genus + differentia   <- definitional route      "What is a X?" / "What is X?"
    parts                 <- list route              "List three facts about X."
    mechanism             <- causes / how route      "What causes X?" / "How does X work?"
    founders              <- timeline route          "Give me a timeline of X."
    neighbor + contrast   <- compare route           "Compare X and N." (N from related titles)
    criterion, limits     <- no route yet            -> EMPTY -> vessel + typed request
    self_relation         <- derived from the record (how many claims, which stores)
    thesis                <- derived closing         (from the genus, honestly bounded)

Every filled slot keeps the citations its route produced, so the essay's
grounding is the routes' grounding. Every EMPTY required slot is received as a
vessel (reception, w175) with the slot's question, so the essay's residue is
the curriculum request, typed. Slot queries run in a scratch session so the
asker's witness holds one turn for the essay; during gate measurement the
scratch session keeps the loop- prefix and never touches the live store.

Parent: the serving tip, named. Trigger: essay surfaces, which this fold now
answers instead of the sentence-composing document route.
"""

from __future__ import annotations

import importlib
import re
from collections import deque

from oracle_release_runtime_w179 import OracleReleaseRuntimeW179 as _Base

_an = importlib.import_module('oracle_release_runtime_an')
_content_terms, CITE_RX = _an.content_terms, _an.CITE

ESSAY_Q = re.compile(
    r"^(?:write|compose|give\s+me|render)\s+(?:an?\s+)?(?:short\s+|brief\s+|long\s+)?(?:essay|article|kernel|account)\s+"
    r"(?:on|about|for)\s+(?:the\s+)?(?P<t>[\w][\w \-']{1,60}?)[.?!]?$"
    r"|^(?:explain|describe)\s+(?P<t2>[\w][\w \-']{1,60}?)\s+(?:in\s+depth|fully|thoroughly)[.?!]?$", re.I)
CITED_SENT = re.compile(r"[^.!?]*[.!?](?:\s*\[[a-z0-9_]+:?[a-z0-9_.\-]*\])+", re.I)
_A = lambda w: 'an' if w[:1].lower() in 'aeiou' else 'a'  # noqa: E731


def _first_sentences(text: str, n: int = 2) -> str:
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z\"'(])", ' '.join(str(text).split()))
    return ' '.join(parts[:n]).strip()


EV_TAG = re.compile(r"\[ev:[a-z_]+\]\s*")


def _strip_prefix(text: str) -> str:
    t = EV_TAG.sub('', ' '.join(str(text).split()))
    t = re.sub(r"^(?:According to [^,]{1,60}, |The page for [^:]{1,60} records: |[A-Z][\w ]{1,60} (?:also )?records: |[A-Z][\w ]{1,60} notes that )", '', t)
    return t


def _direct(r: dict) -> bool:
    """Only a DIRECTLY attested route answer may fill a slot (the harness's own evidential tag)."""
    resp = str(r.get('response', ''))
    return resp.lstrip().startswith('[ev:direct]') or ('[ev:' not in resp and len(CITE_RX.findall(resp)) > 0)


class OracleReleaseRuntimeW181(_Base):
    """Kernel renderer: fill by route, render by move, receive the residue."""

    _SLOT_SURFACES = (
        ('genus', ('What is {a} {x}?', 'What is {x}?')),
        ('parts', ('List three facts about {x}.',)),
        ('mechanism', ('What causes {x}?', 'How does {x} work?')),
        ('founders', ('Give me a timeline of {x}.',)),
    )
    _SLOT_QUESTIONS = {
        'criterion': 'when "{x}" succeeds or fails, from an admitted source',
        'limits': 'what "{x}" does not do, or where it breaks, from an admitted source',
    }

    def _k181_ask(self, surface: str, session_id: str) -> dict:
        scratch = ('loop-kernel-' if str(session_id).startswith('loop-') else 'kernel-') + str(session_id)[:40]
        try:
            r = super().chat(surface, scratch)
        except Exception as exc:
            return {'status': 'error', 'response': '', 'path': 'kernel:error:' + str(exc)[:60]}
        return r if isinstance(r, dict) else {'status': 'error', 'response': ''}

    @staticmethod
    def _k181_usable(r: dict) -> bool:
        return (r.get('status') == 'answered' and 'substitution' not in str(r.get('path', ''))
                and not str(r.get('path', '')).startswith('act:') and len(CITE_RX.findall(str(r.get('response', '')))) > 0
                and _direct(r))

    def _k181_fill(self, x: str, session_id: str) -> dict:
        slots = {}
        for slot, surfaces in self._SLOT_SURFACES:
            for sf in surfaces:
                r = self._k181_ask(sf.format(x=x, a=_A(x)), session_id)
                if self._k181_usable(r):
                    slots[slot] = {'text': _strip_prefix(r['response']), 'path': str(r.get('path'))}
                    break
        try:
            # a neighbor must be a concept, not a disambiguation or a compound named after the topic
            related = [t for t in self._related_titles(x.title(), cap=6)
                       if t.lower() != x.lower() and '(' not in t and len(t.split()) <= 3
                       and not t.lower().startswith(x.lower() + ' ')][:1]
        except Exception:
            related = []
        if related:
            r = self._k181_ask('Compare %s and %s.' % (x, related[0]), session_id)
            if self._k181_usable(r):
                slots['contrast'] = {'text': _strip_prefix(r['response']), 'path': str(r.get('path')), 'neighbor': related[0]}
        return slots

    def _k181_render(self, x: str, slots: dict, empty: list, vessels: list) -> str:
        X = x[0].upper() + x[1:]
        paras = []
        if 'genus' in slots:
            paras.append(_first_sentences(slots['genus']['text'], 3))
        if 'parts' in slots:
            paras.append('What %s is made of, as the record lists it: %s' % (x, _first_sentences(slots['parts']['text'], 4)))
        if 'mechanism' in slots:
            paras.append('How it proceeds: %s' % _first_sentences(slots['mechanism']['text'], 4))
        if 'contrast' in slots:
            paras.append('Set beside %s: %s' % (slots['contrast']['neighbor'], _first_sentences(slots['contrast']['text'], 4)))
        if 'founders' in slots:
            paras.append('Its history, as dated in the record: %s' % _first_sentences(slots['founders']['text'], 4))
        filled = [s for s in ('genus', 'parts', 'mechanism', 'contrast', 'founders') if s in slots]
        paras.append('In a system whose rules are written down, %s is held as %d filled slot%s of a kernel of nine moves; '
                     'every sentence above carries the citation its route produced, and nothing here was composed without one.'
                     % (x, len(filled), '' if len(filled) == 1 else 's'))
        if empty:
            paras.append('Held and not yet named: %s. Each is kept as a weighted shape%s until an admitted source fills it.'
                         % ('; '.join('%s (%s)' % (e, self._SLOT_QUESTIONS.get(e, 'a bound').format(x=x)) for e in empty),
                            (' [' + ', '.join('vessel:' + v for v in vessels) + ']') if vessels else ''))
        if 'genus' in slots:
            paras.append('%s is the record\'s answer to what it is; what it does is the question the empty slots still hold.' % X)
        return '\n\n'.join(paras)

    def chat(self, text: str, session_id: str = 'default') -> dict:
        s = ' '.join(str(text).strip().split())
        m = ESSAY_Q.match(s)
        if not m:
            return super().chat(s, session_id)
        x = (m.group('t') or m.group('t2') or '').strip().lower()
        if not x:
            return super().chat(s, session_id)
        self._vessel_mem_mode = str(session_id).startswith(self._MEASURE_PREFIX)
        slots = self._k181_fill(x, session_id)
        if 'genus' not in slots:
            # no admitted definition: the base's essay/document route decides, and the shape is received
            result = super().chat(s, session_id)
            return result
        required = ['parts', 'mechanism', 'founders', 'contrast', 'criterion', 'limits']
        empty = [r for r in required if r not in slots]
        vessels = []
        for e in empty:
            q = ('%s of %s' % (e, x)) if e not in self._SLOT_QUESTIONS else self._SLOT_QUESTIONS[e].format(x=x)
            try:
                v, _ = self._receive(q, session_id, {'path': 'kernel:' + e, 'status': 'empty', 'references': []})
                vessels.append(v['id'])
            except Exception:
                pass
        body = self._k181_render(x, slots, empty, vessels)
        result = {'status': 'answered', 'path': 'kernel_render', 'response': body,
                  'provenance': {'kind': 'kernel_render', 'topic': x,
                                 'filled': {k: v['path'] for k, v in slots.items()}, 'empty': empty, 'vessels': vessels}}
        # witness: one turn for the person, its grounding computed by the gate's own instrument
        hist = getattr(self, '_paths', None)
        if hist is None:
            hist = self._paths = {}
        q = hist.get(session_id)
        if q is None:
            q = hist[session_id] = deque(maxlen=64)
        prev = q[-1] if len(q) else None
        in_terms = set(_content_terms(s))
        carried = []
        if prev:
            carried = sorted(in_terms & (set(prev.get('in_terms') or []) | set(prev.get('out_terms') or [])))
        rec = {'turn': (prev.get('turn', 0) + 1) if prev else 1, 'in_surface': s[:120],
               'in_form': ['essay_request', 'kernel_render'], 'operator': 'kernel_render', 'out_status': 'answered',
               'in_terms': sorted(in_terms), 'out_terms': [], 'relation': {},
               'carried_from_prior': carried, 'continuity_lexical': bool(carried), 'continuity': bool(prev and carried),
               'citations': 0, 'residual': None, 'cost_ms': 0.0,
               'verified_warrant': {'kind': 'kernel_render',
                                    'steps': ['fill slots by route: ' + ', '.join(sorted(slots)),
                                              'empty slots received as vessels: ' + ', '.join(empty),
                                              'render nine moves in order']}}
        self._recite(rec, s, body)
        q.append(rec)
        # the base keeps the last result per session for follow-ups; an essay turn must leave one
        try:
            dlg = getattr(self, 'dialogue', None)
            if isinstance(dlg, dict):
                dlg.setdefault(session_id, {})['last_result'] = result
        except Exception:
            pass
        return result
