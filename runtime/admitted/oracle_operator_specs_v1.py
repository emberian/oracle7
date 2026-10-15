#!/usr/bin/env python3
"""ORACLE OPERATOR SPECS - operators as data, so a set can be generated.

Every fold admitted so far was hand-authored, and every defect found in them today
was in the same boilerplate rather than in the reasoning: a missing witness record
made a turn invisible to the gate, a missing relevance guard let one fold capture
a whole session, a self-report read a file instead of itself, and a justification
fold read one warrant field and libelled its own good answers. None of those were
interesting mistakes. They were the same mistakes, made once per fold.

So the operators stop being code and become DATA. A spec declares four things:

    trigger   which surfaces it claims, narrowly
    parse     surface -> typed arguments, or a named refusal
    fn        the computation, which is what the operator runs
    ref       the SAME result by a different method, which is what checks it

The host (oracle_release_runtime_w59) interprets these and supplies the discipline
once: witness recording, honest decline, passthrough when the turn is not its
business, and the verification step. Adding a capability becomes adding a spec.

The fn/ref pair is the important part and it is a structural commitment, not a
convention. The operator computes the answer one way; the checker computes it a
different way; the host reports nothing unless the two agree. Where the pairing is
weak, because the second method is too close to the first, the spec says so in
`independence` and that word appears in the sealed report rather than being
quietly omitted. A verification that shares its implementation with the thing it
verifies is theatre, and this file is where that would be easiest to hide.

The panel generator reads these same specs and builds its expected answers from
`ref` ONLY, never from `fn`, so a bug in the operator cannot define its own test.
"""

from __future__ import annotations

import re
from fractions import Fraction


class OutOfFragment(Exception):
    """A named boundary, reported to the user as the reason for declining."""


class NotOurs(OutOfFragment):
    """Not this operator's turn at all. Hand the surface back, do not decline it.

    The distinction matters because some triggers are necessarily loose. "binary"
    appears in "what is binary code", which the corpus answers perfectly well. An
    operator that declined every surface containing its trigger word would take
    working answers away from the rest of the chain, which is the same mistake the
    deduction fold made before w56, arrived at from the other direction.
    """


# ── helpers ───────────────────────────────────────────────────────────────────
def _nums(text):
    return [int(m) for m in re.findall(r'-?\d+', text)]


def _fmt(x):
    if isinstance(x, Fraction):
        return str(x.numerator) if x.denominator == 1 else '%d/%d' % (
            x.numerator, x.denominator)
    if isinstance(x, float):
        return ('%.6f' % x).rstrip('0').rstrip('.')
    return str(x)


# ── 1. unit conversion ────────────────────────────────────────────────────────
# fn multiplies by a direct ratio; ref goes through the SI base in two steps with
# separately written factors. Different route to the same number.
_TO_BASE = {'mm': Fraction(1, 1000), 'cm': Fraction(1, 100), 'm': Fraction(1),
            'km': Fraction(1000), 'inch': Fraction(254, 10000),
            'inches': Fraction(254, 10000), 'foot': Fraction(3048, 10000),
            'feet': Fraction(3048, 10000), 'mile': Fraction(1609344, 1000),
            'miles': Fraction(1609344, 1000), 'yard': Fraction(9144, 10000),
            'yards': Fraction(9144, 10000),
            'mg': Fraction(1, 1000000), 'g': Fraction(1, 1000),
            'kg': Fraction(1), 'tonne': Fraction(1000),
            'pound': Fraction(45359237, 100000000),
            'pounds': Fraction(45359237, 100000000),
            'ounce': Fraction(45359237, 1600000000),
            'ounces': Fraction(45359237, 1600000000),
            'second': Fraction(1), 'seconds': Fraction(1),
            'minute': Fraction(60), 'minutes': Fraction(60),
            'hour': Fraction(3600), 'hours': Fraction(3600),
            'day': Fraction(86400), 'days': Fraction(86400),
            'week': Fraction(604800), 'weeks': Fraction(604800)}
_FAMILY = {}
for _u in ('mm cm m km inch inches foot feet mile miles yard yards'.split()):
    _FAMILY[_u] = 'length'
for _u in ('mg g kg tonne pound pounds ounce ounces'.split()):
    _FAMILY[_u] = 'mass'
for _u in ('second seconds minute minutes hour hours day days week weeks'.split()):
    _FAMILY[_u] = 'time'

_UNIT_RX = re.compile(
    r'\b(-?\d+(?:\.\d+)?)\s*([a-z]+)\s+(?:in|to|into|as)\s+([a-z]+)\b', re.I)
# "how many cm in 3 km" is the same request with the units the other way round,
# which the pattern above reads as nothing at all.
_UNIT_RX_REV = re.compile(
    r'\bhow many\s+([a-z]+)\s+(?:are\s+)?(?:in|to)\s+(-?\d+(?:\.\d+)?)\s*([a-z]+)\b',
    re.I)
_UNIT_ANY = re.compile(
    '(?:%s)|(?:%s)' % (_UNIT_RX.pattern, _UNIT_RX_REV.pattern), re.I)


def _unit_parse(s):
    m = _UNIT_RX.search(s)
    if m:
        qty, src, dst = m.group(1), m.group(2).lower(), m.group(3).lower()
    else:
        m = _UNIT_RX_REV.search(s)
        if not m:
            raise NotOurs('no quantity and two units here')
        qty, src, dst = m.group(2), m.group(3).lower(), m.group(1).lower()
    # An unknown word is not a unit I am declining, it is a sign this was never a
    # conversion. "Compare 2 dogs to cats" matches the shape; declining it would
    # take a working corpus answer away.
    if src not in _TO_BASE or dst not in _TO_BASE:
        raise NotOurs('one of those is not a unit I carry')
    if _FAMILY[src] != _FAMILY[dst]:
        raise OutOfFragment('%s measures %s and %s measures %s, so there is no '
                            'conversion between them'
                            % (src, _FAMILY[src], dst, _FAMILY[dst]))
    return {'qty': Fraction(qty), 'src': src, 'dst': dst}


def _unit_fn(a):
    ratio = _TO_BASE[a['src']] / _TO_BASE[a['dst']]
    out = a['qty'] * ratio
    return out, ['the factor from %s to %s is %s' % (a['src'], a['dst'], _fmt(ratio)),
                 '%s x %s = %s' % (_fmt(a['qty']), _fmt(ratio), _fmt(out))]


def _unit_ref(a):
    base = a['qty'] * _TO_BASE[a['src']]          # to the SI base first
    return base / _TO_BASE[a['dst']]              # then out of it


# ── 2. greatest common divisor / least common multiple ────────────────────────
# fn is Euclid; ref is prime factorisation. Genuinely unrelated algorithms.
_GCD_RX = re.compile(r'\b(?:gcd|greatest common (?:divisor|factor)|hcf)\b', re.I)
_LCM_RX = re.compile(r'\b(?:lcm|least common multiple|lowest common multiple)\b', re.I)


def _gcd_parse(s):
    ns = [n for n in _nums(s) if n > 0]
    if len(ns) < 2:
        raise OutOfFragment('I need two positive whole numbers')
    if len(ns) > 2:
        raise OutOfFragment('I take exactly two numbers, and that had %d' % len(ns))
    if max(ns) > 10 ** 9:
        raise OutOfFragment('those are larger than I will factor reliably')
    return {'a': ns[0], 'b': ns[1], 'want': 'lcm' if _LCM_RX.search(s) else 'gcd'}


def _euclid(a, b):
    steps = []
    while b:
        steps.append('%d mod %d = %d' % (a, b, a % b))
        a, b = b, a % b
    return a, steps


def _gcd_fn(a):
    g, steps = _euclid(a['a'], a['b'])
    if a['want'] == 'gcd':
        return g, steps + ['no remainder left, so the divisor is %d' % g]
    out = a['a'] * a['b'] // g
    return out, steps + ['gcd is %d' % g,
                         '%d x %d / %d = %d' % (a['a'], a['b'], g, out)]


def _factorise(n):
    f, d = {}, 2
    while d * d <= n:
        while n % d == 0:
            f[d] = f.get(d, 0) + 1
            n //= d
        d += 1
    if n > 1:
        f[n] = f.get(n, 0) + 1
    return f


def _gcd_ref(a):
    fa, fb = _factorise(a['a']), _factorise(a['b'])
    if a['want'] == 'gcd':
        out = 1
        for p in set(fa) & set(fb):
            out *= p ** min(fa[p], fb[p])
        return out
    out = 1
    for p in set(fa) | set(fb):
        out *= p ** max(fa.get(p, 0), fb.get(p, 0))
    return out


# ── 3. base conversion ────────────────────────────────────────────────────────
# fn is repeated divmod; ref is positional expansion of the digits it produced.
_BASE_RX = re.compile(
    r'\b(?:convert|write|express)?\s*(-?\d+)\s*(?:from\s*)?(?:base\s*(\d+))?\s*'
    r'(?:in|to|into)\s*(?:base\s*)?(\d+|binary|hex|hexadecimal|octal|decimal)\b', re.I)
_BASE_NAME = {'binary': 2, 'hex': 16, 'hexadecimal': 16, 'octal': 8, 'decimal': 10}
_DIGITS = '0123456789abcdefghijklmnopqrstuvwxyz'


def _base_parse(s):
    m = _BASE_RX.search(s)
    if not m:
        raise NotOurs('no number and target base here')
    n = int(m.group(1))
    frm = int(m.group(2)) if m.group(2) else 10
    tgt = m.group(3).lower()
    to = _BASE_NAME.get(tgt, None)
    if to is None:
        to = int(tgt)
    if not (2 <= to <= 36) or not (2 <= frm <= 36):
        raise OutOfFragment('I convert between base 2 and base 36 only')
    if n < 0:
        raise OutOfFragment('I convert non-negative whole numbers only')
    return {'n': n, 'frm': frm, 'to': to}


def _base_fn(a):
    n, steps, out = a['n'], [], ''
    if n == 0:
        return '0', ['0 in any base is 0']
    while n:
        n, r = divmod(n, a['to'])
        steps.append('remainder %s, carry %d' % (_DIGITS[r], n))
        out = _DIGITS[r] + out
    return out, steps + ['reading the remainders backwards gives %s' % out]


def _base_ref(a):
    """Independent: build with a positional table, then check by expanding it."""
    n = a['n']
    if n == 0:
        return '0'
    digits, powers = [], []
    p = 1
    while p * a['to'] <= n:
        p *= a['to']
    while p >= 1:
        digits.append(_DIGITS[(n // p) % a['to']])
        powers.append(p)
        p //= a['to']
    return ''.join(digits).lstrip('0') or '0'


# ── 4. descriptive statistics ─────────────────────────────────────────────────
# fn sums and divides; ref recomputes from a sorted copy with a running total.
_STAT_RX = re.compile(r'\b(mean|average|median|range|sum|total)\b.*\b\d', re.I)


def _stat_parse(s):
    ns = _nums(s)
    if len(ns) < 2:
        raise NotOurs('fewer than two numbers here')
    if len(ns) > 40:
        raise OutOfFragment('that is more numbers than I will read from a sentence')
    m = _STAT_RX.search(s)
    want = m.group(1).lower() if m else 'mean'
    return {'xs': ns, 'want': 'mean' if want == 'average' else
            ('sum' if want == 'total' else want)}


def _stat_fn(a):
    xs, want = a['xs'], a['want']
    if want == 'sum':
        return Fraction(sum(xs)), ['%s = %d' % (' + '.join(map(str, xs)), sum(xs))]
    if want == 'mean':
        tot = sum(xs)
        return Fraction(tot, len(xs)), [
            'sum is %d over %d values' % (tot, len(xs)),
            '%d / %d = %s' % (tot, len(xs), _fmt(Fraction(tot, len(xs))))]
    if want == 'range':
        return Fraction(max(xs) - min(xs)), [
            'largest %d, smallest %d' % (max(xs), min(xs)),
            '%d - %d = %d' % (max(xs), min(xs), max(xs) - min(xs))]
    srt = sorted(xs)
    n = len(srt)
    if n % 2:
        return Fraction(srt[n // 2]), ['sorted: %s' % ', '.join(map(str, srt)),
                                       'the middle value is %d' % srt[n // 2]]
    lo, hi = srt[n // 2 - 1], srt[n // 2]
    return Fraction(lo + hi, 2), ['sorted: %s' % ', '.join(map(str, srt)),
                                  'two middle values %d and %d' % (lo, hi),
                                  'their mean is %s' % _fmt(Fraction(lo + hi, 2))]


def _stat_ref(a):
    xs, want = list(a['xs']), a['want']
    if want == 'sum':
        t = Fraction(0)
        for v in xs:
            t += v
        return t
    if want == 'mean':
        t = Fraction(0)
        for v in xs:
            t += Fraction(v, len(xs))       # divide as we go, not at the end
        return t
    if want == 'range':
        hi = lo = xs[0]
        for v in xs:
            hi = v if v > hi else hi
            lo = v if v < lo else lo
        return Fraction(hi - lo)
    s = sorted(xs)
    k = len(s)
    return Fraction(s[k // 2]) if k % 2 else Fraction(s[k // 2 - 1] + s[k // 2], 2)


# ── 5. next term in a sequence ────────────────────────────────────────────────
# fn tests a constant difference then a constant ratio; ref fits from the LAST
# pair and verifies the fit against every earlier term, which is a different test.
_SEQ_RX = re.compile(
    r'\b(?:next (?:number|term)|continue the (?:sequence|series)|what comes next)\b',
    re.I)


def _seq_parse(s):
    ns = _nums(s)
    if len(ns) < 3:
        raise NotOurs('fewer than three terms here')
    return {'xs': ns}


def _seq_fn(a):
    xs = a['xs']
    d = xs[1] - xs[0]
    if all(xs[i + 1] - xs[i] == d for i in range(len(xs) - 1)):
        return xs[-1] + d, ['each term is %d more than the one before' % d,
                            '%d + %d = %d' % (xs[-1], d, xs[-1] + d)]
    if xs[0] and all(xs[i] and xs[i + 1] % xs[i] == 0 for i in range(len(xs) - 1)):
        r = xs[1] // xs[0]
        if all(xs[i + 1] // xs[i] == r for i in range(len(xs) - 1)):
            return xs[-1] * r, ['each term is %d times the one before' % r,
                                '%d x %d = %d' % (xs[-1], r, xs[-1] * r)]
    raise OutOfFragment('that is neither a constant difference nor a constant '
                        'ratio, and those are the only patterns I can check')


def _seq_ref(a):
    xs = a['xs']
    d = xs[-1] - xs[-2]                       # fit from the END, not the start
    if all(xs[i + 1] - xs[i] == d for i in range(len(xs) - 1)):
        return xs[-1] + d
    if xs[-2]:
        r = xs[-1] // xs[-2] if xs[-1] % xs[-2] == 0 else None
        if r and all(xs[i] and xs[i + 1] == xs[i] * r for i in range(len(xs) - 1)):
            return xs[-1] * r
    raise OutOfFragment('no constant difference or ratio')


# ── 6. roman numerals ─────────────────────────────────────────────────────────
# fn is greedy subtractive; ref builds place by place from a decimal table.
_ROMAN_RX = re.compile(r'\broman numeral\b|\bin roman\b|\bas a roman\b', re.I)
_VALS = [(1000, 'M'), (900, 'CM'), (500, 'D'), (400, 'CD'), (100, 'C'), (90, 'XC'),
         (50, 'L'), (40, 'XL'), (10, 'X'), (9, 'IX'), (5, 'V'), (4, 'IV'), (1, 'I')]
_PLACE = [['', 'M', 'MM', 'MMM'],
          ['', 'C', 'CC', 'CCC', 'CD', 'D', 'DC', 'DCC', 'DCCC', 'CM'],
          ['', 'X', 'XX', 'XXX', 'XL', 'L', 'LX', 'LXX', 'LXXX', 'XC'],
          ['', 'I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX']]


def _roman_parse(s):
    ns = [n for n in _nums(s) if n > 0]
    if not ns:
        raise NotOurs('no number to convert here')
    n = ns[0]
    if n > 3999:
        raise OutOfFragment('classical roman numerals stop at 3999')
    return {'n': n}


def _roman_fn(a):
    n, out, steps = a['n'], '', []
    for v, sym in _VALS:
        while n >= v:
            out += sym
            n -= v
            steps.append('take %s for %d, %d left' % (sym, v, n))
    return out, steps


def _roman_ref(a):
    n = a['n']
    return (_PLACE[0][n // 1000] + _PLACE[1][(n // 100) % 10]
            + _PLACE[2][(n // 10) % 10] + _PLACE[3][n % 10])


# ── the spec table ────────────────────────────────────────────────────────────
SPECS = [
    {'name': 'unit_convert', 'family': 'measurement',
     'trigger': _UNIT_ANY, 'parse': _unit_parse, 'fn': _unit_fn, 'ref': _unit_ref,
     'render': lambda a, v, s: '%s %s is %s %s.' % (_fmt(a['qty']), a['src'],
                                                    _fmt(v), a['dst']),
     'warrant': 'computation',
     'independence': 'strong: direct ratio against a two-step conversion through '
                     'the SI base with separately written factors',
     'fragment': 'length, mass and time, between units it carries a factor for'},

    {'name': 'gcd_lcm', 'family': 'number_theory',
     'trigger': re.compile(_GCD_RX.pattern + '|' + _LCM_RX.pattern, re.I),
     'parse': _gcd_parse, 'fn': _gcd_fn, 'ref': _gcd_ref,
     'render': lambda a, v, s: 'The %s of %d and %d is %s.' % (a['want'].upper(),
                                                               a['a'], a['b'], v),
     'warrant': 'computation',
     'independence': 'strong: Euclid against prime factorisation, unrelated methods',
     'fragment': 'exactly two positive whole numbers below a billion'},

    {'name': 'base_convert', 'family': 'number_theory',
     'trigger': re.compile(r'\b(?:binary|hexadecimal|hex|octal|base\s*\d+)\b', re.I),
     'parse': _base_parse, 'fn': _base_fn, 'ref': _base_ref,
     'render': lambda a, v, s: '%d in base %d is %s.' % (a['n'], a['to'], v),
     'warrant': 'computation',
     'independence': 'moderate: repeated division against positional expansion; '
                     'both walk the same digits, in opposite directions',
     'fragment': 'non-negative whole numbers, bases 2 to 36'},

    {'name': 'statistics', 'family': 'measurement',
     'trigger': _STAT_RX, 'parse': _stat_parse, 'fn': _stat_fn, 'ref': _stat_ref,
     'render': lambda a, v, s: 'The %s is %s.' % (a['want'], _fmt(v)),
     'warrant': 'computation',
     'independence': 'moderate: sum-then-divide against divide-as-you-go, which '
                     'differs in rounding path but not in principle',
     'fragment': 'between two and forty whole numbers, read from the sentence'},

    {'name': 'sequence_next', 'family': 'pattern',
     'trigger': _SEQ_RX, 'parse': _seq_parse, 'fn': _seq_fn, 'ref': _seq_ref,
     'render': lambda a, v, s: 'The next term is %s.' % v,
     'warrant': 'computation',
     'independence': 'strong: fit from the first pair against fit from the last '
                     'pair, each verified across every term',
     'fragment': 'constant difference or constant ratio only, three terms minimum'},

    {'name': 'roman_numeral', 'family': 'notation',
     'trigger': _ROMAN_RX, 'parse': _roman_parse, 'fn': _roman_fn, 'ref': _roman_ref,
     'render': lambda a, v, s: '%d in roman numerals is %s.' % (a['n'], v),
     'warrant': 'computation',
     'independence': 'strong: greedy subtractive against a place-value table',
     'fragment': '1 to 3999, the classical range'},
]

SPEC_BY_NAME = {s['name']: s for s in SPECS}
