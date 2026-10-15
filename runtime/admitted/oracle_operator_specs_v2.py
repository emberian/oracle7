#!/usr/bin/env python3
"""ORACLE OPERATOR SPECS v2 - the claim that the seventh operator costs a spec,
tested by writing five more and changing nothing else.

v1 shipped six operators inside a host that supplies dispatch, verification,
refusal, passthrough and witness recording. The claim made at the time was that
adding a capability would now be a data change. This file is that claim under
test: five new operators, no edit to the host, no edit to v1, and no new
discipline written anywhere. If the claim is false, it fails here.

The five were chosen for one property above all: a second implementation that is
genuinely a different method rather than the same method retyped. That is the
weakest joint in the design, because an author under time pressure will write the
same algorithm twice and call it verified. So:

    combinations      multiplicative formula  vs  Pascal's triangle by addition
    prime_factorise   trial division          vs  a sieve, then division
    days_between      day-of-year arithmetic  vs  counting months one at a time
    integer_sqrt      Newton's method         vs  binary search on the answer
    fraction_arith    rational arithmetic     vs  cross-multiplication by hand

None of those pairs share a line of reasoning. Where a pairing IS close, the spec
says so in `independence` and the panel report prints it.
"""

from __future__ import annotations

import re
from fractions import Fraction

from oracle_operator_specs_v1 import (SPECS as _V1_SPECS, NotOurs, OutOfFragment,
                                      _nums, _fmt)


# ── 7. combinations and permutations ──────────────────────────────────────────
_COMB_RX = re.compile(
    r'\b(?:how many ways|combinations?|permutations?|choose|n ?c ?r|n ?p ?r)\b', re.I)


def _comb_parse(s):
    ns = [n for n in _nums(s) if n >= 0]
    if len(ns) < 2:
        raise NotOurs('no pair of counts here')
    # "choose 3 from 10" names the SMALLER count first, "10 choose 3" the larger.
    # Reading both the same way made it decline a valid question and, worse, answer
    # an impossible one: "choose 12 from 5" came back 792 instead of a refusal.
    m = re.search(r'(\d+)\s+(?:things?\s+|items?\s+)?(?:from|out of)\s+(\d+)', s, re.I)
    if m:
        k, n = int(m.group(1)), int(m.group(2))
    else:
        n, k = ns[0], ns[1]
    if k > n:
        raise OutOfFragment('you cannot choose %d things from %d' % (k, n))
    if n > 400:
        raise OutOfFragment('I keep this exact, and %d is past where I will' % n)
    want = 'perm' if re.search(r'\bpermutation|arrangement|order matters\b', s, re.I) \
        else 'comb'
    return {'n': n, 'k': k, 'want': want}


def _comb_fn(a):
    n, k, steps = a['n'], a['k'], []
    if a['want'] == 'perm':
        out = 1
        for i in range(k):
            out *= (n - i)
            steps.append('x %d' % (n - i))
        return out, ['multiply %d terms counting down from %d' % (k, n)] + steps[:4]
    num = den = 1
    for i in range(k):
        num *= (n - i)
        den *= (i + 1)
    steps.append('%d! / (%d! x %d!) reduces to %d / %d' % (n, k, n - k, num, den))
    return num // den, steps + ['%d / %d = %d' % (num, den, num // den)]


def _comb_ref(a):
    """Pascal's triangle: addition only, no factorials anywhere."""
    n, k = a['n'], a['k']
    if a['want'] == 'perm':
        row = [1]
        for r in range(1, n + 1):                # build C(n,k) then multiply by k!
            row = [1] + [row[i] + row[i + 1] for i in range(len(row) - 1)] + [1]
        c = row[k]
        f = 1
        for i in range(2, k + 1):
            f *= i
        return c * f
    row = [1]
    for _r in range(n):
        row = [1] + [row[i] + row[i + 1] for i in range(len(row) - 1)] + [1]
    return row[k]


# ── 8. prime factorisation ────────────────────────────────────────────────────
_FACT_RX = re.compile(
    r'\b(?:prime factor(?:s|isation|ization)?|factorise|factorize|is\s+\d+\s+prime)\b',
    re.I)


def _fact_parse(s):
    ns = [n for n in _nums(s) if n > 1]
    if not ns:
        raise NotOurs('no number above one here')
    n = ns[0]
    if n > 10 ** 7:
        raise OutOfFragment('%d is larger than I will factor exactly' % n)
    return {'n': n, 'want': 'prime' if re.search(r'\bis\s+\d+\s+prime\b', s, re.I)
            else 'factors'}


def _fact_fn(a):
    n, d, out, steps = a['n'], 2, [], []
    while d * d <= n:
        while n % d == 0:
            out.append(d)
            steps.append('divides by %d, leaving %d' % (d, n // d))
            n //= d
        d += 1
    if n > 1:
        out.append(n)
        steps.append('%d is left and is prime' % n)
    if a['want'] == 'prime':
        return ('yes' if len(out) == 1 else 'no'), steps
    return ' x '.join(str(p) for p in out), steps


def _fact_ref(a):
    """Sieve first, then divide by the primes it found. No trial division loop."""
    n = a['n']
    limit = int(n ** 0.5) + 1
    sieve = bytearray([1]) * (limit + 1)
    sieve[0:2] = b'\x00\x00'
    for p in range(2, int(limit ** 0.5) + 1):
        if sieve[p]:
            sieve[p * p::p] = bytearray(len(sieve[p * p::p]))
    primes = [i for i in range(2, limit + 1) if sieve[i]]
    out, m = [], n
    for p in primes:
        while m % p == 0:
            out.append(p)
            m //= p
    if m > 1:
        out.append(m)
    if a['want'] == 'prime':
        return 'yes' if len(out) == 1 else 'no'
    return ' x '.join(str(p) for p in out)


# ── 9. days between dates ─────────────────────────────────────────────────────
_DATE_RX = re.compile(
    r'\b(?:how many days|days between|days from)\b.*?(\d{4})-(\d{1,2})-(\d{1,2})'
    r'.*?(\d{4})-(\d{1,2})-(\d{1,2})', re.I | re.S)
_MDAYS = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]


def _leap(y):
    return y % 4 == 0 and (y % 100 != 0 or y % 400 == 0)


def _date_parse(s):
    m = _DATE_RX.search(s)
    if not m:
        raise NotOurs('no pair of ISO dates here')
    y1, m1, d1, y2, m2, d2 = (int(g) for g in m.groups())
    for y, mo, d in ((y1, m1, d1), (y2, m2, d2)):
        if not (1 <= mo <= 12):
            raise OutOfFragment('%d is not a month' % mo)
        dim = _MDAYS[mo - 1] + (1 if mo == 2 and _leap(y) else 0)
        if not (1 <= d <= dim):
            raise OutOfFragment('%04d-%02d has no day %d' % (y, mo, d))
        if y < 1600:
            raise OutOfFragment('I use the Gregorian calendar and stop at 1600')
    return {'a': (y1, m1, d1), 'b': (y2, m2, d2)}


def _ordinal(y, m, d):
    days = 365 * (y - 1) + (y - 1) // 4 - (y - 1) // 100 + (y - 1) // 400
    for i in range(m - 1):
        days += _MDAYS[i] + (1 if i == 1 and _leap(y) else 0)
    return days + d


def _date_fn(a):
    o1, o2 = _ordinal(*a['a']), _ordinal(*a['b'])
    return abs(o2 - o1), ['day number of the first date is %d' % o1,
                          'day number of the second is %d' % o2,
                          '%d - %d = %d' % (max(o1, o2), min(o1, o2), abs(o2 - o1))]


def _date_ref(a):
    """Walk month by month from the earlier date. No day-number formula."""
    (y1, m1, d1), (y2, m2, d2) = sorted([a['a'], a['b']])
    total, y, m = 0, y1, m1
    while (y, m) != (y2, m2):
        total += _MDAYS[m - 1] + (1 if m == 2 and _leap(y) else 0)
        m += 1
        if m > 12:
            m, y = 1, y + 1
    return abs(total + d2 - d1)


# ── 10. integer square root ───────────────────────────────────────────────────
_SQRT_RX = re.compile(
    r'\b(?:square root|sqrt|perfect square)\b', re.I)


def _sqrt_parse(s):
    ns = [n for n in _nums(s) if n >= 0]
    if not ns:
        raise NotOurs('no number here')
    n = ns[0]
    if n > 10 ** 18:
        raise OutOfFragment('that is past the range I keep exact')
    return {'n': n, 'want': 'perfect' if re.search(r'perfect square', s, re.I)
            else 'root'}


def _sqrt_fn(a):
    """Newton's method."""
    n = a['n']
    if n < 2:
        r, steps = n, ['%d is its own root' % n]
    else:
        x, steps = n, []
        while True:
            nxt = (x + n // x) // 2
            steps.append('estimate %d' % nxt)
            if nxt >= x:
                break
            x = nxt
        r = x
    if a['want'] == 'perfect':
        return ('yes' if r * r == n else 'no'), steps[:4] + [
            '%d x %d = %d' % (r, r, r * r)]
    return r, steps[:4] + ['%d x %d = %d, and %d is not a square below it'
                           % (r, r, r * r, (r + 1) * (r + 1))]


def _sqrt_ref(a):
    """Binary search on the answer. No iteration toward a fixed point."""
    n = a['n']
    lo, hi = 0, max(1, n)
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if mid * mid <= n:
            lo = mid
        else:
            hi = mid - 1
    return ('yes' if lo * lo == n else 'no') if a['want'] == 'perfect' else lo


# ── 11. fraction arithmetic ───────────────────────────────────────────────────
_FRAC_RX = re.compile(r'\b\d+\s*/\s*\d+\s*([-+*/]|plus|minus|times|over)\s*\d+\s*/\s*\d+')


def _frac_parse(s):
    m = re.search(r'(\d+)\s*/\s*(\d+)\s*([-+*/]|plus|minus|times|over)\s*(\d+)\s*/\s*(\d+)',
                  s, re.I)
    if not m:
        raise NotOurs('no pair of fractions here')
    a, b, op, c, d = m.group(1), m.group(2), m.group(3).lower(), m.group(4), m.group(5)
    op = {'plus': '+', 'minus': '-', 'times': '*', 'over': '/'}.get(op, op)
    if int(b) == 0 or int(d) == 0:
        raise OutOfFragment('a fraction cannot have zero underneath')
    if op == '/' and int(c) == 0:
        raise OutOfFragment('I will not divide by zero')
    return {'a': int(a), 'b': int(b), 'c': int(c), 'd': int(d), 'op': op}


def _frac_fn(a):
    x, y = Fraction(a['a'], a['b']), Fraction(a['c'], a['d'])
    out = {'+': x + y, '-': x - y, '*': x * y, '/': (x / y if y else None)}[a['op']]
    return out, ['%s %s %s' % (x, a['op'], y), 'gives %s' % _fmt(out)]


def _frac_ref(a):
    """Cross-multiplication by hand, then reduce with a gcd computed here."""
    b, d = a['b'], a['d']
    if a['op'] == '+':
        num, den = a['a'] * d + a['c'] * b, b * d
    elif a['op'] == '-':
        num, den = a['a'] * d - a['c'] * b, b * d
    elif a['op'] == '*':
        num, den = a['a'] * a['c'], b * d
    else:
        num, den = a['a'] * d, b * a['c']
    g, x, y = 0, abs(num), abs(den)
    while y:
        x, y = y, x % y
    g = x or 1
    if den < 0:
        num, den = -num, -den
    return Fraction(num // g, den // g)


NEW_SPECS = [
    {'name': 'combinations', 'family': 'counting',
     'trigger': _COMB_RX, 'parse': _comb_parse, 'fn': _comb_fn, 'ref': _comb_ref,
     'render': lambda a, v, s: ('There are %s %s.'
                                % (v, 'arrangements' if a['want'] == 'perm'
                                   else 'combinations')),
     'warrant': 'computation',
     'independence': 'strong: multiplicative formula against Pascal\'s triangle, '
                     'which uses addition only and no factorials',
     'fragment': 'choosing k from n, both whole, n up to 400'},

    {'name': 'prime_factorise', 'family': 'number_theory',
     'trigger': _FACT_RX, 'parse': _fact_parse, 'fn': _fact_fn, 'ref': _fact_ref,
     'render': lambda a, v, s: (('%d is prime.' if v == 'yes' else '%d is not prime.')
                                % a['n'] if a['want'] == 'prime'
                                else '%d factors as %s.' % (a['n'], v)),
     'warrant': 'computation',
     'independence': 'strong: trial division against a sieve of Eratosthenes',
     'fragment': 'whole numbers above one, up to ten million'},

    {'name': 'days_between', 'family': 'calendar',
     'trigger': re.compile(r'\bdays\b.*\d{4}-\d{1,2}-\d{1,2}', re.I | re.S),
     'parse': _date_parse, 'fn': _date_fn, 'ref': _date_ref,
     'render': lambda a, v, s: 'There are %s days between them.' % v,
     'warrant': 'computation',
     'independence': 'strong: a day-number formula against walking the calendar '
                     'one month at a time',
     'fragment': 'two ISO dates from 1600 onwards, Gregorian'},

    {'name': 'integer_sqrt', 'family': 'number_theory',
     'trigger': _SQRT_RX, 'parse': _sqrt_parse, 'fn': _sqrt_fn, 'ref': _sqrt_ref,
     'render': lambda a, v, s: ('%d is %s perfect square.'
                                % (a['n'], 'a' if v == 'yes' else 'not a')
                                if a['want'] == 'perfect'
                                else 'The integer square root of %d is %s.'
                                     % (a['n'], v)),
     'warrant': 'computation',
     'independence': 'strong: Newton iteration against binary search on the answer',
     'fragment': 'non-negative whole numbers, exact, no decimals'},

    {'name': 'fraction_arith', 'family': 'number_theory',
     'trigger': _FRAC_RX, 'parse': _frac_parse, 'fn': _frac_fn, 'ref': _frac_ref,
     'render': lambda a, v, s: '%d/%d %s %d/%d is %s.' % (a['a'], a['b'], a['op'],
                                                          a['c'], a['d'], _fmt(v)),
     'warrant': 'computation',
     'independence': 'moderate: library rationals against hand cross-multiplication '
                     'with a gcd written here; the arithmetic differs, the algebra '
                     'is the same',
     'fragment': 'two fractions, one operation, exact'},
]

SPECS = list(_V1_SPECS) + NEW_SPECS
SPEC_BY_NAME = {s['name']: s for s in SPECS}
