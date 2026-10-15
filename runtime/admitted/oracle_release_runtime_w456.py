#!/usr/bin/env python3
"""oracle_release_runtime_w456 - an empty composition is not an answer.

Measured on the coding panel: the head asserts on 4 of 12 self-contradictory specifications, and every one comes
from the composition route. Asked for a number that is both even and odd, it builds "keep even then keep odd" and
returns an empty list for every case it tries; asked for the square root of a negative number as a positive
integer, it builds "square, keep negative, keep positive" and does the same. Each then reports that it verified
the result by differential execution, which is true and worthless: the program and the independent computation
agree that there is nothing.

The route already runs the composed program over its own sample cases. This looks at what came back. When every
case yields emptiness - an empty list, an empty string, a null - the pipeline cannot produce anything, and saying
so is the answer.

Zero and False are answers and are never degenerate. Emptiness on a single case is ordinary. Only emptiness on
EVERY case is the signal, because that is what an unsatisfiable pipeline looks like from outside.

Methods _r456_. Parent: the serving head.
"""

from __future__ import annotations

import re

from oracle_release_runtime_w458 import OracleReleaseRuntimeW458 as _Base

COMPOSED = re.compile(r"(?:^|\|)synth:composed(?:\||$)", re.I)
CODE_START = re.compile(r"^\s*(?:def |class |import |from |@)")
PROSE_RESUMES = re.compile(r"^\s*(?:Verified|I chose|I composed|I ran|Read as a pipeline|Nothing in that)", re.I)
# what "it produced nothing" looks like once printed
EMPTY = {'[]', '{}', 'null', 'none', '""', "''", '[""]', '[]\n'}


class OracleReleaseRuntimeW456(_Base):
    """A pipeline that returns nothing for every case it tried has not answered."""

    def _r456_program(self, body):
        lines = str(body or '').split('\n')
        start = next((i for i, l in enumerate(lines) if CODE_START.match(l)), None)
        if start is None:
            return ''
        end = len(lines)
        for i in range(start, len(lines)):
            if PROSE_RESUMES.match(lines[i]):
                end = i
                break
        out = lines[start:end]
        while out and not out[-1].strip():
            out.pop()
        return '\n'.join(out)

    def _r456_all_empty(self, program):
        """did every sample case the program runs produce nothing?

        Run through the executor the code route already uses. A program that prints no lines at all is not judged
        here - there is nothing to read - and neither is one whose output cannot be captured.

        The executor compares stdout against an expected string, so the program runs inside a captured buffer and
        only a verdict word is printed for the comparison to match."""
        probe = ('import contextlib, io\n'
                 '_src = ' + repr(program) + '\n'
                 '_buf = io.StringIO()\n'
                 'try:\n'
                 '    with contextlib.redirect_stdout(_buf):\n'
                 '        exec(compile(_src, "prog", "exec"), {})\n'
                 'except Exception:\n'
                 '    print("UNREADABLE")\n'
                 'else:\n'
                 '    _lines = [l.strip() for l in _buf.getvalue().split(chr(10)) if l.strip()]\n'
                 '    _empty = {"[]", "{}", "null", "None", chr(34)*2, chr(39)*2}\n'
                 '    if not _lines:\n'
                 '        print("UNREADABLE")\n'
                 '    elif all(l in _empty for l in _lines):\n'
                 '        print("ALL_EMPTY")\n'
                 '    else:\n'
                 '        print("PRODUCED")\n')
        try:
            ok, _note = self._verify('python', probe, 'ALL_EMPTY\n')
            return bool(ok)
        except Exception:  # noqa: BLE001
            return False

    def chat(self, text: str, session_id: str = 'default') -> dict:
        res = super().chat(text, session_id)
        try:
            if not isinstance(res, dict) or str(res.get('status')) != 'answered':
                return res
            if not COMPOSED.search(str(res.get('path') or '')):
                return res
            program = self._r456_program(str(res.get('response', '')))
            if not program or not self._r456_all_empty(program):
                return res
            out = dict(res)
            out['status'] = 'withheld'
            out['path'] = '%s|compose:empty' % res.get('path')
            out['response'] = (
                'I composed a pipeline for that and it returns nothing for every case I tried, so there is no '
                'answer in it. That usually means what you asked for cannot hold at once. I would rather tell '
                'you that than hand you a program that can never return anything and call it verified.')
            out['provenance'] = dict(res.get('provenance') or {}, kind='empty_composition', checked=True)
            return out
        except Exception:  # noqa: BLE001
            return res
