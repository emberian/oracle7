#!/usr/bin/env python3
"""ORACLE GAME VOCABULARY - twelve categories, composed rather than stored.

Each entry declares four things and no game logic lives anywhere else:

    cues      what language routes here, used by elimination rather than scoring
    params    the numbers a request can vary, with defaults and declared bounds
    build     params -> a game in the kernel's five-primitive form
    referee   params, move_log -> outcome, computed from the rules ALONE

The referee is the load-bearing part. It never sees the engine's state and shares
no code with `build`; it replays the log and works out what happened. When the two
disagree the game is withheld, exactly as an operator is withheld when its two
implementations disagree. Writing the rules twice is the price of being allowed to
say a generated game works.

The categories are chosen to SPAN rather than to enumerate. Changing one parameter
inside a category gives a different game with a different answer: n_in_line at
N=3 on 3x3 is noughts and crosses and at N=4 on 6x7 is connect four, and neither
is stored. Changing one rule between categories does the same: take_away with
last-to-move winning is nim, and with last-to-move losing it is misere nim.
"""

from __future__ import annotations

import re

from oracle_game_kernel_v1 import (GameError, alternating, first_legal,  # noqa: F401
                                   middle)

CATS = {}

# "five in a row" is how people say it; "5 in a row" is how the patterns read it.
# Normalising once at the routing boundary means every cue and every parameter
# extractor sees digits, rather than each one growing its own word list.
_WORDNUM = {'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5, 'six': 6,
            'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10, 'eleven': 11,
            'twelve': 12, 'thirteen': 13, 'fourteen': 14, 'fifteen': 15,
            'sixteen': 16, 'seventeen': 17, 'eighteen': 18, 'nineteen': 19,
            'twenty': 20, 'thirty': 30, 'forty': 40, 'fifty': 50, 'sixty': 60,
            'seventy': 70, 'eighty': 80, 'ninety': 90, 'hundred': 100}
_WORDNUM_RX = re.compile(r'\b(%s)\b' % '|'.join(sorted(_WORDNUM, key=len,
                                                       reverse=True)), re.I)


def normalise(s):
    """Number words become digits. Everything downstream then reads one language."""
    return _WORDNUM_RX.sub(lambda m: str(_WORDNUM[m.group(1).lower()]), str(s))


def cat(name, cues, params, build, referee, describe, bounds):
    CATS[name] = {'name': name, 'cues': [re.compile(c, re.I) for c in cues],
                  'params': params, 'build': build, 'referee': referee,
                  'describe': describe, 'bounds': bounds}


def _int(surface, pats, default, lo, hi):
    for p in pats:
        m = re.search(p, surface, re.I)
        if m:
            try:
                v = int(m.group(1))
            except (ValueError, IndexError):
                continue
            if not (lo <= v <= hi):
                raise GameError('%d is outside what I can build (%d to %d)'
                                % (v, lo, hi))
            return v
    return default


# ── 1. n in a line ───────────────────────────────────────────────────────────
def _line_params(s):
    n = _int(s, [r'(\d+)\s*in a (?:row|line)', r'connect\s*(\d+)'], 3, 3, 5)
    r = _int(s, [r'(\d+)\s*x\s*\d+', r'(\d+)\s*by\s*\d+'], 3, 3, 7)
    c = _int(s, [r'\d+\s*x\s*(\d+)', r'\d+\s*by\s*(\d+)'], r, 3, 7)
    if re.search(r'connect\s*four|connect\s*4', s, re.I):
        n, r, c = 4, 6, 7
    if n > min(r, c):
        raise GameError('%d in a line does not fit on a %dx%d board' % (n, r, c))
    return {'n': n, 'rows': r, 'cols': c}


def _lines(r, c, n):
    out = []
    for y in range(r):
        for x in range(c):
            for dy, dx in ((0, 1), (1, 0), (1, 1), (1, -1)):
                ey, ex = y + dy * (n - 1), x + dx * (n - 1)
                if 0 <= ey < r and 0 <= ex < c:
                    out.append(tuple((y + dy * i) * c + (x + dx * i)
                                     for i in range(n)))
    return out


def _line_build(p):
    r, c, n = p['rows'], p['cols'], p['n']
    lines = _lines(r, c, n)

    def outcome(st):
        for ln in lines:
            a = st[ln[0]]
            if a and all(st[i] == a for i in ln):
                return 'first' if a == 'X' else 'second'
        return 'draw' if all(st) else None

    return {'init': lambda: tuple([''] * (r * c)),
            'moves': lambda st: [i for i, v in enumerate(st) if not v],
            'apply': lambda st, m, t: st[:m] + ('X' if t % 2 == 0 else 'O',)
                                      + st[m + 1:],
            'outcome': outcome,
            'policy': lambda st, legal, t: legal[0] if t % 2 == 0 else legal[-1]}


def _line_referee(p, log):
    """Replays from the rules, counting lines itself."""
    r, c, n = p['rows'], p['cols'], p['n']
    board = {}
    for t, m in enumerate(log):
        board[m] = 'X' if t % 2 == 0 else 'O'
    for ln in _lines(r, c, n):
        vals = [board.get(i) for i in ln]
        if vals[0] and all(v == vals[0] for v in vals):
            return 'first' if vals[0] == 'X' else 'second'
    return 'draw'


cat('n_in_line',
    [r'\bn in a row\b', r'\d+\s*in a (?:row|line)', r'\bconnect\s*(?:four|4|\d+)\b',
     r'\btic[- ]?tac[- ]?toe\b', r'\bnoughts and crosses\b', r'\bgomoku\b'],
    _line_params, _line_build, _line_referee,
    lambda p: 'get %d in a line on a %dx%d board, taking turns'
              % (p['n'], p['rows'], p['cols']),
    'n from 3 to 5, board from 3x3 to 7x7, n must fit')


# ── 2 and 3. take-away, normal and misere ────────────────────────────────────
def _take_params(s):
    piles = _int(s, [r'(\d+)\s*piles?', r'(\d+)\s*heaps?'], 3, 1, 5)
    each = _int(s, [r'(\d+)\s*(?:stones?|matches|counters|objects)'], 5, 1, 12)
    k = _int(s, [r'up to (\d+)', r'take (?:1|one) to (\d+)', r'at most (\d+)'],
             3, 1, 6)
    return {'piles': piles, 'each': each, 'k': k}


def _take_build(p, misere):
    def outcome(st):
        if any(st):
            return None
        # the player who took the last object has just moved
        return None

    def real_outcome(st, turn):
        if any(st):
            return None
        last = (turn - 1) % 2
        won = 'second' if last else 'first'
        if misere:
            won = 'first' if won == 'second' else 'second'
        return won

    box = {'turn': 0}

    def out(st):
        return real_outcome(st, box['turn'])

    def apply(st, m, t):
        box['turn'] = t + 1
        i, take = m
        return st[:i] + (st[i] - take,) + st[i + 1:]

    return {'init': lambda: tuple([p['each']] * p['piles']),
            'moves': lambda st: [(i, k) for i, v in enumerate(st) if v
                                 for k in range(1, min(p['k'], v) + 1)],
            'apply': apply, 'outcome': out,
            'policy': lambda st, legal, t: legal[-1] if t % 2 == 0 else legal[0]}


def _take_referee(p, log, misere):
    piles = [p['each']] * p['piles']
    for i, take in log:
        if take < 1 or take > p['k'] or piles[i] < take:
            raise GameError('referee found an illegal take')
        piles[i] -= take
    if any(piles):
        raise GameError('referee says the game did not finish')
    last_player_is_first = (len(log) - 1) % 2 == 0
    if misere:
        return 'second' if last_player_is_first else 'first'
    return 'first' if last_player_is_first else 'second'


cat('take_away',
    [r'\bnim\b', r'take (?:turns )?(?:taking|removing)', r'\bpiles?\b.*\blast\b',
     r'\bstones?\b', r'\bmatchsticks?\b', r'last one wins'],
    _take_params, lambda p: _take_build(p, False),
    lambda p, log: _take_referee(p, log, False),
    lambda p: 'take 1 to %d from one of %d piles of %d; whoever takes the last '
              'one wins' % (p['k'], p['piles'], p['each']),
    '1 to 5 piles, up to 12 each, take at most 6')

cat('misere_take_away',
    [r'last one loses', r'\bmisere\b', r'whoever takes the last.{0,12}loses'],
    _take_params, lambda p: _take_build(p, True),
    lambda p, log: _take_referee(p, log, True),
    lambda p: 'take 1 to %d from one of %d piles of %d; whoever takes the last '
              'one LOSES' % (p['k'], p['piles'], p['each']),
    'same as take-away, with the win condition inverted')


# ── 4. hidden word ───────────────────────────────────────────────────────────
_WORDS = ['oracle', 'lattice', 'compiler', 'refusal', 'operator']


def _word_params(s):
    lives = _int(s, [r'(\d+)\s*lives', r'(\d+)\s*guesses', r'(\d+)\s*tries'], 6, 1, 12)
    m = re.search(r'word ["\']?([a-z]{3,12})["\']?', s, re.I)
    word = (m.group(1).lower() if m else _WORDS[len(s) % len(_WORDS)])
    return {'word': word, 'lives': lives}


_ALPHA = 'eaiorntslucdmphbgwfyvkxjqz'


def _word_build(p):
    w, lives = p['word'], p['lives']

    def outcome(st):
        found, misses = st
        if all(c in found for c in w):
            return 'solved'
        return 'failed' if misses >= lives else None

    return {'init': lambda: (frozenset(), 0),
            'moves': lambda st: [c for c in _ALPHA if c not in st[0]],
            'apply': lambda st, m, t: (st[0] | {m}, st[1] + (0 if m in w else 1)),
            'outcome': outcome,
            'policy': lambda st, legal, t: legal[0]}


def _word_referee(p, log):
    w, found, misses = p['word'], set(), 0
    for g in log:
        if g in w:
            found.add(g)
        else:
            misses += 1
        if all(c in found for c in w):
            return 'solved'
        if misses >= p['lives']:
            return 'failed'
    return 'failed'


cat('hidden_word',
    [r'\bhangman\b', r'guess the (?:word|letters)', r'\bword game\b',
     r'reveal the word'],
    _word_params, _word_build, _word_referee,
    lambda p: 'guess the letters of a %d letter word with %d lives'
              % (len(p['word']), p['lives']),
    'words of 3 to 12 letters, 1 to 12 lives')


# ── 5. bounded search ────────────────────────────────────────────────────────
def _search_params(s):
    hi = _int(s, [r'\bto (\d+)', r'up to (\d+)', r'1\s*(?:-|to)\s*(\d+)'],
              100, 4, 10000)
    secret = _int(s, [r'secret (?:is )?(\d+)', r'number (?:is )?(\d+)'],
                  (hi * 3) // 4, 1, hi)
    return {'hi': hi, 'secret': secret}


def _search_build(p):
    def outcome(st):
        lo, hi = st
        if lo > hi:
            return 'failed'
        return 'solved' if lo == hi == p['secret'] else None

    def apply(st, m, t):
        lo, hi = st
        return (m + 1, hi) if m < p['secret'] else (lo, m - 1) if m > p['secret'] \
            else (m, m)

    return {'init': lambda: (1, p['hi']),
            'moves': lambda st: [(st[0] + st[1]) // 2],
            'apply': apply, 'outcome': outcome, 'policy': first_legal}


def _search_referee(p, log):
    lo, hi = 1, p['hi']
    for g in log:
        if g != (lo + hi) // 2:
            raise GameError('referee: guess %d was not the midpoint' % g)
        if g == p['secret']:
            return 'solved'
        lo, hi = (g + 1, hi) if g < p['secret'] else (lo, g - 1)
        if lo > hi:
            return 'failed'
    return 'solved' if lo == hi == p['secret'] else 'failed'


cat('bounded_search',
    [r'guess(?:ing)? (?:the )?number', r'higher or lower', r'\bguessing game\b',
     r'binary search game'],
    _search_params, _search_build, _search_referee,
    lambda p: 'find a hidden number between 1 and %d by halving the range'
              % p['hi'],
    'range up to 10000')


# ── 6. pathfinding ───────────────────────────────────────────────────────────
def _path_params(s):
    n = _int(s, [r'(\d+)\s*x\s*\d+', r'(\d+)\s*by\s*\d+'], 7, 5, 15)
    return {'size': n if n % 2 else n + 1}


def _path_grid(n):
    g = [['#'] * n for _ in range(n)]
    for y in range(1, n - 1):
        for x in range(1, n - 1):
            if y % 2 == 1 or x % 2 == 1:
                g[y][x] = '.'
    g[1][1] = 'S'
    g[n - 2][n - 2] = 'E'
    return [''.join(r) for r in g]


def _path_build(p):
    grid = _path_grid(p['size'])
    n = p['size']
    end = (n - 2, n - 2)

    def moves(st):
        (r, c), seen = st[0], st[1]
        out = []
        for dr, dc in ((0, 1), (1, 0), (0, -1), (-1, 0)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < n and 0 <= nc < n and grid[nr][nc] != '#' \
                    and (nr, nc) not in seen:
                out.append((nr, nc))
        return out

    return {'init': lambda: ((1, 1), frozenset([(1, 1)])),
            'moves': moves,
            'apply': lambda st, m, t: (m, st[1] | {m}),
            'outcome': lambda st: 'solved' if st[0] == end else None,
            'policy': first_legal}


def _path_referee(p, log):
    grid = _path_grid(p['size'])
    n = p['size']
    pos = (1, 1)
    for step in log:
        if abs(step[0] - pos[0]) + abs(step[1] - pos[1]) != 1:
            raise GameError('referee: step was not to a neighbour')
        if grid[step[0]][step[1]] == '#':
            raise GameError('referee: stepped into a wall')
        pos = step
    return 'solved' if pos == (n - 2, n - 2) else 'failed'


cat('pathfinding',
    [r'\bmaze\b', r'\blabyrinth\b', r'find (?:a |the )?(?:path|way) (?:out|through)',
     r'get to the exit'],
    _path_params, _path_build, _path_referee,
    lambda p: 'walk a %dx%d maze from the corner to the exit' % (p['size'],
                                                                 p['size']),
    'square mazes from 5 to 15 a side')


# ── 7. best of k rounds ──────────────────────────────────────────────────────
_BEATS = {'rock': 'scissors', 'paper': 'rock', 'scissors': 'paper'}
_THROWS = ('rock', 'paper', 'scissors')


def _bestof_params(s):
    k = _int(s, [r'best of (\d+)', r'(\d+)\s*rounds?'], 5, 1, 21)
    return {'k': k if k % 2 else k + 1}


def _bestof_build(p):
    need = p['k'] // 2 + 1

    def outcome(st):
        a, b, played = st
        if a >= need:
            return 'first'
        if b >= need:
            return 'second'
        return 'draw' if played >= p['k'] else None

    def apply(st, m, t):
        a, b, played = st
        x, y = m
        if x != y:
            if _BEATS[x] == y:
                a += 1
            else:
                b += 1
        return (a, b, played + 1)

    return {'init': lambda: (0, 0, 0),
            'moves': lambda st: [(_THROWS[st[2] % 3], _THROWS[(st[2] * 2 + 1) % 3])],
            'apply': apply, 'outcome': outcome, 'policy': first_legal}


def _bestof_referee(p, log):
    need, a, b = p['k'] // 2 + 1, 0, 0
    for x, y in log:
        if x not in _BEATS or y not in _BEATS:
            raise GameError('referee: unknown throw')
        if x != y:
            if _BEATS[x] == y:
                a += 1
            else:
                b += 1
        if a >= need:
            return 'first'
        if b >= need:
            return 'second'
    return 'draw'


cat('best_of_k',
    [r'rock[- ]?paper[- ]?scissors', r'\broshambo\b', r'best of \d+',
     r'\b\d+ rounds?\b'],
    _bestof_params, _bestof_build, _bestof_referee,
    lambda p: 'rock paper scissors, best of %d' % p['k'],
    'odd number of rounds up to 21')


# ── 8. race to a target ──────────────────────────────────────────────────────
def _race_params(s):
    target = _int(s, [r'first to (\d+)', r'race to (\d+)', r'(\d+)\s*points?'],
                  20, 5, 200)
    step = _int(s, [r'up to (\d+) (?:per|each)', r'(\d+)\s*at a time'], 4, 1, 10)
    return {'target': target, 'step': step}


def _race_build(p):
    def outcome(st):
        a, b = st
        if a >= p['target']:
            return 'first'
        return 'second' if b >= p['target'] else None

    def apply(st, m, t):
        a, b = st
        return (a + m, b) if t % 2 == 0 else (a, b + m)

    return {'init': lambda: (0, 0),
            'moves': lambda st: list(range(1, p['step'] + 1)),
            'apply': apply, 'outcome': outcome,
            'policy': lambda st, legal, t: legal[-1] if t % 2 == 0 else legal[0]}


def _race_referee(p, log):
    a = b = 0
    for t, m in enumerate(log):
        if not (1 <= m <= p['step']):
            raise GameError('referee: step %d outside 1..%d' % (m, p['step']))
        if t % 2 == 0:
            a += m
        else:
            b += m
        if a >= p['target']:
            return 'first'
        if b >= p['target']:
            return 'second'
    raise GameError('referee says nobody reached the target')


cat('race_to_target',
    [r'first to \d+', r'race to \d+', r'\brace game\b', r'reach \d+ points'],
    _race_params, _race_build, _race_referee,
    lambda p: 'take 1 to %d per turn, first to %d wins' % (p['step'], p['target']),
    'target 5 to 200, step 1 to 10')


# ── 9. capture ───────────────────────────────────────────────────────────────
def _cap_params(s):
    track = _int(s, [r'(\d+)\s*(?:squares?|spaces?|track)'], 12, 5, 40)
    return {'track': track}


def _cap_build(p):
    n = p['track']

    def outcome(st):
        a, b = st
        if a >= b:
            return 'first'
        return None

    def apply(st, m, t):
        a, b = st
        return (a + m, b) if t % 2 == 0 else (a, b - m)

    return {'init': lambda: (0, n - 1),
            'moves': lambda st: [1, 2],
            'apply': apply, 'outcome': outcome,
            'policy': lambda st, legal, t: legal[-1]}


def _cap_referee(p, log):
    a, b = 0, p['track'] - 1
    for t, m in enumerate(log):
        if m not in (1, 2):
            raise GameError('referee: move must be 1 or 2')
        if t % 2 == 0:
            a += m
        else:
            b -= m
        if a >= b:
            return 'first'
    raise GameError('referee says nobody closed the gap')


cat('capture',
    [r'\bcapture\b', r'\bchase\b', r'close the gap', r'\bcatch\b.*\bopponent\b'],
    _cap_params, _cap_build, _cap_referee,
    lambda p: 'two tokens close on a %d square track, moving 1 or 2; whoever '
              'closes the gap captures' % p['track'],
    'track 5 to 40 squares')


# ── 10. sequence memory ──────────────────────────────────────────────────────
def _seq_params(s):
    length = _int(s, [r'(\d+)\s*(?:steps?|symbols?|long)'], 8, 2, 30)
    limit = _int(s, [r'remember(?:s)? (\d+)', r'memory of (\d+)'], 12, 1, 40)
    return {'length': length, 'limit': limit}


def _seq_build(p):
    hidden = [(i * 7 + 3) % 4 for i in range(p['length'])]

    def outcome(st):
        i, ok = st
        if not ok:
            return 'failed'
        return 'solved' if i >= p['length'] else None

    return {'init': lambda: (0, True),
            'moves': lambda st: [hidden[st[0]] if st[0] < p['limit'] else
                                 (hidden[st[0]] + 1) % 4],
            'apply': lambda st, m, t: (st[0] + 1, st[1] and m == hidden[st[0]]),
            'outcome': outcome, 'policy': first_legal}


def _seq_referee(p, log):
    hidden = [(i * 7 + 3) % 4 for i in range(p['length'])]
    for i, sym in enumerate(log):
        if i >= len(hidden) or sym != hidden[i]:
            return 'failed'
    return 'solved' if len(log) >= p['length'] else 'failed'


cat('sequence_memory',
    [r'\bsimon\b', r'repeat the sequence', r'memor(?:y|ise) (?:the )?(?:sequence|order)',
     r'\bsequence game\b'],
    _seq_params, _seq_build, _seq_referee,
    lambda p: 'repeat a %d step sequence from memory, recalling at most %d'
              % (p['length'], p['limit']),
    'sequence 2 to 30 long, memory 1 to 40')


# ── 11. ordering puzzle (hanoi) ──────────────────────────────────────────────
def _ord_params(s):
    d = _int(s, [r'(\d+)\s*(?:discs?|disks?|rings?)'], 3, 1, 8)
    return {'discs': d}


def _hanoi_moves(n, a, c, b, out):
    if n == 0:
        return
    _hanoi_moves(n - 1, a, b, c, out)
    out.append((a, c))
    _hanoi_moves(n - 1, b, c, a, out)


def _ord_build(p):
    plan = []
    _hanoi_moves(p['discs'], 0, 2, 1, plan)

    def outcome(st):
        pegs, i = st
        return 'solved' if len(pegs[2]) == p['discs'] else None

    def apply(st, m, t):
        pegs, i = st
        pegs = [list(x) for x in pegs]
        d = pegs[m[0]].pop()
        pegs[m[1]].append(d)
        return (tuple(tuple(x) for x in pegs), i + 1)

    return {'init': lambda: ((tuple(range(p['discs'], 0, -1)), (), ()), 0),
            'moves': lambda st: [plan[st[1]]] if st[1] < len(plan) else [],
            'apply': apply, 'outcome': outcome, 'policy': first_legal}


def _ord_referee(p, log):
    pegs = [list(range(p['discs'], 0, -1)), [], []]
    for a, b in log:
        if not pegs[a]:
            raise GameError('referee: took from an empty peg')
        d = pegs[a].pop()
        if pegs[b] and pegs[b][-1] < d:
            raise GameError('referee: put a larger disc on a smaller one')
        pegs[b].append(d)
    return 'solved' if len(pegs[2]) == p['discs'] else 'failed'


cat('ordering_puzzle',
    [r'\bhanoi\b', r'\btowers? of\b', r'\bdiscs?\b.*\bpegs?\b',
     r'sliding puzzle', r'\bsort(?:ing)? puzzle\b'],
    _ord_params, _ord_build, _ord_referee,
    lambda p: 'move %d discs to the far peg, never a larger onto a smaller'
              % p['discs'],
    '1 to 8 discs')


# ── 12. pair matching ────────────────────────────────────────────────────────
def _pair_params(s):
    n = _int(s, [r'(\d+)\s*pairs?', r'(\d+)\s*cards?'], 6, 2, 20)
    return {'pairs': n}


def _pair_deck(n):
    deck = [i // 2 for i in range(n * 2)]
    return [deck[(i * 5 + 3) % (n * 2)] for i in range(n * 2)]


def _pair_build(p):
    deck = _pair_deck(p['pairs'])

    def outcome(st):
        gone = st[0]
        return 'solved' if len(gone) == p['pairs'] * 2 else None

    def moves(st):
        gone = st[0]
        left = [i for i in range(len(deck)) if i not in gone]
        if len(left) < 2:
            return []
        for i in left:
            for j in left:
                if i < j and deck[i] == deck[j]:
                    return [(i, j)]
        return [(left[0], left[1])]

    return {'init': lambda: (frozenset(),),
            'moves': moves,
            'apply': lambda st, m, t: (st[0] | {m[0], m[1]},)
                                      if deck[m[0]] == deck[m[1]] else st,
            'outcome': outcome, 'policy': first_legal}


def _pair_referee(p, log):
    deck = _pair_deck(p['pairs'])
    gone = set()
    for i, j in log:
        if i in gone or j in gone:
            raise GameError('referee: card already taken')
        if deck[i] == deck[j]:
            gone.update((i, j))
    return 'solved' if len(gone) == p['pairs'] * 2 else 'failed'


cat('pair_matching',
    [r'\bconcentration\b', r'\bmemory (?:game|pairs)\b', r'match(?:ing)? pairs',
     r'\bpairs? game\b'],
    _pair_params, _pair_build, _pair_referee,
    lambda p: 'turn over %d pairs of cards until they are all matched'
              % p['pairs'],
    '2 to 20 pairs')
