#!/usr/bin/env python3
"""ORACLE GAME KERNEL - five primitives, and a referee that has to agree.

The machine had games in a catalogue. Asked for one it did not have it returned a
different game and called it verified, which is the failure this whole project
exists to prevent, and no amount of adding entries fixes it: a catalogue that
always finds a nearest match cannot say "I do not have that", and a catalogue can
never hold the game nobody has asked for yet.

So games stop being entries and become COMPOSITIONS, the same move the operators
made. A game is five things, and nearly every small game is exactly these:

    INIT      the opening position
    MOVES     what is legal from a position
    APPLY     position and move to a new position
    OUTCOME   won / lost / drawn / still going
    POLICY    how a player chooses, so the thing can play itself to a result

A vocabulary of state shapes, move rules and win conditions composes into far more
games than anyone writes down. Nim is piles plus take-k plus last-to-move.
Connect four is a grid plus place-marker plus four-in-a-line. Neither needs to be
stored, and changing "last to move wins" to "last to move loses" gives misere nim
for free, which is a different game that nobody had to author.

VERIFICATION, which is the part that makes any of it count. Playing a game proves
nothing on its own: a broken game plays happily to a wrong answer. So every
generated game is checked the way every operator is checked, by a second method
that shares no code with the first:

    the ENGINE plays the game and records the move log
    an independent REFEREE replays that log from the rules alone and must arrive
        at the same outcome
    plus invariants: every move was legal when it was made, the game terminated
        inside its move budget, and the outcome is one of the declared ones

Disagreement means the game is WITHHELD. Not shipped with a caveat, withheld, the
same as an operator whose two implementations disagree.

No neural network, no LM call. Pure python.
"""

from __future__ import annotations

MAX_MOVES = 400


class GameError(Exception):
    """The composition did not produce a playable game. Named, never silent."""


class NonTerminating(GameError):
    """It ran past the move budget, which is a defect and not a draw."""


class IllegalMove(GameError):
    """The policy chose something the rules did not permit."""


class RefereeDisagrees(GameError):
    """Engine and referee reached different outcomes. The game is not trustworthy."""


OUTCOMES = ('first', 'second', 'draw', 'solved', 'failed')


def play(game, max_moves=MAX_MOVES):
    """Run a game to a terminal state. Returns (outcome, move_log, turns).

    `game` is a dict of callables: init, moves, apply, outcome, policy. Nothing in
    here knows what any particular game IS.
    """
    state = game['init']()
    log = []
    for turn in range(max_moves):
        done = game['outcome'](state)
        if done is not None:
            return done, log, turn
        legal = list(game['moves'](state))
        if not legal:
            return 'draw', log, turn
        move = game['policy'](state, legal, turn)
        if move not in legal:
            raise IllegalMove('policy chose %r, legal were %r' % (move, legal[:6]))
        log.append(move)
        state = game['apply'](state, move, turn)
    raise NonTerminating('past %d moves' % max_moves)


def verify(game, referee, params):
    """Play, then have an independent referee replay the log. Both must agree.

    The referee is written from the rules and never sees the engine's state; it
    receives only the move log. Two implementations of the same rules, which is
    the same discipline the operators use, applied to a thing that unfolds in time.
    """
    outcome, log, turns = play(game)
    if outcome not in OUTCOMES:
        raise GameError('outcome %r is not one of the declared ones' % outcome)
    second = referee(params, log)
    if second != outcome:
        raise RefereeDisagrees('engine said %r, referee said %r' % (outcome, second))
    return {'outcome': outcome, 'moves': len(log), 'turns': turns, 'log': log}


# ── policies, which are part of the kernel rather than of any game ────────────
def first_legal(state, legal, turn):
    return legal[0]


def alternating(state, legal, turn):
    """Take from opposite ends so self-play does not collapse to one line."""
    return legal[0] if turn % 2 == 0 else legal[-1]


def middle(state, legal, turn):
    return legal[len(legal) // 2]
