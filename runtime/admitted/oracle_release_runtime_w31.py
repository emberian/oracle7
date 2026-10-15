#!/usr/bin/env python3
"""oracle_release_runtime_w31 - CORRECTNESS RELEASE: the merge, one true head.

The defect this closes is the largest one in the project's record. Two branches
descended from the same ancestor (oracle_release_runtime_ao):

    loop branch     ao -> w1 -> w4 -> w6 -> ... -> w24 -> w29   (self-improved)
    serving branch  ao -> bed2 -> evidential_v2 -> evidential_v3 (public site)

The self-improvement loop has been admitting folds into a chain THE PUBLIC HEAD
NEVER SERVED. Episodic world memory, reflection, typed potentials, grounded
continuation, the live made-of rule, the two-hop composer and verified compute
were all admitted, and none of them ever reached a visitor. The manifest reported
the loop's tip while the harness instantiated the evidential branch, so the head
identity was true on paper and false in practice.

This fold merges the branches. Both derive from ao, so cooperative multiple
inheritance linearizes cleanly: every w-fold's super() call now continues into
the evidential layer instead of stopping at ao, which means a turn is read by the
self-improved routes FIRST and falls through to the evidential serving behaviour
that the public site has depended on. Nothing is deleted; the two histories are
composed in one head.

This is a CORRECTNESS RELEASE, not a capability: w30 carried identical code and
was refused for no_gain, correctly, because a structural repair cannot move
conversation metrics - it measured exactly the head (232 answered, 152 continuity,
255 read, 0.2107 grounding), zero regression. The defect it repairs is not in any
answer; it is in WHICH HEAD ANSWERS. A head identity that is true on paper and
false in practice is precisely the class of defect this exemption exists for.

Hand-authored 2026-08-26 under Ben's directive. Judged by the gate.
"""

from __future__ import annotations

from oracle_release_runtime_w29 import OracleReleaseRuntimeW29
from oracle_sibling_evidential_v3 import SiblingEvidentialV3


class OracleReleaseRuntimeW31(OracleReleaseRuntimeW29, SiblingEvidentialV3):
    """The single head: self-improved routes over the evidential serving layer.

    Method resolution walks the loop branch first (compute, composer, rule folds,
    reflection, episodic memory, potentials), then the evidential branch, then
    the shared ancestor. Both branches keep their behaviour; neither is amputated.
    """

    MERGED_BRANCHES = ('oracle_release_runtime_w29', 'oracle_sibling_evidential_v3')
