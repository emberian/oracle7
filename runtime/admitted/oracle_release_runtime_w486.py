#!/usr/bin/env python3
"""oracle_release_runtime_w486 - GRADED code answers, the request read without its expected outputs, and a PERSISTENT
library of verified programs.

CORRECTNESS RELEASE. The gate's code family is single prose examples, unaffected; what this removes is WRONG PROGRAMS
ASSERTED in conversation, measured by code_chat_ab_v1.py / code_evidence_v1.py on MBPP tasks posed exactly as a person
writes them (description + two examples inline, the third HIDDEN), MBPP TEST split run once, everything frozen
(code_organ_v3 8b4591a9, organ_code_chat_v2 a5f93d76, rule from TRAIN only):
  served w482:  183 programs released, all asserted; 117 pass the hidden example, 66 FAIL it
  this fold:    174 released; 121 pass, 53 fail.  GRADED: 81 asserted CONFIDENTLY (65 right, 16 wrong); 93 shown as
                TENTATIVE with a request for one more example (56 right, 37 wrong)
  confidently asserted wrong programs 66 -> 16; no program is withheld.
Found live when w482 was admitted: "second_biggest([5,2,8,3]) == 5, second_biggest([1,9,4]) == 4" -> max(4, a0[0]):
the EXPECTED OUTPUT became a constant. The request is now read without its expected outputs (inputs are kept: they are
part of the specification). CONFIDENT = the program's moves cover at least half of the request's words (chosen on
TRAIN: 47 right / 11 wrong confident vs 43 / 25 tentative; validation 11 / 1 vs 6 / 6).
PERSISTENT LIBRARY: only confident programs become stored forms, written to self_loop/code_library_v1.json and loaded
at start, so what the organ verified survives restarts and later requests compose or recall it (continuous learning
without retraining). Measurement sessions (loop-) never write it.
Imports new organ versions (organ_code_chat_v2, code_organ_v3); w482's are immutable.
Parent: the serving tip, named. Methods _c486_.
"""

from __future__ import annotations

from pathlib import Path

from oracle_release_runtime_w360 import OracleReleaseRuntimeW360 as _Base

try:
    import organ_code_chat_v2 as _cc2
except Exception:  # noqa: BLE001
    _cc2 = None

LIBRARY = Path(__file__).resolve().parent.parent / 'code_library_v1.json'


class _Recorder:
    """wraps the chat organ so the dispatcher can grade the reply it produced"""

    def __init__(self, chat, owner):
        self.chat, self.owner = chat, owner

    def __getattr__(self, name):
        return getattr(self.chat, name)

    def answer(self, text):
        a = self.chat.answer(text)
        self.owner._c486_last = a
        return a


class OracleReleaseRuntimeW486(_Base):

    def _c482_org(self):
        o = getattr(self, '_c486_o', None)
        if o is None and _cc2 is not None:
            try:
                o = self._c486_o = _Recorder(_cc2.CodeChat(library_path=str(LIBRARY)), self)
            except Exception:  # noqa: BLE001
                o = self._c486_o = False
        return o or super()._c482_org()

    def _c480_dispatch(self, text, session_id, res):
        org = self._c482_org()
        if isinstance(org, _Recorder):
            org.chat.persist = not str(session_id).startswith('loop-')   # measurement never writes the library
        self._c486_last = None
        out = super()._c480_dispatch(text, session_id, res)
        a = getattr(self, '_c486_last', None)
        if not (isinstance(out, dict) and str(out.get('path', '')).startswith('organ:code') and a):
            return out
        body = str(out.get('response', ''))
        body = body.replace('I ran it on your 1 examples before answering and all pass',
                            'I ran it on your example before answering and it passes')
        out = dict(out)
        prov = dict(out.get('provenance') or {})
        prov['confident'] = bool(a.get('confident'))
        if a.get('recalled'):
            body = body.replace('Here is the program.', 'Here is the program; I verified it earlier and recalled it.', 1)
        if not a.get('confident'):
            body = body.replace('Here is the program.',
                                'Here is a program that passes your examples, but they do not pin it down: its steps '
                                'account for less than half of what you described, so treat it as TENTATIVE. One more '
                                'example would let me check it.', 1)
            out['path'] = 'organ:code>tentative'
        out['response'] = body
        out['provenance'] = prov
        return out
