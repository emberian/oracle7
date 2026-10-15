#!/usr/bin/env python3
"""oracle_release_runtime_w428 - TEX READER: typeset arithmetic evaluated exactly, checked by a second method.

MATH-500 (2026-09-06): the served model could only abstain on all 200 problems, because no
operator read typeset input; the parsed-surface law (w422) made that abstention honest. This
fold gives the exact operators a reader for the bounded grammar of typeset arithmetic:

    numbers, + - * / ^, parentheses (incl. \\left \\right), \\frac{a}{b}, \\sqrt{x} of perfect squares,
    \\cdot \\times \\div, and the alternating / arithmetic series "1-2+3-4+...+99-100"

The surface must be one of the compute forms ("Compute", "Evaluate", "What is the value of",
"What is", "Find the value of", "Simplify") with ONE expression and nothing else that the
reader does not consume; a problem with words the grammar does not cover stays withheld under
w422. Every value is computed over exact Fractions and re-computed by a second method
(integer/decimal evaluation of the same tree); the two must agree or nothing is said.
Methods _t428_. Parent: the serving tip, named.
"""

from __future__ import annotations

import re
import time
from decimal import Decimal, getcontext
from fractions import Fraction

from oracle_release_runtime_w426 import OracleReleaseRuntimeW426 as _Base

getcontext().prec = 50
COMPUTE_FORM = re.compile(r"^(?:compute|evaluate|simplify|find the value of|what is the value of|what is|calculate)\s*:?\s*(.+?)\s*(?:in your head)?\.?\s*$", re.I)
SERIES = re.compile(r"^(-?\d+)((?:[+-]\d+){2,8})[+-]\\?(?:dots|cdots|ldots)([+-])(\d+)([+-])(\d+)$")
TOKEN = re.compile(r"\s*(?:(\d+(?:\.\d+)?)|(\\frac|\\dfrac|\\tfrac|\\sqrt|\\cdot|\\times|\\div|\\left|\\right)|([-+*/^(){}]))")


class _Tok:
    def __init__(self, src):
        self.src = src
        self.pos = 0
        self.toks = []
        s = src
        while s and s.strip():
            m = TOKEN.match(s)
            if not m:
                raise ValueError('unreadable at %r' % s[:12])
            if m.group(1):
                self.toks.append(('num', m.group(1)))
            elif m.group(2):
                t = m.group(2)
                if t in ('\\cdot', '\\times'):
                    self.toks.append(('op', '*'))
                elif t == '\\div':
                    self.toks.append(('op', '/'))
                elif t in ('\\left', '\\right'):
                    pass
                else:
                    self.toks.append(('cmd', t))
            else:
                self.toks.append(('op', m.group(3)))
            s = s[m.end():]

    def peek(self):
        return self.toks[self.pos] if self.pos < len(self.toks) else (None, None)

    def take(self, kind=None, val=None):
        k, v = self.peek()
        if k is None or (kind and k != kind) or (val and v != val):
            raise ValueError('expected %s %s got %s %s' % (kind, val, k, v))
        self.pos += 1
        return v


def _parse(tok):
    """expr := term (('+'|'-') term)* ; term := power (('*'|'/'|implicit) power)* ; power := unary ('^' power)?"""
    def expr():
        v = term()
        while tok.peek() == ('op', '+') or tok.peek() == ('op', '-'):
            op = tok.take('op')
            r = term()
            v = ('+', v, r) if op == '+' else ('-', v, r)
        return v

    def term():
        v = power()
        while True:
            k, s = tok.peek()
            if (k, s) in (('op', '*'), ('op', '/')):
                tok.take('op')
                r = power()
                v = (s, v, r)
            elif k == 'cmd' and s in ('\\frac', '\\dfrac', '\\tfrac') and v[0] == 'num' and '.' not in v[1]:
                r = power()  # a whole number followed by a fraction is a MIXED number: 4\dfrac{5}{8} = 4 + 5/8
                v = ('+', v, r)
            elif k in ('num', 'cmd') or (k, s) == ('op', '('):
                r = power()  # implicit multiplication: 3(4), 2\sqrt{9}
                v = ('*', v, r)
            else:
                return v

    def power():
        b = unary()
        if tok.peek() == ('op', '^'):
            tok.take('op')
            e = power()
            return ('^', b, e)
        return b

    def unary():
        k, s = tok.peek()
        if (k, s) == ('op', '-'):
            tok.take('op')
            return ('neg', unary())
        if (k, s) == ('op', '+'):
            tok.take('op')
            return unary()
        return atom()

    def brace():
        tok.take('op', '{')
        v = expr()
        tok.take('op', '}')
        return v

    def atom():
        k, s = tok.peek()
        if k == 'num':
            tok.take('num')
            return ('num', s)
        if k == 'cmd' and s in ('\\frac', '\\dfrac', '\\tfrac'):
            tok.take('cmd')
            a = brace()
            b = brace()
            return ('/', a, b)
        if k == 'cmd' and s == '\\sqrt':
            tok.take('cmd')
            return ('sqrt', brace())
        if (k, s) == ('op', '('):
            tok.take('op')
            v = expr()
            tok.take('op', ')')
            return v
        if (k, s) == ('op', '{'):
            return brace()
        raise ValueError('unexpected %s %s' % (k, s))

    v = expr()
    if tok.peek() != (None, None):
        raise ValueError('trailing input')
    return v


def _eval_frac(t):
    op = t[0]
    if op == 'num':
        return Fraction(t[1])
    if op == 'neg':
        return -_eval_frac(t[1])
    if op == 'sqrt':
        v = _eval_frac(t[1])
        if v < 0:
            raise ValueError('negative root')
        n, d = v.numerator, v.denominator
        rn, rd = int(round(n ** 0.5)), int(round(d ** 0.5))
        if rn * rn != n or rd * rd != d:
            raise ValueError('not a perfect square')
        return Fraction(rn, rd)
    a, b = _eval_frac(t[1]), _eval_frac(t[2])
    if op == '+':
        return a + b
    if op == '-':
        return a - b
    if op == '*':
        return a * b
    if op == '/':
        if b == 0:
            raise ValueError('division by zero')
        return a / b
    if op == '^':
        if b.denominator != 1 or abs(b) > 64:
            raise ValueError('exponent out of grammar')
        return a ** int(b)
    raise ValueError(op)


def _eval_dec(t):
    """Second method: the same tree over 50-digit decimals."""
    op = t[0]
    if op == 'num':
        return Decimal(t[1])
    if op == 'neg':
        return -_eval_dec(t[1])
    if op == 'sqrt':
        return _eval_dec(t[1]).sqrt()
    a, b = _eval_dec(t[1]), _eval_dec(t[2])
    if op == '+':
        return a + b
    if op == '-':
        return a - b
    if op == '*':
        return a * b
    if op == '/':
        return a / b
    if op == '^':
        return a ** int(b)
    raise ValueError(op)


def _fmt(v):
    if v.denominator == 1:
        return str(v.numerator)
    return '%d/%d' % (v.numerator, v.denominator)


def _series(expr_text):
    """1-2+3-4+5-...+99-100 style: consecutive integers with a repeating sign pattern, closed by a second method."""
    m = SERIES.match(expr_text.replace(' ', ''))
    if not m:
        return None
    a0, run, sN1, n1, sN2, n2 = m.groups()
    a0, n1, n2 = int(a0), int(n1), int(n2)
    lead = [(1 if s == '+' else -1, int(v)) for s, v in re.findall(r"([+-])(\d+)", run)]
    terms = [(1, a0)] + lead
    # consecutive integers, signs alternating from the first term; the tail must continue the same pattern
    if any(terms[i][1] != terms[i - 1][1] + 1 for i in range(1, len(terms))) or n2 != n1 + 1:
        return None
    if any(terms[i][0] == terms[i - 1][0] for i in range(1, len(terms))):
        return None
    total = 0
    for i, k in enumerate(range(a0, n2 + 1)):
        total += k if i % 2 == 0 else -k
    expected_last_sign = 1 if (n2 - a0) % 2 == 0 else -1
    if (1 if sN2 == '+' else -1) != expected_last_sign:
        return None
    # second method: pairing consecutive terms gives -1 per pair, plus the unpaired last term
    count = n2 - a0 + 1
    total2 = -(count // 2) + (n2 if count % 2 else 0)
    if total != total2:
        return None
    return total, 'alternating series %d to %d (%d terms)' % (a0, n2, count)


class OracleReleaseRuntimeW428(_Base):
    """Typeset arithmetic read whole, computed exactly, checked twice."""

    @staticmethod
    def _t428_extract(q):
        s = ' '.join(str(q).split())
        m = COMPUTE_FORM.match(s)
        if not m:
            return None
        body = m.group(1).strip()
        body = body.replace('$', '').replace('\\[', '').replace('\\]', '').replace('\\(', '').replace('\\)', '').strip(' .?')
        if not body or re.search(r"[A-Za-z]", re.sub(r"\\(?:frac|dfrac|tfrac|sqrt|cdot|times|div|left|right|dots|cdots|ldots)", '', body)):
            return None
        return body

    def _t428_try(self, q, res, t0):
        body = self._t428_extract(q)
        if body is None:
            return None
        ser = _series(body)
        if ser:
            val, how = ser
            text = 'The value is %d. Read as an %s; summed term by term and checked by pairing, which agrees.' % (val, how)
            return self._t428_answer(res, text, {'rule': 'series', 'value': str(val), 'expr': body[:120]}, t0)
        try:
            tree = _parse(_Tok(body))
            v = _eval_frac(tree)
            d = _eval_dec(tree)
        except Exception as e:  # noqa: BLE001
            return None
        if abs(Decimal(v.numerator) / Decimal(v.denominator) - d) > Decimal('1e-30'):
            return None
        text = 'The value is %s. Computed exactly over fractions and checked by a second method (50-digit decimal), which agrees.' % _fmt(v)
        if v.denominator != 1:
            text += ' As a decimal: %s.' % (str(Decimal(v.numerator) / Decimal(v.denominator))[:24])
        return self._t428_answer(res, text, {'rule': 'tex_eval', 'value': _fmt(v), 'expr': body[:120]}, t0)

    @staticmethod
    def _t428_answer(res, text, prov, t0):
        out = dict(res)
        out.update({'status': 'answered', 'path': 'compute:tex_verified', 'response': text, 'references': [],
                    'provenance': dict(res.get('provenance') or {}, kind='compute', verified_warrant={'kind': 'tex_eval', 'steps': [prov]}, tex=prov,
                                       ms=int((time.time() - t0) * 1000), parent_path=str(res.get('path', '')))})
        return out

    @staticmethod
    def _t428_math_words(s):
        """A competition word problem in plain text: numbers plus the vocabulary of one (integer, probability, sum,
        product, reciprocal, digits, divisible, cube, square, remainder, fraction). Dump routes are never its answer."""
        low = s.lower()
        words = sum(1 for w in ('integer', 'integers', 'probability', 'sum of', 'product of', 'reciprocal', 'digits', 'divisible', 'perfect cube', 'perfect square',
                                'remainder', 'fraction', 'smallest', 'largest', 'consecutive', 'expressed as', 'common fraction', 'how many ways', 'positive', 'even number', 'odd number')
                    if w in low)
        return words >= 2 or (words >= 1 and len(re.findall(r"\b\d+\b", s)) >= 1)

    def chat(self, text: str, session_id: str = 'default') -> dict:
        res = super().chat(text, session_id)
        try:
            s = ' '.join(str(text).strip().split())
            if str(session_id).startswith('loop-delib-'):
                return res
            path = str(res.get('path', ''))
            if res.get('status') == 'answered' and path.startswith(('arb:', 'document_runtime', 'definitional', 'capability:')) and self._t428_math_words(s) and not _is_plain_question(s):
                # a word problem answered by a summary, a definition or a list is a misroute; the receipt is honest
                out = dict(res)
                out.update({'status': 'withheld', 'path': 'operator:unparsed|vessel:receipt',
                            'response': 'That is a mathematics word problem. My exact operators read typeset and plain arithmetic, and none of them read this one whole, so I will not guess at it.',
                            'references': [], 'provenance': dict(res.get('provenance') or {}, kind='operator_unparsed', word_problem=True, parent_path=path)})
                try:
                    self._receive(s[:400], session_id, res)
                except Exception:
                    pass
                return out
            if res.get('status') == 'answered' and not path.startswith(('operator:unparsed', 'factoid:withheld')):
                return res
            if '\\' not in s and '$' not in s and '^' not in s:
                return res
            out = self._t428_try(s, res, time.time())
            if out:
                return out
        except Exception:
            return res
        return res


def _is_plain_question(s):
    """A short everyday question with a number in it is not a word problem ("How many legs does a spider have?")."""
    return len(s.split()) <= 9
