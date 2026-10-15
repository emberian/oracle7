#!/usr/bin/env python3
"""oracle_release_runtime_w458 - a computation is answered by the calculator, or refused. Not by the encyclopaedia.

On the generated maths panel, 21 of 128 questions are computations that fall out of the maths fragment and are
then answered by a route with no arithmetic in it: "What is 50% of 178?" comes back as the Roman numeral for
fifty, and "What is the area of a rectangle 26 by 27?" as the definition of area. True sentences, offered as
answers, each costing the honest score twice - the answer not given, and the assertion made.

This is the same defect as the coding route reporting "verified" for a program it never checked against the
request: a fall out of a route that would have been honest, into a route that has no idea what was asked.

The rule is narrow on purpose, because a question with numbers in it is usually not a computation. It fires only
when the question NAMES an operation and CARRIES the arithmetic to perform, and only when the route that answered
is not a maths route:

    "How many moons does Jupiter have?"          no operation named        - untouched
    "What is the population of France in 2020?"  no operation named        - untouched
    "In which battle did Harold II die?"         no operation, no numerals - untouched
    "What is 50% of 178?"                        percent, two numerals     - refused with a receipt
    "What is the square root of 144?"            a unary operation, one    - refused with a receipt

It teaches no mathematics and wins no new answers. It converts assertions into receipts, and every receipt names
the operation it could not perform, which is exactly the list the operators that follow are drawn from.

Methods _r458_. Parent: the serving head.
"""

from __future__ import annotations

import re

from oracle_release_runtime_w295 import OracleReleaseRuntimeW295 as _Base

# an operation, not a subject
OPERATION = re.compile(
    r"\b(?:percent|per cent|area|perimeter|circumference|volume|hypotenuse|"
    r"square root|cube root|logarithm|log base|to the power|squared|cubed|"
    r"times|multiplied by|plus|minus|divided by|remainder|"
    r"solve for|factorise|factorize|factorial|prime factor)\b|%", re.I)
# operations taking ONE operand: requiring two numerals refused "the square root of 144", which is a computation
# with a single argument and nothing ambiguous about it
UNARY = re.compile(
    r"\b(?:square root|cube root|logarithm|log base|squared|cubed|factorial|"
    r"prime|factorise|factorize|prime factor)\b", re.I)
IS_PRIME = re.compile(r"\bis\s+\d+\s+(?:a\s+)?prime\b", re.I)
NUMERAL = re.compile(r"(?<![A-Za-z])\d+(?:\.\d+)?")
SYMBOLIC = re.compile(r"\d\s*[-+*/^]\s*\d|\d\s*x\b|\bx\s*[-+*/^=]")
MATH_ROUTE = re.compile(r"compute:|algebra:|op:|arithmetic|calculat", re.I)
RECEIPT = re.compile(r"(?:^|\|)(?:vessel:receipt|[a-z_]*:receipt)(?:\||$)")


class OracleReleaseRuntimeW458(_Base):
    """Arithmetic is not something the encyclopaedia gets to answer."""

    @staticmethod
    def _r458_is_computation(text):
        """does this ask for something to be COMPUTED, rather than merely mention numbers?"""
        t = str(text or '')
        named = OPERATION.search(t) or IS_PRIME.search(t)
        if not named:
            return False
        n = len(NUMERAL.findall(t))
        if n >= 2 or '%' in t or SYMBOLIC.search(t) is not None:
            return True
        return n >= 1 and (UNARY.search(t) is not None or IS_PRIME.search(t) is not None)

    @staticmethod
    def _r458_named(text):
        t = str(text or '')
        m = OPERATION.search(t)
        if m and m.group(0).strip() != '%':
            return m.group(0).strip().lower()
        if IS_PRIME.search(t):
            return 'primality'
        return 'percentage' if '%' in t else 'that calculation'

    def chat(self, text: str, session_id: str = 'default') -> dict:
        res = super().chat(text, session_id)
        try:
            if not isinstance(res, dict) or str(res.get('status')) != 'answered':
                return res
            path = str(res.get('path') or '')
            if MATH_ROUTE.search(path) or RECEIPT.search(path):
                return res                      # the calculator answered, or it has already refused
            if not self._r458_is_computation(text):
                return res                      # numbers in a question are not a computation
            op = self._r458_named(text)
            out = dict(res)
            out['status'] = 'withheld'
            out['path'] = '%s|math:out_of_fragment|vessel:receipt' % path
            out['response'] = (
                'That asks me to work out %s, and I compute exactly or not at all. It is outside the arithmetic I '
                'can carry out, so rather than answer it from a page about the words in your question, I am '
                'telling you I cannot do it yet.'
                % (op if op in ('percentage', 'primality', 'that calculation') else 'the ' + op))
            out['provenance'] = dict(res.get('provenance') or {}, kind='math_out_of_fragment',
                                     operation=op, displaced_path=path)
            return out
        except Exception:  # noqa: BLE001
            return res
