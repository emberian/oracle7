#!/usr/bin/env python3
"""oracle_release_runtime_w523 - CAPABILITY RELEASE: the maths agent, version 3 - REASONING over several statements.

w521 (admitted) calls the maths agent on competition-format problems the core declines; w522 pointed that call at v2.
This fold points it at wander-train/math_solver_v3.py, which adds the SYSTEM family: every equation and every function
definition in the problem (definitions may carry a parameter, "g(x) = x^2 - k"), function calls expanded, the whole system
solved for all unknowns at once, the asked quantity evaluated on every solution (one value, or the sum / product / largest /
smallest the question asks for); every solution substituted back into every stated equation. Also: undefined functions
(h(4x-1), P(0)) declined, mixed numbers (8\\frac13 = 8 + 1/3), factorial operands, translated / reflected / rotated
coordinates declined.
Development only (MATH train pool, 3,500 problems never used by a measurement): v2 192 right -> v3 200 right, wrong 1
(plus 2 thousands-separator formatting). Gate panel v26 competition_math (+280 MATH test rows 300-499, labels only):
v2 23 right / 1 wrong -> v3 25 / 0.
The fold never imports a runtime other than its parent: w521's module is reached through sys.modules (the parent chain
loads it)."""
import sys

from oracle_release_runtime_w384 import OracleReleaseRuntimeW384 as _Base

try:
    import math_solver_v3 as _MS3
    _W521 = sys.modules.get("oracle_release_runtime_w521")
    if _W521 is not None:
        _W521._MS = _MS3                                  # w521's agent call now reaches the v3 solver
except Exception:  # noqa: BLE001 - without v3 the fold is exactly its parent
    _MS3 = None


class OracleReleaseRuntimeW523(_Base):
    pass
