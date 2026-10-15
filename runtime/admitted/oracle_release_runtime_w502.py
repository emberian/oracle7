#!/usr/bin/env python3
"""oracle_release_runtime_w502 - CORRECTNESS RELEASE: the word-problem route must not read a chemical formula's
subscripts as quantities.

Found by the chemistry specialist's held-out verdict (2026-09-29): "What percentage by mass of C6H12O6 is hydrogen?"
fell through to the core, and organ:math>word:percent_of_total answered "50% ... percent = 6 / 12 x 100" - it took the
subscripts 6 and 12 as a part and a whole. The true answer is 6.7%. The same shape answered C12H22O11 "50%" from 11 / 22.
A confident wrong answer from an admitted organ is a correctness defect.
This release withdraws a word-problem answer when the turn contains a chemical formula (two or more element-and-count
pairs, e.g. C6H12O6, H2SO4, Ca(OH)2) and declines honestly instead. It adds no capability (the chemistry specialist
answers these exactly), removes wrong answers only, and touches no other route.
Parent: the serving tip, named. Methods _c502_.
"""

from __future__ import annotations

import re

from oracle_release_runtime_w363 import OracleReleaseRuntimeW363 as _Base

# a token of two or more element-symbol components (brackets allowed) with at least one digit: C6H12O6, H2SO4, CO2,
# Ca(OH)2. Known trade-off: a product code like "PS5" also matches, so such a word problem declines - the safe direction.
FORMULA = re.compile(r"(?<![A-Za-z0-9])(?=[A-Za-z0-9()]*\d)(?:[A-Z][a-z]?\d*|\((?:[A-Z][a-z]?\d*)+\)\d*){2,}(?![A-Za-z0-9])")


class OracleReleaseRuntimeW502(_Base):

    def _c480_dispatch(self, text, session_id, res):
        out = super()._c480_dispatch(text, session_id, res)
        path = str(out.get('path', ''))
        if path.startswith('organ:math>word') and FORMULA.search(str(text)):
            new = dict(out)
            new.update({'status': 'clarification', 'path': 'organ:math>word_declined:formula',
                        'response': "That contains a chemical formula, and I won't read its subscripts as quantities in a "
                                    "word problem. Ask it as chemistry (for example, the percent by mass of an element in "
                                    "a compound) and it can be computed exactly.",
                        'references': [], 'provenance': {'kind': 'correctness_w502', 'withdrew': path}})
            return new
        return out
