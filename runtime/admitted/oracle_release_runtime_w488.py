#!/usr/bin/env python3
"""oracle_release_runtime_w488 - WORD PROBLEMS: single-step prose read into an equation by a stored schema.

The math organ (v1/v2) declines a word problem ("the quantities must be translated into equations first"). This fold
connects word_problems_v1 (sha 4c0c60b1): each SCHEMA is a stored form - trigger words, the TYPED quantities it needs
(money, percent, time, length, mass, volume; read with their units), and a formula - and it fires only when every
quantity is found with the right type, the question asks for what the formula produces, and the problem is single-step
(no chained quantities: left, change, faster, every day, ...). Two schemas reading a problem differently -> abstain.
Schemas: simple interest, unit price, total cost, sale price, percent of a total, percent of, distance/rate, unit
conversion, rectangle/circle/cone/cylinder/sphere measures.
Measured on OpenStax word problems held out BY MODULE, run once, frozen: 5 right / 0 wrong of 244 (development
modules: 40 / 0 of 813); a 'largest number in the problem' mutant scores 7 and 8. Precise and narrow: most textbook
word problems chain two or more steps, which v1 declines.
Released only where the chain did not answer. Parent: the serving tip, named. Methods _c488_.
"""

from __future__ import annotations

from oracle_release_runtime_w486 import OracleReleaseRuntimeW486 as _Base

try:
    import word_problems_v1 as _wp
except Exception:  # noqa: BLE001
    _wp = None
try:
    import oracle_release_runtime_w480 as _w480
    _run = _w480._run
except Exception:  # noqa: BLE001
    _run = None


def _fmt(v, unit):
    if unit == "$":
        return "$%s" % ("{:,.2f}".format(v) if v % 1 else "{:,.0f}".format(v))
    if unit == "%":
        return "%s%%" % ("%g" % round(v, 4))
    return ("%g" % round(v, 6)) + ((" " + unit) if unit and unit not in ("sq", "cu") else
                                   (" square units" if unit == "sq" else (" cubic units" if unit == "cu" else "")))


class OracleReleaseRuntimeW488(_Base):

    def _c480_dispatch(self, text, session_id, res):
        out = super()._c480_dispatch(text, session_id, res)
        if _wp is None or _run is None or self._c480_answered(out):
            return out
        a = _run(_wp.answer, text)
        if not a:
            return out
        body = ("[ev:derived] %s. Read as %s: %s. Checked: every quantity the formula needs was found with its unit, "
                "and the question asks for what the formula gives." % (_fmt(a["value"], a["unit"]),
                                                                        a["schema"].replace("_", " "),
                                                                        "; ".join(a["steps"])))
        new = dict(out)
        new.update({'status': 'answered', 'path': 'organ:math>word:%s' % a['schema'], 'response': body,
                    'provenance': {'kind': 'organ_word_problem', 'schema': a['schema'], 'value': a['value'],
                                   'parent_path': str(out.get('path', '')), 'parent_status': out.get('status')}})
        return new
