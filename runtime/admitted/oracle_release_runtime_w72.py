#!/usr/bin/env python3
"""oracle_release_runtime_w72 - CORRECTNESS RELEASE: composed programs are programs too.

The reference-resolution fold reads the witness for things a follow-up could be
pointing at, and it recognised exactly one kind of program: the catalogue kind,
recorded as VERIFIED_PROGRAM by the code fold. The synthesis fold records
COMPOSED_PROGRAM instead, because it builds pipelines rather than retrieving
entries, and nothing told the resolver those are the same sort of object.

So the machine would write you a composed program, verify it by differential
execution, and then answer "Did you run it?" with "I didn't fully parse that".
It had run it. It had the output. It could not see that the thing it had made was
a thing you could point at.

Found by the conversation panel rather than by use, which is the reason to build
panels: four scripts came back unresolved, I assumed the fold was being properly
cautious, and it was blind instead.

Two constructions now count as programs, and the warrant kinds that go with them
are both accepted when the machine is asked whether it ran the thing:

    VERIFIED_PROGRAM   from the code fold, warranted by test execution
    COMPOSED_PROGRAM   from the synthesis fold, warranted by differential execution

Hand-authored 2026-08-28. Judged by the gate.
"""

from __future__ import annotations

from oracle_release_runtime_w71 import OracleReleaseRuntimeW71

_PROGRAM_CONSTRUCTIONS = ('VERIFIED_PROGRAM', 'COMPOSED_PROGRAM')
_RESULT_CONSTRUCTIONS = ('VERIFIED_COMPUTATION',)


class OracleReleaseRuntimeW72(OracleReleaseRuntimeW71):
    """Reference resolution that can see everything the machine actually builds."""

    def _referents(self, session_id):
        hist = getattr(self, '_paths', None) or {}
        q = hist.get(session_id)
        out = []
        if not q:
            return out
        for e in reversed(list(q)):
            op = str(e.get('operator', ''))
            if op.startswith(('justify:', 'resolve:')):
                continue
            surface = str(e.get('in_surface', ''))
            conv = e.get('conversion') or {}
            # the conversion slot leaks between turns, so only trust it when its own
            # `from` is the surface of the turn it was found on
            own = str(conv.get('from', ''))[:60].strip() == surface[:60].strip()
            construction = str(conv.get('construction', ''))
            if own and construction in _PROGRAM_CONSTRUCTIONS:
                out.append(('program', str(conv.get('to', '')), surface))
            elif own and construction in _RESULT_CONSTRUCTIONS:
                out.append(('result', str(conv.get('to', '')), surface))
            terms = [t for t in (e.get('in_terms') or [])
                     if t not in self._stop_terms() and len(t) > 2]
            if terms:
                out.append(('topic', terms[0], surface))
            if len(out) >= 6:
                break
        return out

    @staticmethod
    def _stop_terms():
        return {'summarize', 'explain', 'compare', 'list', 'tell', 'facts', 'about',
                'what', 'how', 'why', 'the', 'a', 'an'}
