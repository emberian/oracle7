#!/usr/bin/env python3
"""oracle_release_runtime_w500 - SOCIAL second pair parts, with the instrument that sees them (panel family
open_social, kind "social", v23: 188 DailyDialog test utterances, judge validated - references 188/188, echo 0,
wrong-act 0, cold acknowledgement 0).

Thanks -> welcome, farewell -> farewell, apology -> absolution, how-are-you -> Oracle7's own state (turn count;
nothing claimed that it lacks). organ_social_v1 speaks ONLY over an unanswered turn or the chain's COLD acknowledgement
("Noted. The session state is kept; ask on.") - never over a reply that carries the thread: the chain already answers a
mid-conversation "thanks" with "Glad that helps. We were on Colosseum: ..." and replacing that closed six held-out
threads in the first w498 (rejected, continuation_taken 66 -> 61). Never over a withheld decline.
Parent: the serving tip, named. Methods _c500_.
"""

from __future__ import annotations

import re

from oracle_release_runtime_w498 import OracleReleaseRuntimeW498 as _Base

try:
    import organ_social_v1 as _soc
except Exception:  # noqa: BLE001
    _soc = None
try:
    import oracle_release_runtime_w480 as _w480
    _run = _w480._run
except Exception:  # noqa: BLE001
    _run = None

ACK_PATHS = ('arb:act_acknowledge', 'act:acknowledge')
COLD_ACK = re.compile(r"^\s*Noted\.\s+The session state is kept", re.I)


class OracleReleaseRuntimeW500(_Base):

    def _c500_soc(self):
        o = getattr(self, '_c500_s', None)
        if o is None and _soc is not None:
            o = self._c500_s = _soc.SocialOrgan()
        return o

    def _c500_turns(self, session_id):
        org = self._c496_org()
        try:
            return org.sessions.get(session_id, {}).get("turns") if org else None
        except Exception:  # noqa: BLE001
            return None

    def _c480_dispatch(self, text, session_id, res):
        out = super()._c480_dispatch(text, session_id, res)
        if _run is None or str(out.get('status')) == 'withheld':
            return out
        path, body = str(out.get('path', '')), str(out.get('response', ''))
        cold = path.startswith(ACK_PATHS) and COLD_ACK.search(body)
        if self._c480_answered(out) and not cold:
            return out
        soc = self._c500_soc()
        a = _run(soc.answer, text, self._c500_turns(session_id)) if soc else None
        if not a:
            return out
        new = dict(out)
        new.update({'status': 'answered', 'path': 'organ:social>%s' % a['kind'], 'response': a['response'],
                    'references': [], 'provenance': {'kind': 'organ_social', 'move': a['kind'], 'parent_path': path,
                                                     'parent_status': out.get('status')}})
        return new
