#!/usr/bin/env python3
"""oracle_release_runtime_w57 - CORRECTNESS RELEASE: say what you are, not what the file says.

Asked "what is your admitted head", the machine read HEAD_MANIFEST.json and
answered with the tip recorded there. On 2026-08-28 it answered "I am served by
w54" while the process serving that answer had loaded its class at boot, hours
before w54 was admitted. The sentence was sincere and false. It was reading a
record about itself instead of looking at itself.

That is a worse failure than a wrong answer about volcanoes, because the whole
claim of this architecture is that it can say what it is made of and show the
artifact. A self-report that quotes a file the process has not reloaded is
exactly the kind of unearned confidence the rest of the system is built to refuse.

The fix is to introspect. The class actually executing the turn is on this
object's method resolution order, so the head is read from type(self) rather than
from disk, and the depth is counted the same way. The manifest is still consulted,
but now as a SECOND source, and when the two disagree the machine says so plainly
instead of picking whichever one it happened to read:

    I am running w55. The manifest records w56 as the admitted head, so the
    record is ahead of this process and w56 will serve after the next restart.

That sentence is worth more than either number alone, because a visitor who sees
it learns something true about how the system works: admission and serving are
separate acts, and the gap between them is visible rather than hidden.

Hand-authored 2026-08-28. Judged by the gate.
"""

from __future__ import annotations

from oracle_release_runtime_w56 import OracleReleaseRuntimeW56
from oracle_release_runtime_w33 import _Q_HEAD

_PREFIX = 'oracle_release_runtime_'


class OracleReleaseRuntimeW57(OracleReleaseRuntimeW56):
    """Self-report grounded in the loaded class rather than a file on disk."""

    def _loaded_head(self):
        """(name, depth) of the runtime actually executing, from the MRO."""
        chain = [c for c in type(self).__mro__
                 if str(getattr(c, '__module__', '')).startswith(_PREFIX)]
        if not chain:
            return None, 0
        return str(chain[0].__module__).split('runtime_')[-1], len(chain)

    def _self_answer(self, s):
        loaded, depth = self._loaded_head()
        if loaded is None:
            return super()._self_answer(s)
        man = self._read_manifest() or {}
        recorded = str(man.get('tip', '')).split('runtime_')[-1] or None

        if _Q_HEAD.search(s):
            if recorded and recorded != loaded:
                return ('I am running %s, which is the class this process actually '
                        'loaded, with %d runtimes on its resolution order. The '
                        'manifest records %s as the '
                        'admitted head, so the record is ahead of this process and '
                        '%s will serve after the next restart. I am telling you both '
                        'because the file is not evidence of what I am executing. '
                        '[self:loaded] [self:manifest]'
                        % (loaded, depth, recorded, recorded),
                        ['self:loaded', 'self:manifest'])
            return ('I am served by %s, the admitted head, and that is the class '
                    'this process loaded rather than a line I read in a file. Its '
                    'resolution order carries %d runtimes, each admitted by the '
                    'gate before it could serve. [self:loaded] [self:manifest]'
                    % (loaded, depth), ['self:loaded', 'self:manifest'])

        out = super()._self_answer(s)
        if out and recorded and recorded != loaded:
            text, cites = out
            stale = 'The runtime serving you now is %s.' % recorded
            if stale in str(text):
                text = str(text).replace(
                    stale, 'The runtime serving you now is %s; the manifest already '
                           'records %s, which serves after the next restart.'
                           % (loaded, recorded))
                return (text, cites)
        return out
