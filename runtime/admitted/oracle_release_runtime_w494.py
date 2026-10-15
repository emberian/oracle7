#!/usr/bin/env python3
"""oracle_release_runtime_w494 - GENERAL CONVERSATION: the turns people actually open with.

Measured on the serving head (w492) with conv_instrument_v1 (real opening turns: DailyDialog + OpenAssistant; a turn is
good only if it is not a refusal, is on topic, and adds substance; an echo mutant scores 0): development 600 turns ->
44 good, 542 refused ("I didn't fully parse that" for feelings, advice, opinions, jokes, recipes, statements; "can you
explain how vaccines work" read as a question about the word "Can").
This fold connects organ_converse_v1:
  1. NORMALISE conversational wrappers before the chain reads the turn ("can you explain X" -> "Explain X", "tell me
     something interesting about X" -> "Tell me about X", "what's" -> "what is")
  2. FEELINGS - honest acknowledgement, then cited sentences from the relevant page (Stress management, Loneliness...);
     self-harm language -> care and a crisis line (988 / Samaritans), never a refusal
  3. OPINIONS - no personal opinions or favourites, then what the record says about the subject
  4. JOKES and RECIPES - two new public-domain stores (Project Gutenberg: 1,145 content-filtered jokes, 2,533 recipes),
     every item cited to its book
  5. STATEMENTS - acknowledgement, one grounded sentence on the subject, a question back; lines addressed to a person or
     a role - honestly: an AI, and what it can do (necessarily canned; reported separately, never counted as knowledge)
The organ runs only where the chain could not PARSE the turn (a clarification); over an evidence-based withheld
decline only the crisis path speaks, and its request move answers only definitional requests (reach is not answer).
Parent: the serving tip, named. Methods _c494_.
"""

from __future__ import annotations

from oracle_release_runtime_w492 import OracleReleaseRuntimeW492 as _Base

try:
    import organ_converse_v1 as _conv
except Exception:  # noqa: BLE001
    _conv = None
try:
    import oracle_release_runtime_w480 as _w480
    _run = _w480._run
except Exception:  # noqa: BLE001
    _run = None


class OracleReleaseRuntimeW494(_Base):

    def _c494_org(self):
        o = getattr(self, '_c494_o', None)
        if o is None and _conv is not None:
            try:
                rel = self._c480_rel()
                o = self._c494_o = _conv.ConverseOrgan(rel.r)
            except Exception:  # noqa: BLE001
                o = self._c494_o = False
        return o or None

    def chat(self, text: str, session_id: str = "default") -> dict:
        t = text
        if _conv is not None and isinstance(text, str):
            try:
                n = _conv.normalize(text)
                if n and n.strip(" ?.!").lower() != text.strip(" ?.!").lower():
                    t = n
            except Exception:  # noqa: BLE001
                t = text
        return super().chat(t, session_id)

    def _c480_dispatch(self, text, session_id, res):
        out = super()._c480_dispatch(text, session_id, res)
        if _run is None or self._c480_answered(out):
            return out
        org = self._c494_org()
        a = _run(org.answer, text) if org else None
        if not a:
            return out
        # a WITHHELD decline is the chain's evidence-based judgement (does not follow, answer absent from every store);
        # only the crisis path may speak over it (gate diff 2026-09-28: taking those over raised false_yes 22 -> 72)
        if str(out.get('status')) == 'withheld' and a.get('kind') != 'safety':
            return out
        new = dict(out)
        new.update({'status': 'answered', 'path': 'organ:converse>%s' % a['kind'], 'response': a['response'],
                    'references': [{'id': c, 'text': c, 'role': 'converse'} for c in a.get('cites') or []],
                    'provenance': {'kind': 'organ_converse', 'move': a['kind'],
                                   'parent_path': str(out.get('path', '')), 'parent_status': out.get('status')}})
        return new
