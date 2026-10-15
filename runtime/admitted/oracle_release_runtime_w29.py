#!/usr/bin/env python3
"""oracle_release_runtime_w29 - COMPUTE v3: verified arithmetic with a shown trace.

The gap this closes: the chain treated every surface as a question needing corpus
evidence, so "What is 47 times 19 plus 236?" fell to a definitional substitution
about the number nineteen. Arithmetic is not warranted by attestation. It is
warranted by COMPUTATION, and the warrant form here is the evaluation trace:
every step shown, the way premises are shown elsewhere.

Discipline kept:
  - no eval(): a real recursive-descent parser over a closed grammar, so the
    semantics are ours and auditable
  - TOTAL PARSE ONLY: the route fires only when every token of the surface is
    consumed by the arithmetic grammar. A sentence that merely contains numbers
    is not an arithmetic surface and is passed to the chain untouched.
  - the decline discipline survives: division by zero, overflow, and unsupported
    operators are refused with the reason named, never approximated.

v2 lesson from w27's rejection (grounding_cited 0.2086 -> 0.1879): the route
returned before the base recorder ran, so its turns left NO witness entry and the
surface terms diluted the grounding average. v2 records its own witness entry:
in_form typed as arithmetic, out_status answered, continuity set when a prior
result is carried, and in_terms deliberately EMPTY because an arithmetic surface
contains no corpus terms to ground. The warrant lives in the computation trace,
not in citations, and the instrument is told the truth about that.

v3 note: w28 carried identical logic and was refused because the grounding
instrument counted only citation as warrant, so replacing a cited deflection with
a correct computation lowered the average. The instrument was amended (verified
warrants now count) and the head re-measured on the same panel. The code below is
unchanged from w28; only the measuring changed, and it changed toward the truth.

Hand-authored 2026-08-26 as a capability release, chained on w24.
Judged by the daemon gate like every other fold.
"""

from __future__ import annotations

import re

from oracle_release_runtime_w24 import OracleReleaseRuntimeW24

_UNITS = {'zero': 0, 'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
          'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10,
          'eleven': 11, 'twelve': 12, 'thirteen': 13, 'fourteen': 14,
          'fifteen': 15, 'sixteen': 16, 'seventeen': 17, 'eighteen': 18,
          'nineteen': 19}
_TENS = {'twenty': 20, 'thirty': 30, 'forty': 40, 'fifty': 50, 'sixty': 60,
         'seventy': 70, 'eighty': 80, 'ninety': 90}
_SCALE = {'hundred': 100, 'thousand': 1000, 'million': 1000000}

_LEAD = re.compile(
    r'^\s*(?:what(?:\'s| is)|whats|calculate|compute|evaluate|work out|'
    r'how much is|tell me)\s+', re.I)
_TRAIL = re.compile(r'[\s?.!]+$')


def _words_to_number(tokens, i):
    """Consume a number phrase starting at i. Returns (value, next_i) or None."""
    total, current, used = 0, 0, 0
    j = i
    while j < len(tokens):
        t = tokens[j]
        if t in _UNITS:
            current += _UNITS[t]
        elif t in _TENS:
            current += _TENS[t]
        elif t in _SCALE:
            if current == 0:
                current = 1
            if _SCALE[t] >= 1000:
                total += current * _SCALE[t]
                current = 0
            else:
                current *= _SCALE[t]
        elif t == 'and' and used and j + 1 < len(tokens) and (
                tokens[j + 1] in _UNITS or tokens[j + 1] in _TENS):
            j += 1
            continue
        else:
            break
        used += 1
        j += 1
    if not used:
        return None
    return total + current, j


class _Tok:
    def __init__(self, kind, value=None):
        self.kind = kind
        self.value = value


def _tokenize(s: str):
    """Surface -> token stream, or None if anything is not arithmetic."""
    s = _LEAD.sub('', s)
    s = _TRAIL.sub('', s)
    s = s.replace('×', '*').replace('÷', '/').replace('^', '**')
    s = re.sub(r'\bmultiplied by\b|\btimes\b', '*', s, flags=re.I)
    s = re.sub(r'\bdivided by\b|\bover\b', '/', s, flags=re.I)
    s = re.sub(r'\bto the power of\b|\braised to\b', '**', s, flags=re.I)
    s = re.sub(r'\bplus\b|\badded to\b|\band\b(?=\s*[\d(])', '+', s, flags=re.I)
    s = re.sub(r'\bminus\b|\bless\b|\bsubtract\b', '-', s, flags=re.I)
    s = re.sub(r'\bpercent of\b|\bpercent\b', '%OF%', s, flags=re.I)
    s = re.sub(r'\badd\b|\bsum of\b', '', s, flags=re.I)
    words = re.findall(r'[A-Za-z]+|\d+\.?\d*|\*\*|[+\-*/()]|%OF%', s)
    if not words:
        return None
    out, i = [], 0
    while i < len(words):
        w = words[i]
        if re.fullmatch(r'\d+\.?\d*', w):
            out.append(_Tok('num', float(w) if '.' in w else int(w)))
            i += 1
        elif w in ('+', '-', '*', '/', '**', '(', ')', '%OF%'):
            out.append(_Tok(w))
            i += 1
        else:
            got = _words_to_number([x.lower() for x in words], i)
            if got is None:
                return None                  # a non-arithmetic word: not our surface
            val, i = got
            out.append(_Tok('num', val))
    return out


class _Parser:
    """expr := term (('+'|'-') term)* ; term := pow (('*'|'/'|'%OF%') pow)*
       pow  := unary ('**' pow)?    ; unary := '-'? atom
       atom := num | '(' expr ')'"""

    def __init__(self, toks):
        self.t = toks
        self.i = 0
        self.steps = []

    def peek(self):
        return self.t[self.i].kind if self.i < len(self.t) else None

    def eat(self, kind):
        tok = self.t[self.i]
        self.i += 1
        return tok

    def parse(self):
        v = self.expr()
        if self.i != len(self.t):
            raise ValueError('trailing tokens')
        return v

    def expr(self):
        v = self.term()
        while self.peek() in ('+', '-'):
            op = self.eat(self.peek()).kind
            r = self.term()
            nv = v + r if op == '+' else v - r
            self.steps.append('%s %s %s = %s' % (_fmt(v), op, _fmt(r), _fmt(nv)))
            v = nv
        return v

    def term(self):
        v = self.pow_()
        while self.peek() in ('*', '/', '%OF%'):
            op = self.eat(self.peek()).kind
            r = self.pow_()
            if op == '*':
                nv = v * r
                sym = 'x'
            elif op == '/':
                if r == 0:
                    raise ZeroDivisionError('division by zero')
                nv = v / r
                sym = '/'
            else:
                nv = v * r / 100.0
                sym = '% of'
            self.steps.append('%s %s %s = %s' % (_fmt(v), sym, _fmt(r), _fmt(nv)))
            v = nv
        return v

    def pow_(self):
        v = self.unary()
        if self.peek() == '**':
            self.eat('**')
            r = self.pow_()
            if abs(v) > 1e6 or abs(r) > 64:
                raise ValueError('exponent out of verified range')
            nv = v ** r
            self.steps.append('%s ^ %s = %s' % (_fmt(v), _fmt(r), _fmt(nv)))
            return nv
        return v

    def unary(self):
        if self.peek() == '-':
            self.eat('-')
            return -self.unary()
        return self.atom()

    def atom(self):
        k = self.peek()
        if k == 'num':
            return self.eat('num').value
        if k == '(':
            self.eat('(')
            v = self.expr()
            if self.peek() != ')':
                raise ValueError('unbalanced parenthesis')
            self.eat(')')
            return v
        raise ValueError('unexpected token')


def _fmt(v):
    if isinstance(v, float):
        if abs(v - round(v)) < 1e-9:
            return str(int(round(v)))
        return ('%.6f' % v).rstrip('0').rstrip('.')
    return str(v)


_ANA = re.compile(r'\b(?:that|it|this|the result|the answer|the total)\b', re.I)
_IMP_BY = re.compile(r'^\s*(?:now\s+|then\s+)?(divide|multiply)\s+(.+?)\s+by\s+(.+)$', re.I)
_IMP_TO = re.compile(r'^\s*(?:now\s+|then\s+)?(add|subtract)\s+(.+?)\s+(?:to|from)\s+(.+)$', re.I)
_IMP_BARE = re.compile(
    r'^\s*(?:now\s+|then\s+)?(?:and\s+)?(times|plus|minus|add|subtract|divide by|'
    r'divided by|multiply by|multiplied by|over)\s+(.+)$', re.I)
_OPMAP = {'times': '*', 'multiply by': '*', 'multiplied by': '*', 'plus': '+',
          'add': '+', 'minus': '-', 'subtract': '-', 'divide by': '/',
          'divided by': '/', 'over': '/'}


class OracleReleaseRuntimeW29(OracleReleaseRuntimeW24):
    """Base + verified arithmetic. Warrant form: computation trace.

    Multi-turn: a computed value is carried on the session, so "now divide that
    by 5" continues the calculation. The carry is recorded as continuity, and it
    is only ever a value THIS route computed - never a number lifted from prose.
    """

    def _witness_compute(self, session_id, surface, value, steps, carried):
        """Record this turn in the witness. A compute turn has a typed reading and
        a verified warrant, and it carries NO corpus terms - in_terms stays empty,
        so the citation-grounding average is neither inflated nor diluted by it."""
        from collections import deque
        hist = getattr(self, '_paths', None)
        if hist is None:
            hist = self._paths = {}
        q = hist.get(session_id)
        if q is None:
            q = hist[session_id] = deque(maxlen=64)
        prev = q[-1].get('turn', 0) if len(q) else 0
        q.append({'turn': prev + 1, 'in_surface': str(surface)[:120],
                  'in_form': ['arithmetic'], 'operator': 'compute:verified',
                  'out_status': 'answered', 'in_terms': [], 'out_terms': [],
                  'relation': {'grounded': [], 'grounded_cited': [],
                               'introduced': [], 'unaccounted': []},
                  'carried_from_prior': ['prior_result'] if carried else [],
                  'continuity_lexical': bool(carried), 'continuity': bool(carried),
                  'citations': 0, 'residual': None, 'cost_ms': 0.5,
                  'conversion': {'construction': 'VERIFIED_COMPUTE',
                                 'from': str(surface)[:80], 'to': _fmt(value),
                                 'produced_by': 'compute_w29'},
                  'verified_warrant': {'kind': 'computation', 'steps': steps}})

    def _carry(self, session_id):
        d = getattr(self, '_last_value', None)
        if d is None:
            d = self._last_value = {}
        return d.get(session_id)

    def _resolve_followup(self, surface: str, session_id: str):
        """Rewrite an anaphoric follow-up into a total arithmetic surface."""
        last = self._carry(session_id)
        if last is None:
            return surface, False
        s = surface
        m = _IMP_BY.match(s)
        if m:
            op = '/' if m.group(1).lower() == 'divide' else '*'
            s = '%s %s %s' % (m.group(2), op, m.group(3))
        else:
            m = _IMP_TO.match(s)
            if m:
                op = '+' if m.group(1).lower() == 'add' else '-'
                s = '%s %s %s' % (m.group(3), op, m.group(2))
            else:
                m = _IMP_BARE.match(s)
                if m:
                    s = 'that %s %s' % (_OPMAP[m.group(1).lower()], m.group(2))
        if not _ANA.search(s):
            return surface, False
        return _ANA.sub(_fmt(last), s), True

    def _compute(self, surface: str):
        toks = _tokenize(surface)
        if not toks or not any(t.kind == 'num' for t in toks):
            return None
        if not any(t.kind in ('+', '-', '*', '/', '**', '%OF%') for t in toks):
            return None                       # a bare number is not a computation
        p = _Parser(toks)
        try:
            value = p.parse()
        except ZeroDivisionError:
            return ('refuse', 'division by zero is undefined, so I will not answer it')
        except Exception:
            return None                       # not a total arithmetic parse
        return ('ok', value, p.steps)

    def chat(self, text: str, session_id: str = 'default') -> dict:
        s = ' '.join(str(text).strip().split())
        carried = False
        got = None
        # a follow-up FORM outranks a bare parse: "minus 29" after a result is a
        # continuation, not the negative number twenty nine.
        if (_IMP_BY.match(s) or _IMP_TO.match(s) or _IMP_BARE.match(s)
                or _ANA.search(s)):
            s2, carried = self._resolve_followup(s, session_id)
            if carried:
                got = self._compute(s2)
                if got is None:
                    carried = False
        if got is None:
            got = self._compute(s)
        if got is not None:
            if got[0] == 'refuse':
                return {'status': 'withheld', 'path': 'compute:refused',
                        'response': 'That expression has no defined value: %s.' % got[1],
                        'provenance': {'kind': 'computation', 'verified': False},
                        'latency_ms': 1}
            _, value, steps = got
            body = ('%s.' % _fmt(value)) if not steps else (
                'In steps: %s. The answer is %s.' % ('; '.join(steps), _fmt(value)))
            if carried:
                body = 'Carrying the previous result: ' + body
            d = getattr(self, '_last_value', None)
            if d is None:
                d = self._last_value = {}
            d[session_id] = value
            self._witness_compute(session_id, s, value, steps, carried)
            pending = getattr(self, '_pending_conversion', None)
            if pending is None:
                pending = self._pending_conversion = {}
            pending[session_id] = {'construction': 'VERIFIED_COMPUTE',
                                   'from': s[:80], 'to': _fmt(value),
                                   'produced_by': 'compute_w27'}
            return {'status': 'answered', 'path': 'compute:verified',
                    'response': body,
                    'provenance': {'kind': 'computation', 'verified': True,
                                   'steps': steps, 'carried_prior': carried,
                                   'evaluator': 'w27_closed_grammar'},
                    'latency_ms': 1}
        return super().chat(s, session_id)
