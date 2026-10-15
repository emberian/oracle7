#!/usr/bin/env python3
"""oracle_release_runtime_w522 - CAPABILITY RELEASE: the maths agent, version 2.

w521 (admitted) calls wander-train/math_solver_v1.py on competition-format problems the core declines; v1 is frozen (the
governance law: a module an admitted fold imports never changes). This fold points that call at math_solver_v2.py:
  new families   general function values incl. composition (g(f(-2))), coordinate geometry (distance, midpoint, centre from
                 a diameter, slope, y-intercept point, square from adjacent vertices), circle centre / radius from its
                 equation, quadratic extremum, coefficient of a term in an expansion, rationalising, an expression that
                 simplifies to a constant
  fixes          trig powers (\\sin^3 18 deg) and subscripted numbers (43210_6 - 3210_7) declined; the asked expression must
                 follow the question words directly (v1 answered "what is the units digit of ab" with ab); "possible values"
                 read as a solve question
Development only (MATH train sample, 700 problems never used by a measurement; the 400 spent MATH-500 problems): train
31 right / 0 wrong (+1 scored wrong for term order: 1 + sqrt 2 vs sqrt 2 + 1); MATH-500 dev 20 right + 2 TeX-format.
Gate panel v25 competition_math (counts only): v1 7 answered / 6 right -> v2 9 / 8.
Parent: whatever head this is reparented onto; nothing else changes."""
import oracle_release_runtime_w521 as _W521

from oracle_release_runtime_w521 import OracleReleaseRuntimeW521 as _Base

try:
    import math_solver_v2 as _MS2
    _W521._MS = _MS2                                       # w521's agent call now reaches the v2 solver
except Exception:  # noqa: BLE001 - without v2 the fold is exactly its parent
    _MS2 = None


class OracleReleaseRuntimeW522(_Base):
    pass
