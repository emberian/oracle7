#!/usr/bin/env python3
"""oracle_release_runtime_w46 - CORRECTNESS RELEASE: rejoin the two live branches.

The same failure that hid the loop from the public happened again, one level in:
two authors worked the chain at once and it forked at w34.

    hand-authored branch   w34 -> w36 -> w37   (program catalogue, synthesis)
    worker branch          w34 -> w41 -> w42 -> w44 -> w45   (epoch folds)

Neither was wrong. What was wrong is that the manifest resolves the tip by the
HIGHEST NUMBER, so w45 became the head and w36/w37 were silently listed as
orphans - a numbering convention deciding which mind serves. Capability that had
passed the gate stopped reaching anyone, exactly as before.

This fold rejoins them by cooperative multiple inheritance; both branches descend
from w34, so the linearisation is clean and neither history is amputated. The
manifest's tip rule is being repaired alongside this, to select the leaf of the
inheritance graph rather than the largest integer.

Hand-authored 2026-08-27. Judged by the gate.
"""

from __future__ import annotations

from oracle_release_runtime_w37 import OracleReleaseRuntimeW37
from oracle_release_runtime_w45 import OracleReleaseRuntimeW45


class OracleReleaseRuntimeW46(OracleReleaseRuntimeW37, OracleReleaseRuntimeW45):
    """One head: hand-authored capability over the worker's own admitted folds."""

    MERGED_BRANCHES = ('oracle_release_runtime_w37', 'oracle_release_runtime_w45')
