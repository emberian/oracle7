#!/usr/bin/env python3
"""oracle_release_runtime_w66 - CORRECTNESS RELEASE: merging back a fold I orphaned.

w60 was admitted and never served. I authored w61 extending w59 while w60 was still
in front of the gate, the chain forked, and every fold after that inherited the
branch without it. So the refusal-aware justification w60 exists to provide has been
sitting in the admitted directory all afternoon, reaching nobody.

It was found by a metric rather than by looking, which is the only reason it was
found at all. The accountability measurement showed the machine saying "my record
holds no warrant of any kind" about turns where it had DECLINED, which is exactly
the false account w60 was written to prevent. Chasing that back through the manifest
showed w60 sitting in `orphaned_admitted`, a field the manifest has been publishing
correctly and nothing has ever read.

This is the third branch split today and the second one I caused. The first two were
about a worker authoring concurrently. This one had no such excuse: I wrote the
parent line myself, in the wrong order, while the fold I was skipping sat in the
queue.

The merge is cooperative multiple inheritance, the pattern already used for w31 and
w46. Both parents converge on w59, so the linearisation is unambiguous and w60's
_justify override lands ahead of the base implementation it was written to correct.

A structural guard goes in with this, in the gate rather than here: a candidate
whose parents do not include the current tip is FORKING THE CHAIN and is refused.
Merges name the tip among several parents and still pass. That rule would have
stopped w61 on the day I wrote it, and it removes my ability to make this mistake a
fourth time.

Hand-authored 2026-08-28. Judged by the gate.
"""

from __future__ import annotations

from oracle_release_runtime_w65 import OracleReleaseRuntimeW65
from oracle_release_runtime_w60 import OracleReleaseRuntimeW60


class OracleReleaseRuntimeW66(OracleReleaseRuntimeW65, OracleReleaseRuntimeW60):
    """The capability line and the orphaned correctness fold, rejoined."""
