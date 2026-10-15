#!/usr/bin/env python3
"""oracle_release_runtime_w498 - CORRECTNESS RELEASE: hollow answers made admitted organs unreachable.

Found on the live harness after w494 (2026-09-28): "tell me a joke" -> capability:summarize with status ANSWERED and
the text "No provenance-admitted material on tell me a joke is available to summarize." The chain reported a decline as
an answer, so the dispatch never offered the turn to the organs, and the joke store admitted in w494 (1,145 cited jokes)
could not be reached. That is a correctness defect in two ways: the status misreports what happened, and an admitted
capability is unreachable. This release treats a reply whose status says answered but whose text declines as the parse
failure it is - and only moves that assert no fact about the world may speak over it: the conversation organ's explicit
intents (joke, recipe, feelings, crisis) and the self organ's self-only moves. false_yes cannot rise through this door.

Scope, stated because the first w498 was rejected (continuation_taken 66 -> 61): the social moves (thanks / goodbye /
apology) are NOT in this release. Replacing the chain's acknowledgement closed six held-out threads its own reply had
kept open; those moves return later with panel items, because a new capability is new items, not an exemption.
Checks before submission: 0 route changes on the held-out conversation scripts, 0 regressions on the fixed list,
0 newly asserted must-decline items. Parent: the serving tip, named. Methods _c498_.
"""

from __future__ import annotations

import re

from oracle_release_runtime_w496 import OracleReleaseRuntimeW496 as _Base

try:
    import oracle_release_runtime_w480 as _w480
    _run = _w480._run
except Exception:  # noqa: BLE001
    _run = None

HOLLOW = re.compile(r"^\s*(?:\[[^\]]*\]\s*)?(?:no provenance-admitted material on .{1,120}? is available to summari[sz]e|"
                    r"i didn't fully parse that)", re.I)
INTENT_KINDS = {"joke", "recipe", "feelings", "safety"}


class OracleReleaseRuntimeW498(_Base):

    def _c480_dispatch(self, text, session_id, res):
        out = super()._c480_dispatch(text, session_id, res)
        if _run is None:
            return out
        path = str(out.get('path', ''))
        body = str(out.get('response', ''))
        # a hollow answer: status answered, text declines
        if self._c480_answered(out) and not path.startswith('organ:') and HOLLOW.search(body):
            conv = self._c494_org()
            a = _run(conv.answer, text) if conv else None
            if a and a.get('kind') in INTENT_KINDS:
                return self._c498_reply(out, 'organ:converse>%s' % a['kind'], a['response'], path, a.get('cites'))
            org = self._c496_org()
            a = _run(org.answer, text, session_id) if org else None
            if a and a.get('kind') in getattr(__import__('organ_self_v1'), 'SELF_ONLY', set()):
                return self._c498_reply(out, 'organ:self>%s' % a['kind'], a['response'], path)
        return out

    def _c498_reply(self, out, path, response, parent_path, cites=None):
        new = dict(out)
        new.update({'status': 'answered', 'path': path, 'response': response,
                    'references': [{'id': c, 'text': c, 'role': 'converse'} for c in cites or []],
                    'provenance': {'kind': 'organ_w498', 'parent_path': parent_path, 'parent_status': out.get('status'),
                                   'hollow': True}})
        return new
