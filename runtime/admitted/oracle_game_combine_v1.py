#!/usr/bin/env python3
"""ORACLE GAME COMBINATORS - operators that take games and return games.

Twelve categories with parameters is a large space. It is still a flat one: every
game it can build is one of twelve shapes wearing different numbers. The move that
makes it genuinely open is HIGHER ORDER operators, which take a game and give back
a different game, because then the space closes under its own operations.

Two of them, and they are chosen because both are real games people actually play
rather than formal curiosities:

    INVERT      the win condition is flipped. Get three in a row and you LOSE,
                which is a real game (misere noughts and crosses) with completely
                different play from the one it inverts. Applied to any of the
                twelve, not just to take-away where it was hand-written.

    COMPOUND    play game A, then game B, and whoever won more takes the match.
                "Tic tac toe then nim" is not in any catalogue, is not a
                parameter setting of anything, and is a perfectly well defined
                game. This is what combining categories means.

Both come with their own referees, built by composing the referees underneath
them, so a combined game is checked the same way a simple one is: the engine
plays, the referee replays, and the emitted program runs in a separate process.
A combination is only allowed out if all three agree about it.

The count matters less than the closure. Twelve categories give twelve games; with
INVERT that is twenty-four; with COMPOUND over ordered pairs it is 24 x 24 before
any parameter is chosen, and the parameters are still free. Nothing in that space
is stored.
"""

from __future__ import annotations

import re

from oracle_game_kernel_v1 import GameError, play

COMPOUND_BUDGET = 1200
from oracle_game_vocab_v1 import CATS

_FLIP = {'first': 'second', 'second': 'first', 'draw': 'draw',
         'solved': 'failed', 'failed': 'solved'}


# ── INVERT ───────────────────────────────────────────────────────────────────
def invert_build(inner_name, params):
    inner = CATS[inner_name]['build'](params)
    base_outcome = inner['outcome']

    def outcome(st):
        got = base_outcome(st)
        return _FLIP[got] if got is not None else None

    return dict(inner, outcome=outcome)


def invert_referee(inner_name, params, log):
    got = CATS[inner_name]['referee'](params, log)
    return _FLIP[got]


# ── COMPOUND ─────────────────────────────────────────────────────────────────
def compound_build(a_name, b_name, a_params, b_params):
    """Play A to a result, then B, then compare. One game, two halves."""
    ga = CATS[a_name]['build'](a_params)
    gb = CATS[b_name]['build'](b_params)

    def score_of(res):
        return {'first': 1, 'solved': 1, 'second': -1, 'failed': -1,
                'draw': 0}[res]

    # Every move is TAGGED with the half it belongs to, so the kernel's own move
    # log is already splittable by the referee. The first version kept a private
    # tagged log inside the state and handed the referee the kernel's untagged
    # one, which is why every compound died on unpacking.
    def init():
        return ('a', ga['init'](), None, 0)

    def moves(st):
        leg, inner = st[0], st[1]
        g = ga if leg == 'a' else gb
        legal = [(leg, m) for m in g['moves'](inner)]
        if not legal and leg == 'a':
            # the first half ran out of legal moves without declaring a result.
            # Returning nothing here makes the KERNEL call the whole compound a
            # draw and the second half never happens, which the referee then
            # rightly refuses. Hand back a marker so the transition still occurs.
            return [('a', None)]
        return legal

    def apply(st, tagged, t):
        leg, inner, first_res, count = st
        _tag, m = tagged
        if m is None:                       # the exhaustion marker from moves()
            return ('b', gb['init'](), ga['outcome'](inner) or 'draw', 0)
        g = ga if leg == 'a' else gb
        inner2 = g['apply'](inner, m, count)          # the INNER half's own turn
        done = g['outcome'](inner2)
        if done is not None and leg == 'a':
            return ('b', gb['init'](), done, 0)
        return (leg, inner2, first_res, count + 1)

    def outcome(st):
        leg, inner, first_res, _count = st
        if leg == 'a':
            return None
        done = gb['outcome'](inner)
        if done is None:
            return None
        total = score_of(first_res) + score_of(done)
        return 'first' if total > 0 else 'second' if total < 0 else 'draw'

    def policy(st, legal, t):
        return legal[0] if st[3] % 2 == 0 else legal[-1]

    return {'init': init, 'moves': moves, 'apply': apply, 'outcome': outcome,
            'policy': policy}


def compound_referee(a_name, b_name, a_params, b_params, log):
    """Split the tagged log and hand each half to the referee that owns it."""
    a_log = [m for leg, m in log if leg == 'a' and m is not None]
    b_log = [m for leg, m in log if leg == 'b' and m is not None]
    if not a_log or not b_log:
        raise GameError('referee: one half of the compound never happened')
    ra = CATS[a_name]['referee'](a_params, a_log)
    rb = CATS[b_name]['referee'](b_params, b_log)
    sc = {'first': 1, 'solved': 1, 'second': -1, 'failed': -1, 'draw': 0}
    total = sc[ra] + sc[rb]
    return 'first' if total > 0 else 'second' if total < 0 else 'draw'


# ── routing the combinations ─────────────────────────────────────────────────
_INVERT_CUE = re.compile(
    r'\b(?:misere|mis[eè]re)\b|you lose|makes you lose|loses instead'
    r'|whoever .{0,24}loses|reverse(?:d)? (?:rules|win)|inverted'
    r'|the loser wins|last one loses', re.I)
_COMPOUND_CUE = re.compile(
    r'\bthen\b|\bfollowed by\b|\band then\b|\bboth\b.{0,20}\bgames?\b'
    r'|combin(?:e|ed|ation) of', re.I)


def find_categories(surface):
    """Every category the surface names, in the order it names them."""
    hits = []
    for name, c in CATS.items():
        for rx in c['cues']:
            m = rx.search(surface)
            if m:
                hits.append((m.start(), name))
                break
    hits.sort()
    out = []
    for _pos, name in hits:
        if name not in out:
            out.append(name)
    return out


def parse_combination(surface):
    """(kind, payload) or None if this is not a combination request.

    kind is 'invert' or 'compound'. Raises GameError when the request clearly
    wants a combination but the pieces do not resolve, so it can decline with a
    reason rather than quietly build one half.
    """
    names = find_categories(surface)
    wants_compound = bool(_COMPOUND_CUE.search(surface))
    wants_invert = bool(_INVERT_CUE.search(surface))

    if wants_compound:
        real = [n for n in names if n != 'misere_take_away']
        if len(real) < 2:
            raise GameError('that asks for two games joined together and I can '
                            'only find one of them in it')
        a, b = real[0], real[1]
        pa = CATS[a]['params'](surface)
        pb = CATS[b]['params'](surface)
        return 'compound', (a, b, pa, pb)

    if wants_invert and names:
        base = [n for n in names if n != 'misere_take_away']
        if not base:
            return None                       # plain misere nim, already a category
        n = base[0]
        return 'invert', (n, CATS[n]['params'](surface))
    return None


def describe(kind, payload):
    if kind == 'invert':
        n, p = payload
        return ('%s, with the win condition inverted: doing the thing that '
                'normally wins LOSES' % CATS[n]['describe'](p))
    a, b, pa, pb = payload
    return ('two games in one match: first %s, then %s, and whoever wins more '
            'takes it' % (CATS[a]['describe'](pa), CATS[b]['describe'](pb)))


def build_and_referee(kind, payload):
    if kind == 'invert':
        n, p = payload
        return (invert_build(n, p),
                lambda _params, log: invert_referee(n, p, log), p)
    a, b, pa, pb = payload
    return (compound_build(a, b, pa, pb),
            lambda _params, log: compound_referee(a, b, pa, pb, log),
            {'a': a, 'b': b})
