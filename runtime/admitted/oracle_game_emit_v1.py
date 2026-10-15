#!/usr/bin/env python3
"""ORACLE GAME EMISSION - handing over the source, and a third way to be wrong.

The gate refused the game engine for a real reason: it could compose a game and
play it, but it could not give you the code. Asked "write the same thing in
javascript" after a composed game, it had nothing to hand over, and a catalogue
entry could still beat it because catalogue entries carry source.

So each category gets a REALIZATION: a template that, given the parameters the
router extracted, writes a standalone program for that particular game. The
template is the category's realization and the composition is still generated:
nothing anywhere stores "five in a row on a seven by seven board", the router
picks n_in_line with those numbers and this writes the program for it.

The reason this is worth more than a stored file is what it makes possible. There
are now THREE independent readings of every generated game:

    the ENGINE     composes it from primitives and plays it
    the REFEREE    replays the move log from the rules alone
    the PROGRAM    is written out, executed as a separate process, and prints
                   its own outcome

All three must agree before anything is handed over. Two agreeing could be two
implementations of one misunderstanding; three agreeing, where the third is a
process that shares no memory with the other two, is harder to arrange by
accident. When they disagree the game is withheld and the disagreement is named.

Emitted programs take no input and print one line, `outcome: X in N moves`, so
the check is mechanical rather than a human reading output.
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path


class EmitError(Exception):
    """No realization for that composition. Named, never a silent fallback."""


_LINE = '''\
WINS = %(wins)r
ROWS, COLS, N = %(rows)d, %(cols)d, %(n)d

def winner(board):
    for line in WINS:
        a = board[line[0]]
        if a and all(board[i] == a for i in line):
            return "first" if a == "X" else "second"
    return "draw" if all(board) else None

def play():
    board = [""] * (ROWS * COLS)
    for turn in range(ROWS * COLS):
        done = winner(board)
        if done:
            return done, turn
        empty = [i for i, v in enumerate(board) if not v]
        board[empty[0] if turn %% 2 == 0 else empty[-1]] = "X" if turn %% 2 == 0 else "O"
    return winner(board) or "draw", ROWS * COLS

result, moves = play()
print("outcome:", result, "in", moves, "moves")
'''

_TAKE = '''\
PILES, EACH, K, MISERE = %(piles)d, %(each)d, %(k)d, %(misere)r

def play():
    piles = [EACH] * PILES
    turn = 0
    while any(piles):
        legal = [(i, t) for i, v in enumerate(piles) for t in range(1, min(K, v) + 1)]
        i, take = legal[-1] if turn %% 2 == 0 else legal[0]
        piles[i] -= take
        turn += 1
    last_was_first = (turn - 1) %% 2 == 0
    won = "first" if last_was_first else "second"
    if MISERE:
        won = "second" if won == "first" else "first"
    return won, turn

result, moves = play()
print("outcome:", result, "in", moves, "moves")
'''

_WORD = '''\
WORD, LIVES = %(word)r, %(lives)d
ALPHA = "eaiorntslucdmphbgwfyvkxjqz"

def play():
    found, misses, moves = set(), 0, 0
    for g in ALPHA:
        moves += 1
        if g in WORD:
            found.add(g)
        else:
            misses += 1
        if all(c in found for c in WORD):
            return "solved", moves
        if misses >= LIVES:
            return "failed", moves
    return "failed", moves

result, moves = play()
print("outcome:", result, "in", moves, "moves")
'''

_SEARCH = '''\
HI, SECRET = %(hi)d, %(secret)d

def play():
    lo, hi, moves = 1, HI, 0
    while lo <= hi:
        mid = (lo + hi) // 2
        moves += 1
        if mid == SECRET:
            return "solved", moves
        lo, hi = (mid + 1, hi) if mid < SECRET else (lo, mid - 1)
    return "failed", moves

result, moves = play()
print("outcome:", result, "in", moves, "moves")
'''

_PATH = '''\
from collections import deque
N = %(size)d

def grid():
    g = [["#"] * N for _ in range(N)]
    for y in range(1, N - 1):
        for x in range(1, N - 1):
            if y %% 2 == 1 or x %% 2 == 1:
                g[y][x] = "."
    return ["".join(r) for r in g]

def play():
    g = grid()
    start, end = (1, 1), (N - 2, N - 2)
    pos, seen, moves = start, {start}, 0
    while pos != end:
        nxt = None
        for dr, dc in ((0, 1), (1, 0), (0, -1), (-1, 0)):
            r, c = pos[0] + dr, pos[1] + dc
            if 0 <= r < N and 0 <= c < N and g[r][c] != "#" and (r, c) not in seen:
                nxt = (r, c)
                break
        if nxt is None:
            return "failed", moves
        pos = nxt
        seen.add(pos)
        moves += 1
    return "solved", moves

result, moves = play()
print("outcome:", result, "in", moves, "moves")
'''

_BESTOF = '''\
K = %(k)d
BEATS = {"rock": "scissors", "paper": "rock", "scissors": "paper"}
THROWS = ("rock", "paper", "scissors")

def play():
    need, a, b, played = K // 2 + 1, 0, 0, 0
    while played < K:
        x, y = THROWS[played %% 3], THROWS[(played * 2 + 1) %% 3]
        if x != y:
            if BEATS[x] == y:
                a += 1
            else:
                b += 1
        played += 1
        if a >= need:
            return "first", played
        if b >= need:
            return "second", played
    return "draw", played

result, moves = play()
print("outcome:", result, "in", moves, "moves")
'''

_RACE = '''\
TARGET, STEP = %(target)d, %(step)d

def play():
    a = b = moves = 0
    while True:
        if moves %% 2 == 0:
            a += STEP
        else:
            b += 1
        moves += 1
        if a >= TARGET:
            return "first", moves
        if b >= TARGET:
            return "second", moves

result, moves = play()
print("outcome:", result, "in", moves, "moves")
'''

_CAP = '''\
TRACK = %(track)d

def play():
    a, b, moves = 0, TRACK - 1, 0
    while a < b:
        if moves %% 2 == 0:
            a += 2
        else:
            b -= 2
        moves += 1
    return "first", moves

result, moves = play()
print("outcome:", result, "in", moves, "moves")
'''

_SEQ = '''\
LENGTH, LIMIT = %(length)d, %(limit)d
HIDDEN = [(i * 7 + 3) %% 4 for i in range(LENGTH)]

def play():
    for i in range(LENGTH):
        said = HIDDEN[i] if i < LIMIT else (HIDDEN[i] + 1) %% 4
        if said != HIDDEN[i]:
            return "failed", i + 1
    return "solved", LENGTH

result, moves = play()
print("outcome:", result, "in", moves, "moves")
'''

_HANOI = '''\
DISCS = %(discs)d

def moves_for(n, a, c, b, out):
    if n == 0:
        return
    moves_for(n - 1, a, b, c, out)
    out.append((a, c))
    moves_for(n - 1, b, c, a, out)

def play():
    plan = []
    moves_for(DISCS, 0, 2, 1, plan)
    pegs = [list(range(DISCS, 0, -1)), [], []]
    for a, b in plan:
        d = pegs[a].pop()
        if pegs[b] and pegs[b][-1] < d:
            return "failed", len(plan)
        pegs[b].append(d)
    return ("solved" if len(pegs[2]) == DISCS else "failed"), len(plan)

result, moves = play()
print("outcome:", result, "in", moves, "moves")
'''

_PAIRS = '''\
PAIRS = %(pairs)d
DECK = [[i // 2 for i in range(PAIRS * 2)][(i * 5 + 3) %% (PAIRS * 2)]
        for i in range(PAIRS * 2)]

def play():
    gone, moves = set(), 0
    while len(gone) < PAIRS * 2:
        left = [i for i in range(len(DECK)) if i not in gone]
        pick = None
        for i in left:
            for j in left:
                if i < j and DECK[i] == DECK[j]:
                    pick = (i, j)
                    break
            if pick:
                break
        if not pick:
            return "failed", moves
        gone.update(pick)
        moves += 1
    return "solved", moves

result, moves = play()
print("outcome:", result, "in", moves, "moves")
'''


def _lines(rows, cols, n):
    out = []
    for y in range(rows):
        for x in range(cols):
            for dy, dx in ((0, 1), (1, 0), (1, 1), (1, -1)):
                ey, ex = y + dy * (n - 1), x + dx * (n - 1)
                if 0 <= ey < rows and 0 <= ex < cols:
                    out.append(tuple((y + dy * i) * cols + (x + dx * i)
                                     for i in range(n)))
    return out


_TEMPLATES = {
    'n_in_line': lambda p: _LINE % {'wins': _lines(p['rows'], p['cols'], p['n']),
                                    'rows': p['rows'], 'cols': p['cols'],
                                    'n': p['n']},
    'take_away': lambda p: _TAKE % dict(p, misere=False),
    'misere_take_away': lambda p: _TAKE % dict(p, misere=True),
    'hidden_word': lambda p: _WORD % p,
    'bounded_search': lambda p: _SEARCH % p,
    'pathfinding': lambda p: _PATH % p,
    'best_of_k': lambda p: _BESTOF % p,
    'race_to_target': lambda p: _RACE % p,
    'capture': lambda p: _CAP % p,
    'sequence_memory': lambda p: _SEQ % p,
    'ordering_puzzle': lambda p: _HANOI % p,
    'pair_matching': lambda p: _PAIRS % p,
}


def emit(category, params):
    """Standalone python for THIS composition. Raises if there is no realization."""
    t = _TEMPLATES.get(category)
    if t is None:
        raise EmitError('no realization for %s' % category)
    return t(params)


def run_emitted(source, timeout=25):
    """Execute it as a separate process and read back what it says happened."""
    with tempfile.TemporaryDirectory() as d:
        f = Path(d) / 'game.py'
        f.write_text(source, encoding='utf-8')
        try:
            p = subprocess.run([sys.executable, str(f)], capture_output=True,
                               text=True, timeout=timeout)
        except subprocess.TimeoutExpired:
            raise EmitError('the emitted program did not finish in %ds' % timeout)
    if p.returncode != 0:
        raise EmitError('the emitted program failed: %s'
                        % (p.stderr or '').strip()[:160])
    out = (p.stdout or '').strip().splitlines()
    line = out[-1] if out else ''
    if not line.startswith('outcome:'):
        raise EmitError('the emitted program printed %r' % line[:80])
    parts = line.split()
    return parts[1], int(parts[3])
