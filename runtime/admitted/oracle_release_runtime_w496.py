#!/usr/bin/env python3
"""oracle_release_runtime_w496 - the SELF term: Oracle7's ego and relational moves (layer 0 = constitution_resonant_self_v1).

After the knowledge organs, the conversation turns still failing are RELATIONAL: an opener hands the listener a position
and a human second speaker answers from it (DailyDialog human act labels: a directive is answered by a commissive or a
question, almost never by information). With no self term, a reply can only be retrieval or refusal. This fold connects
organ_self_v1:
  role / customer   the turn casts Oracle7 as clerk (or the person as clerk): it plays the role, fills the slot from the
                    turn (destination, item), and says in one clause that nothing real is booked
  vocative          addressed by another name: says who it is and offers what it can
  remark            a bodily predicate put to it (drive, sleep, eat, a face): answered honestly from the frozen IDENTITY
  compliment        received, honestly
  self-question     what it is doing / thinking / its stance / what it is: answered from measured state - the turn count,
                    and the OPEN END: the last subject is resonant / thinly bound / unbound with its passage count
  disclosure        the person's news: an appraised acknowledgement (feeling shapes the voice only), one grounded
                    sentence on the named place or thing, a question back
Where it speaks: only where the chain could not PARSE the turn or the conversation organ had only a weak reply (a canned
'addressed' line or a bare statement acknowledgement); never over an evidence-based withheld decline.
Measured by relational_instrument_v1 (reply act vs HUMAN second-speaker acts, with constant-act and shuffle mutants) and
the blind human panel. Parent: the serving tip, named. Methods _c496_.
"""

from __future__ import annotations

from oracle_release_runtime_w494 import OracleReleaseRuntimeW494 as _Base

try:
    import organ_self_v1 as _self
except Exception:  # noqa: BLE001
    _self = None
try:
    import oracle_release_runtime_w480 as _w480
    _run = _w480._run
except Exception:  # noqa: BLE001
    _run = None

WEAK = ('organ:converse>addressed', 'organ:converse>statement')


class OracleReleaseRuntimeW496(_Base):

    def _c496_org(self):
        o = getattr(self, '_c496_o', None)
        if o is None and _self is not None:
            try:
                conv = self._c494_org()
                o = self._c496_o = _self.SelfOrgan(conv) if conv else False
            except Exception:  # noqa: BLE001
                o = self._c496_o = False
        return o or None

    def chat(self, text: str, session_id: str = "default") -> dict:
        org = self._c496_org()
        if org is not None:
            try:
                org.remember(session_id)          # the autobiography counts every turn, answered or not
            except Exception:  # noqa: BLE001
                pass
        return super().chat(text, session_id)

    def _c480_dispatch(self, text, session_id, res):
        out = super()._c480_dispatch(text, session_id, res)
        if _run is None:
            return out
        path = str(out.get('path', ''))
        weak = path.startswith(WEAK)
        generic_self = path.startswith('act:about')     # the chain's one generic self-description
        if self._c480_answered(out) and not (weak or generic_self):
            return out
        parent = (out.get('provenance') or {}).get('parent_status') if weak else out.get('status')
        org = self._c496_org()
        a = _run(org.answer, text, session_id) if org else None
        if not a:
            return out
        if generic_self and a.get('kind') != 'self':
            return out                            # only a measured-state answer about itself replaces the generic one
        # an evidence-based decline is spoken over only by a move that asserts nothing about the world
        if str(parent) == 'withheld' and a.get('kind') not in _self.SELF_ONLY:
            return out
        new = dict(out)
        new.update({'status': 'answered', 'path': 'organ:self>%s' % a['kind'], 'response': a['response'],
                    'references': [{'id': c, 'text': c, 'role': 'self'} for c in a.get('cites') or []],
                    'provenance': {'kind': 'organ_self', 'move': a['kind'], 'appraisal': a.get('appraisal'),
                                   'parent_path': path, 'parent_status': parent}})
        return new
