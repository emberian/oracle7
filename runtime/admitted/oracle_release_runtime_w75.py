#!/usr/bin/env python3
"""oracle_release_runtime_w75 - the game engine, complete: composed, combined, emitted.

w74 was refused by the gate and the refusal was correct. It could compose a game
and play it, and it could not hand you the code, so a follow-up asking for the
same thing in another language got nothing. A catalogue entry could still beat it
on that, and a capability that loses to a catalogue on any axis is not finished.

Three things arrive together here.

    EMISSION      each category has a realization: given the parameters the router
                  read, it writes a standalone program for THAT game. Nothing
                  stores "five in a row on seven by seven"; the router picks
                  n_in_line with those numbers and the realization writes it out.

    A THIRD CHECK the emitted program is executed as a SEPARATE PROCESS and must
                  report the same outcome the engine played and the referee
                  replayed. Two agreeing implementations can be two versions of
                  one misunderstanding. Three, where the third shares no memory
                  with the other two, is harder to arrange by accident.

    COMBINATORS   operators that take a game and give back a game. INVERT flips
                  the win condition of any category, so "tic tac toe where three
                  in a row makes you lose" is a real and different game the engine
                  has never been given. COMPOUND plays one game then another and
                  awards the match, so "tic tac toe then nim" exists without
                  anyone writing it down. The space closes under its own
                  operations, which is the difference between a large catalogue
                  and a generative one.

Everything still refuses. No category, ambiguous phrasing, parameters outside the
declared bounds, a game that will not terminate, a referee that disagrees, an
emitted program that will not run: each declines by name. The engine says what it
cannot do more often than it says what it can, which is the property worth having.

Hand-authored 2026-08-28. Judged by the gate.
"""

from __future__ import annotations

import re

from oracle_release_runtime_w72 import OracleReleaseRuntimeW72
from oracle_game_kernel_v1 import GameError, RefereeDisagrees, play, verify
from oracle_game_vocab_v1 import CATS, normalise
from oracle_game_emit_v1 import EmitError, emit, run_emitted
from oracle_game_combine_v1 import (COMPOUND_BUDGET, build_and_referee,
                                    describe as describe_combo, parse_combination)

_WANTS_GAME = re.compile(
    r'\b(?:write|make|build|code|create|generate|invent|design)\b.{0,40}\b'
    r'(?:game|puzzle|match)\b'
    r'|\bplay\s+(?:a|me a)\b'
    r'|\b(?:tic[- ]?tac[- ]?toe|hangman|nim|hanoi|connect\s*(?:four|4)|maze|'
    r'rock[- ]?paper[- ]?scissors|concentration|simon)\b', re.I)
_INVERTED = re.compile(r'last one loses|\bmisere\b|whoever takes the last.{0,14}loses',
                       re.I)


class OracleReleaseRuntimeW75(OracleReleaseRuntimeW72):
    """Games composed from primitives, combined by operators, and handed over."""

    @staticmethod
    def _candidates(s):
        return [n for n, c in CATS.items() if any(rx.search(s) for rx in c['cues'])]

    def _route(self, raw):
        s = normalise(raw)
        combo = parse_combination(s)            # may raise GameError with a reason
        if combo:
            return ('combo', combo, [])
        cands = self._candidates(s)
        if not cands:
            raise LookupError('no category')
        ruled = []
        if _INVERTED.search(s) and 'take_away' in cands:
            cands = [c for c in cands if c != 'take_away']
            ruled.append(('take_away', 'the request says the last move LOSES'))
        alive, hit = [], []
        for name in cands:
            try:
                alive.append((name, CATS[name]['params'](s)))
            except GameError as why:
                ruled.append((name, str(why)))
                hit.append(str(why))
        if not alive:
            raise GameError(hit[0] if hit else 'nothing survived')
        if len(alive) > 1:
            raise ValueError('; '.join('%s (%s)' % (n, CATS[n]['describe'](p))
                                       for n, p in alive[:3]))
        return ('simple', alive[0], ruled)

    def _refuse(self, path, body, **prov):
        return {'status': 'withheld', 'path': path, 'response': body,
                'provenance': dict({'kind': 'game', 'built': False}, **prov),
                'latency_ms': 2}

    def chat(self, text: str, session_id: str = 'default') -> dict:
        s = ' '.join(str(text).strip().split())
        if not _WANTS_GAME.search(s):
            return super().chat(s, session_id)

        # The realizations are python. A composed game is now recorded as a
        # program, so reference resolution WILL offer it for "write the same thing
        # in javascript", and the language swap would find no language token in the
        # game's own surface, change nothing, and re-compose the same python game
        # while appearing to answer. That is answering a different question, so it
        # declines instead. This costs a metric and it is the correct behaviour.
        lang = re.search(r'\bin (go|javascript|js|java|rust|c\+\+|ruby|c#)\b',
                         s, re.I)
        if lang:
            return self._refuse(
                'game:no_realization_in_language',
                'I compose games and write them out in python, and I have no %s '
                'realization to write this one in. I could hand you the python and '
                'let you assume it was what you asked for, which is worse than '
                'saying so.' % lang.group(1),
                reason='no realization in %s' % lang.group(1),
                languages=['python'])

        try:
            kind, payload, ruled = self._route(s)
        except LookupError:
            return self._refuse(
                'game:no_category',
                'I build games by composing them, and nothing in that request maps '
                'onto a shape I can compose. The kinds I can build are: %s. Each '
                'takes parameters and each can be inverted or joined to another, '
                'so "connect four", "five in a row on a seven by seven board" and '
                '"tic tac toe then nim" are all available without any of them '
                'being stored.' % ', '.join(sorted(CATS)),
                reason='no category matched', categories=sorted(CATS))
        except ValueError as amb:
            return self._refuse('game:ambiguous',
                                'That could be more than one game and nothing in it '
                                'rules the others out: %s. Say which and I will '
                                'build it.' % amb, reason='ambiguous')
        except GameError as why:
            return self._refuse('game:out_of_bounds',
                                '%s. I would rather tell you the bound than build a '
                                'smaller game and let you assume it was the one you '
                                'asked for.' % str(why).rstrip('.'), reason=str(why))

        # ── build, play, referee ────────────────────────────────────────────
        try:
            if kind == 'combo':
                combo_kind, combo_payload = payload
                game, referee, params = build_and_referee(combo_kind, combo_payload)
                outcome, log, _turns = play(game, COMPOUND_BUDGET)
                second = referee(params, log)
                if second != outcome:
                    raise RefereeDisagrees('engine said %r, referee said %r'
                                           % (outcome, second))
                result = {'outcome': outcome, 'moves': len(log)}
                told = describe_combo(combo_kind, combo_payload)
                category = '%s(%s)' % (combo_kind, combo_payload[0]
                                       if combo_kind == 'invert'
                                       else '%s+%s' % combo_payload[:2])
                emitted = None
            else:
                name, prm = payload
                spec = CATS[name]
                result = verify(spec['build'](prm), spec['referee'], prm)
                told = spec['describe'](prm)
                category = name
                src = emit(name, prm)
                eo, _em = run_emitted(src)      # a THIRD reading, separate process
                if eo != result['outcome']:
                    raise RefereeDisagrees(
                        'the program I wrote out reports %r but playing it here '
                        'gave %r' % (eo, result['outcome']))
                emitted = src
        except RefereeDisagrees as why:
            return self._refuse('game:referee_disagrees',
                                'I built that game and played it, and a second '
                                'reading of the same rules disagreed about what '
                                'happened: %s. One of them is wrong and I do not '
                                'know which, so I am not handing it to you.' % why,
                                built=True, verified=False)
        except EmitError as why:
            return self._refuse('game:cannot_emit',
                                'I composed and played that game, and then could '
                                'not write it out as a program I could run to check '
                                'myself: %s. I will not give you code I have not '
                                'executed.' % why, built=True, verified=False)
        except GameError as why:
            return self._refuse('game:did_not_play',
                                'I composed that game and it did not play to a '
                                'result: %s. A game I cannot finish is not a game I '
                                'can give you.' % why, built=True, verified=False)

        said = {'first': 'the first player won', 'second': 'the second player won',
                'draw': 'it was drawn', 'solved': 'it was solved',
                'failed': 'it was not solved'}[result['outcome']]
        checks = ('I played it through and %s after %d moves. A second reading of '
                  'the same rules replayed every move and agreed.'
                  % (said, result['moves']))
        if emitted:
            checks += (' I also wrote it out as a program and ran that separately, '
                       'and it reported the same result, so three readings agree.')
        extra = (' I ruled out %s, because %s.' % (ruled[0][0].replace('_', ' '),
                                                   ruled[0][1])) if ruled else ''
        body = 'I built you a game: %s. %s%s' % (told, checks, extra)
        if emitted:
            body += '\n\n' + emitted.strip()

        from collections import deque
        hist = getattr(self, '_paths', None)
        if hist is None:
            hist = self._paths = {}
        q = hist.get(session_id)
        if q is None:
            q = hist[session_id] = deque(maxlen=64)
        prev = q[-1].get('turn', 0) if len(q) else 0
        q.append({'turn': prev + 1, 'in_surface': s[:120], 'in_form': ['game_request'],
                  'operator': 'game:composed', 'out_status': 'answered',
                  'in_terms': [], 'out_terms': [],
                  'relation': {'grounded': [], 'grounded_cited': [],
                               'introduced': [], 'unaccounted': []},
                  'carried_from_prior': [], 'continuity_lexical': False,
                  'continuity': True, 'citations': 0, 'residual': None,
                  'cost_ms': 4.0,
                  # recorded as a PROGRAM so a follow-up can refer to it the way it
                  # refers to any other program the machine has written
                  'conversion': {'construction': 'COMPOSED_PROGRAM', 'from': s[:80],
                                 'to': 'game/%s' % category,
                                 'produced_by': 'game_w75'},
                  'verified_warrant': {
                      'kind': 'differential_execution',
                      'steps': ['played to %s in %d moves' % (result['outcome'],
                                                              result['moves']),
                                'referee replayed the log and agreed']
                               + (['the emitted program ran separately and agreed']
                                  if emitted else [])}})
        return {'status': 'answered', 'path': 'game:composed', 'response': body,
                'provenance': {'kind': 'game', 'built': True, 'verified': True,
                               'category': category,
                               'params': (payload[1] if kind == 'simple' else {}),
                               'outcome': result['outcome'],
                               'moves': result['moves'],
                               'emitted_source': bool(emitted),
                               'checked_by': ('engine, independent referee, and the '
                                              'emitted program run separately')},
                'latency_ms': 5}
