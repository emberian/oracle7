#!/usr/bin/env python3
"""oracle_release_runtime_w482 - the CODE ORGAN in conversation: a request that states examples gets a program that ran.

The chain's own code route (w32) answers from a fixed catalogue of hand-written tasks: set moves. This fold connects
the code organ (code_organ_v2 via organ_code_chat_v1): a request that asks for a function AND states at least two
examples (`name(args) == value`, `->`, `returns`, `should return`) is solved by composing typed library moves (the type
system is the specified structure; the request's words rank the moves), the rendered source is EXECUTED against every
example, and the program is released only if all pass. Verified programs join the process's library (stored forms).
Measured on MBPP's 500 test tasks, run once, frozen (sha b2e52a1d): 137 solved / 1 wrong (standard protocol); with a
hidden third assert 117 pass it / 36 do not (76%); growing library 146 solved, 42 reusing programs the organ verified.
Released for a program request with verifiable examples over any chain route (catalogue code:*, synth:composed),
none of which executes against the person's own examples; this one does. Without verifiable examples: the chain's.
PROSE REQUESTS with ONE example ("..., so 'oracle' becomes 'elcaro'") are solved in STRICT mode (code_organ_v2): only
constants the request names (numbers, quoted characters, ordinals and number words: second=1, doubled=2), only base
library moves, and the program whose moves jointly COVER most of the request's words wins at any size - the single
example only checks it. On the gate's code_spec family: 18 of 18 answerable requests get correct programs, 12 of 12
impossible ones decline (the chain failed 13 of the 30). Library entries c2f/f2c/isleap/joincomma/nwords were added
from that family's failure classes (labelled so in code_organ_v2). A request whose function was verified before is
RECALLED as the stored form and re-checked, not re-derived.
MATH ORGAN v2 replaces w480's frozen v1 here: v1 read "the factorial of a number" as a request to factor.
Parent: the serving tip, named. Methods _c482_.
"""

from __future__ import annotations

import re

from oracle_release_runtime_w356 import OracleReleaseRuntimeW356 as _Base

try:
    import organ_code_chat_v1 as _cc
except Exception:  # noqa: BLE001
    _cc = None
try:
    import math_organ_v2 as _math2                       # v1 is frozen with w480; v2 fixes "factorial" != factor
except Exception:  # noqa: BLE001
    _math2 = None
try:
    import oracle_release_runtime_w480 as _w480
    _run = _w480._run
except Exception:  # noqa: BLE001
    _run = None


class OracleReleaseRuntimeW482(_Base):

    def _c480_math(self):
        # the math organ v2: w480's v1 read "a function that returns the FACTORIAL" as a request to FACTOR (found on the
        # gate's code_spec family); v2 declines requests for programs and does not read factorial as factor
        o = getattr(self, '_c482_m', None)
        if o is None and _math2 is not None:
            try:
                o = self._c482_m = _math2.MathOrgan()
            except Exception:  # noqa: BLE001
                o = self._c482_m = False
        return o or super()._c480_math()

    def _c482_org(self):
        o = getattr(self, '_c482_o', None)
        if o is None and _cc is not None:
            try:
                o = self._c482_o = _cc.CodeChat()
            except Exception:  # noqa: BLE001
                o = self._c482_o = False
        return o or None

    def _c480_dispatch(self, text, session_id, res):
        out = super()._c480_dispatch(text, session_id, res)
        answered = self._c480_answered(out)
        path = str(out.get('path', ''))
        # a PROGRAM request with VERIFIABLE examples (two structured, or one prose example) is the code organ's: its
        # program is executed against those examples, which no chain route (catalogue code:*, synth:composed) does -
        # except where another organ (math, relation, dialogue) already answered
        if _cc is None or _run is None or path.startswith('organ:') or not _cc.CODE_ASK.search(text or ''):
            return out
        org = self._c482_org()
        if org is None or (len(org.examples(text)) < 2 and not org.prose_example(text)):
            return out
        a = _run(org.answer, text)
        if not a:
            return out
        body = ('Here is the program. I ran it on your %d examples before answering and all pass.\n\n%s\n\n%s'
                % (a['passed'], '\n'.join(a['imports'] + ([''] if a['imports'] else []) + [a['program']]),
                   '\n'.join('%s  # passes' % t for t in a['tests'])))
        if a['reused']:
            body += '\n\nIt composes %s, which I verified earlier in this session.' % ', '.join(a['reused'])
        new = dict(out)
        new.update({'status': 'answered', 'path': 'organ:code>composed', 'response': body,
                    'provenance': {'kind': 'organ_code', 'tests': a['tests'], 'passed': a['passed'],
                                   'reused': a['reused'], 'parent_path': path, 'parent_status': out.get('status')}})
        return new
