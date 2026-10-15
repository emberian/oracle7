#!/usr/bin/env python3
"""oracle_release_runtime_w503 - CORRECTNESS RELEASE: a request must not be answered about its CONTEXT instead of its
SUBJECT.

Found by the Python specialist's held-out verdict (2026-09-29): "Explain what isinstance does in Python." fell through to
the core, and organ:converse>request answered "Here's what my sources say about python: Python is the name given to a
genus of constricting snakes..." - it explained the trailing context word ("in Python") and not the thing asked about
("isinstance"), and the sense it chose was the wrong one. Reach is not an answer.
This release withdraws a converse request reply whose topic is only the trailing context of the turn ("... in T", "for T",
"using T", "with T", "on T") while the turn names another subject that the reply never mentions, and declines honestly
instead. It adds no capability (the Python specialist answers these from the interpreter's own docs), removes wrong
answers only, and touches no other route. Parent: w502 (itself a correctness release on the w363 tip). Methods _c503_.
"""

from __future__ import annotations

import re

from oracle_release_runtime_w502 import OracleReleaseRuntimeW502 as _Base

TOPIC = re.compile(r"^Here's what my sources say about (.+?):", re.I)
CONTEXT = re.compile(r"\b(?:in|for|using|with|on|inside)\s+(?:the\s+)?([A-Za-z][\w+#-]*(?:\.[\w+#-]+)*)\s*[?.!]*\s*$", re.I)
STOP = set("explain what does do did how work works working mean means meaning tell describe about define definition is are "
           "the a an of to it this that please me you can could would should and or why when where which who whom whose "
           "function functions method methods thing things".split())


class OracleReleaseRuntimeW503(_Base):

    def _c480_dispatch(self, text, session_id, res):
        out = super()._c480_dispatch(text, session_id, res)
        path = str(out.get('path', ''))
        if not path.startswith('organ:converse>request'):
            return out
        body = str(out.get('response', ''))
        tm = TOPIC.search(body)
        cm = CONTEXT.search(str(text))
        if not tm or not cm or tm.group(1).strip().lower() != cm.group(1).lower():
            return out
        head = str(text)[:cm.start()]
        subjects = [w for w in re.findall(r"[A-Za-z_][\w.]*", head) if w.lower() not in STOP and len(w) > 2]
        if not subjects or any(re.search(r"\b%s\b" % re.escape(w), body, re.I) for w in subjects):
            return out
        x, ctx = subjects[0], cm.group(1)
        new = dict(out)
        new.update({'status': 'clarification', 'path': 'organ:converse>request_declined:context_only',
                    'response': "I don't have an explanation of %s in %s in my sources, and I won't answer about %s itself "
                                "instead - that would be a different question." % (x, ctx, ctx),
                    'references': [], 'provenance': {'kind': 'correctness_w503', 'withdrew': path, 'topic': tm.group(1)}})
        return new
