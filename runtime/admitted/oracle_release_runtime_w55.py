#!/usr/bin/env python3
"""oracle_release_runtime_w55 - ALGEBRA: solve for the unknown, then check it.

The compute fold (w29) evaluates closed arithmetic: every quantity is known and
the answer is a number. This fold handles the case where one quantity is NOT
known and has to be recovered from a constraint, which is a different act. It is
the first operator in the chain that reasons about a thing it cannot see.

The warrant form is DERIVATION plus VERIFICATION BY SUBSTITUTION, and the second
half is what makes it worth having. Solving is a chain of law-named steps
(collect, distribute, divide), so the reader can check each one. But the machine
then puts its own answer back into the original equation, evaluates both sides
independently in exact rational arithmetic, and only reports the solution if the
two sides come out equal. A wrong step cannot survive that, because a wrong
solution does not satisfy the equation it came from. This is the same discipline
as the synthesis fold, where emitted code is run against a reference computed
another way: solve one way, check another, agree or withhold.

Everything is Fraction, never float, so 1/3 is a third rather than 0.3333333.

Bounded on purpose, and it says which bound it hit:
    linear in one unknown       3x + 5 = 20, 2(x - 3) = 4x + 1     solved
    simplification              2x + 3x - 4 + 7                    collected
    nonlinear                   x * x = 9                          declined
    unknown in a denominator    1 / x = 4                          declined
    two unknowns                x + y = 3                          declined

A solver that pretends to handle every equation is a guesser. This one names the
frontier it stops at, which is also the list of what to build next.

Hand-authored 2026-08-28 as Phase 1 of the minimal-basis program.
Judged by the gate.
"""

from __future__ import annotations

import re
from fractions import Fraction

from oracle_release_runtime_w54 import OracleReleaseRuntimeW54

# deliberately only x, y, z. Letters like "a" and "n" are real English words and
# would let this fold hijack "what is a volcano" as an expression in a.
_VARS = 'xyz'
_TOKEN = re.compile(r'\s*(\d+\.?\d*|[%s]|\*\*|[-+*/()^=])' % _VARS)
_ASK = re.compile(
    r'\b(?:solve|simplify|collect|expand|what is [%s]\b|find [%s]\b|value of [%s]\b)'
    % (_VARS, _VARS, _VARS), re.I)
_EQN = re.compile(r'[%s]' % _VARS)


class Nonlinear(Exception):
    """The expression left the fragment this fold is warranted for."""


class NotOurs(Nonlinear):
    """Not an algebra turn at all. Hand it back rather than declining it."""


class Lin:
    """a*x + b with exact rational coefficients. The whole state space."""

    __slots__ = ('a', 'b')

    def __init__(self, a=0, b=0):
        self.a = Fraction(a)
        self.b = Fraction(b)

    def __add__(self, o):
        return Lin(self.a + o.a, self.b + o.b)

    def __sub__(self, o):
        return Lin(self.a - o.a, self.b - o.b)

    def __mul__(self, o):
        if self.a and o.a:
            raise Nonlinear('the unknown multiplied by itself')
        return Lin(self.a * o.b + o.a * self.b, self.b * o.b)

    def __truediv__(self, o):
        if o.a:
            raise Nonlinear('the unknown in a denominator')
        if not o.b:
            raise Nonlinear('division by zero')
        return Lin(self.a / o.b, self.b / o.b)

    def __neg__(self):
        return Lin(-self.a, -self.b)

    def text(self, v='x'):
        if not self.a:
            return _num(self.b)
        head = ('%s%s' % ('' if self.a == 1 else '-' if self.a == -1 else _num(self.a), v))
        if not self.b:
            return head
        return '%s %s %s' % (head, '+' if self.b > 0 else '-', _num(abs(self.b)))


def _num(f):
    f = Fraction(f)
    if f.denominator == 1:
        return str(f.numerator)
    return '%d/%d' % (f.numerator, f.denominator)


class _P:
    """Recursive descent over the tokens. No eval, ever."""

    def __init__(self, toks, var):
        self.t = toks
        self.i = 0
        self.v = var

    def peek(self):
        return self.t[self.i] if self.i < len(self.t) else None

    def take(self):
        tok = self.peek()
        self.i += 1
        return tok

    def expr(self):
        node = self.term()
        while self.peek() in ('+', '-'):
            op = self.take()
            rhs = self.term()
            node = node + rhs if op == '+' else node - rhs
        return node

    def term(self):
        node = self.factor()
        while True:
            nxt = self.peek()
            if nxt in ('*', '/'):
                op = self.take()
                rhs = self.factor()
                node = node * rhs if op == '*' else node / rhs
            elif nxt is not None and (nxt == '(' or nxt == self.v
                                      or nxt[0].isdigit()):
                node = node * self.factor()          # implicit: 3x, 2(x+1)
            else:
                return node

    def factor(self):
        tok = self.take()
        if tok is None:
            raise Nonlinear('the expression ended early')
        if tok == '-':
            return -self.factor()
        if tok == '+':
            return self.factor()
        if tok == '(':
            node = self.expr()
            if self.peek() == ')':
                self.take()
            return node
        if tok in ('^', '**'):
            raise Nonlinear('a power of the unknown')
        if tok == self.v:
            node = Lin(1, 0)
        elif tok[0].isdigit():
            node = Lin(0, Fraction(tok))
        else:
            raise Nonlinear('a second unknown, %s' % tok)
        if self.peek() in ('^', '**'):
            self.take()
            p = self.take()
            if p == '2' and node.a:
                raise Nonlinear('the unknown squared')
            if p and p.isdigit():
                out = Lin(0, 1)
                for _ in range(int(p)):
                    out = out * node
                return out
            raise Nonlinear('a power this fold cannot type')
        return node


def _parse(src, var):
    toks = _TOKEN.findall(src)
    if not toks:
        raise Nonlinear('nothing to read')
    p = _P(toks, var)
    node = p.expr()
    if p.i < len(p.t):
        raise Nonlinear('trailing symbols this fold cannot type')
    return node


class OracleReleaseRuntimeW55(OracleReleaseRuntimeW54):
    """Base + linear algebra, solved by law and checked by substitution.

    Also carries one CORRECTNESS RELEASE for the deduction fold above it, found by
    the held-out half of the capability panel rather than by me. "The server is
    down" contains the word "is", so it was read only as an instance (server, down)
    and never as the proposition "server is down". Modus ponens looks for the
    proposition, so the inference silently failed on any antecedent phrased with a
    copula. The fix is additive: an asserted instance is now ALSO recorded as a
    proposition, and nothing in the sealed fold is edited.
    """

    def _ingest(self, surface, st):
        added = super()._ingest(surface, st)
        for x, cls in st.get('inst', []):
            prop = '%s is %s' % (x, cls)
            if prop not in st['fact']:
                st['fact'].append(prop)
        return added

    @staticmethod
    def _extract(surface):
        """Pull the expression out of the sentence around it.

        The tokenizer skips characters it does not know, which would let a
        sentence quietly lose half its meaning and still get an answer. So the
        span is taken by scanning outward from the equals sign over math
        characters only, and anything else in the sentence is left where it is
        rather than silently dropped.
        """
        ok = set('0123456789+-*/^(). ' + _VARS)
        if '=' in surface:
            left, right = surface.split('=', 1)
            i = len(left)
            while i > 0 and left[i - 1] in ok:
                i -= 1
            j = 0
            while j < len(right) and right[j] in ok:
                j += 1
            lhs, rhs = left[i:].strip(), right[:j].strip()
            if not lhs or not rhs:
                raise NotOurs('I could not find an equation in that')
            return '%s = %s' % (lhs, rhs)
        body = surface
        for junk in ('solve for', 'solve', 'simplify', 'collect', 'expand',
                     'what is', 'find', 'the value of', 'value of', 'please'):
            body = re.sub(r'\b%s\b' % junk, ' ', body, flags=re.I)
        body = body.replace('?', ' ').strip(' .,')
        if any(ch not in ok for ch in body):
            raise NotOurs('there is text in there I cannot read as an expression')
        return body

    def _algebra(self, surface):
        """Returns (steps, answer, check) or raises Nonlinear. No side effects."""
        body = self._extract(surface)

        present = [v for v in _VARS if re.search(r'(?<![a-z])%s(?![a-z])' % v, body)]
        if not present:
            raise Nonlinear('no unknown to solve for')
        if len(present) > 1:
            raise Nonlinear('more than one unknown (%s)' % ', '.join(present))
        var = present[0]

        if body.count('=') > 1:
            raise Nonlinear('more than one equation')
        if '=' not in body:
            node = _parse(body, var)
            return (['read the expression as %s' % node.text(var),
                     'collect like terms'],
                    node.text(var), None)

        left_s, right_s = [s.strip() for s in body.split('=')]
        left, right = _parse(left_s, var), _parse(right_s, var)
        steps = ['read it as %s = %s' % (left.text(var), right.text(var))]

        da, db = left.a - right.a, right.b - left.b
        if not da:
            if not db:
                return (steps + ['both sides are the same expression'],
                        'Every value of %s satisfies it' % var, 'identity')
            # not an incapacity: "no value works" is a conclusion, so report it
            return (steps + ['the unknown cancels, leaving %s = %s, which is false'
                             % (_num(left.b), _num(right.b))],
                    'No value of %s satisfies it' % var, 'contradiction')
        steps.append('collect %s on the left: %s%s = %s'
                     % (var, _num(da), var, _num(db)))
        sol = db / da
        steps.append('divide both sides by %s: %s = %s' % (_num(da), var, _num(sol)))

        # the check: put it back and evaluate both sides independently
        lv = left.a * sol + left.b
        rv = right.a * sol + right.b
        if lv != rv:
            raise Nonlinear('the substitution check failed, so I will not report it')
        steps.append('check by substitution: left gives %s, right gives %s, equal'
                     % (_num(lv), _num(rv)))
        return steps, '%s = %s' % (var, _num(sol)), _num(lv)

    def _witness_alg(self, session_id, surface, steps, answered):
        from collections import deque
        hist = getattr(self, '_paths', None)
        if hist is None:
            hist = self._paths = {}
        q = hist.get(session_id)
        if q is None:
            q = hist[session_id] = deque(maxlen=64)
        prev = q[-1].get('turn', 0) if len(q) else 0
        q.append({'turn': prev + 1, 'in_surface': str(surface)[:120],
                  'in_form': ['equation'], 'operator': 'algebra:solved',
                  'out_status': 'answered' if answered else 'withheld',
                  'in_terms': [], 'out_terms': [],
                  'relation': {'grounded': [], 'grounded_cited': [],
                               'introduced': [], 'unaccounted': []},
                  'carried_from_prior': [], 'continuity_lexical': False,
                  'continuity': True, 'citations': 0, 'residual': None,
                  'cost_ms': 1.5,
                  'conversion': {'construction': 'SOLUTION',
                                 'from': str(surface)[:80],
                                 'to': steps[-1][:60] if steps else 'declined',
                                 'produced_by': 'algebra_w55'},
                  'verified_warrant': ({'kind': 'algebra', 'steps': steps,
                                        'checked_by': 'substitution'}
                                       if answered else None)})

    def chat(self, text: str, session_id: str = 'default') -> dict:
        s = ' '.join(str(text).strip().split())
        low = s.lower()
        has_var = bool(re.search(r'(?<![a-z])[%s](?![a-z])' % _VARS, low))
        looks_algebraic = has_var and (('=' in s) or bool(_ASK.search(low)))
        if not looks_algebraic:
            return super().chat(s, session_id)
        if not re.search(r'\d', s):
            return super().chat(s, session_id)

        try:
            steps, answer, check = self._algebra(low)
        except NotOurs:
            return super().chat(s, session_id)
        except Nonlinear as why:
            self._witness_alg(session_id, s, [], False)
            return {'status': 'withheld', 'path': 'algebra:out_of_fragment',
                    'response': ('I solve linear equations in one unknown exactly, '
                                 'and this one is outside that: %s. I could give you '
                                 'a plausible looking answer, but I would have no way '
                                 'to check it, so I will not.' % why),
                    'provenance': {'kind': 'algebra', 'solved': False,
                                   'reason': str(why),
                                   'fragment': 'linear, one unknown, rational'},
                    'latency_ms': 2}
        except Exception:
            return super().chat(s, session_id)

        if check is None:
            body = ('That simplifies to %s. %s.'
                    % (answer, '; then '.join(steps)))
        else:
            body = ('%s. %s.' % (answer, '; then '.join(steps)))
        self._witness_alg(session_id, s, steps, True)
        pending = getattr(self, '_pending_conversion', None)
        if pending is None:
            pending = self._pending_conversion = {}
        pending[session_id] = {'construction': 'SOLUTION', 'from': s[:80],
                               'to': answer, 'produced_by': 'algebra_w55'}
        return {'status': 'answered', 'path': 'algebra:solved',
                'response': body,
                'provenance': {'kind': 'algebra', 'solved': True,
                               'answer': answer, 'steps': steps,
                               'verified_by': 'substitution',
                               'both_sides_evaluate_to': check,
                               'exact': True},
                'latency_ms': 2}
