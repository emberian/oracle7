#!/usr/bin/env python3
"""oracle_release_runtime_w54 - DEDUCTION: the operator that should have been first.

The open-ended audit found the machine clarifying on "if all mammals are warm
blooded and a whale is a mammal, is a whale warm blooded?" - a question that is
pure composition, which is the architecture's native act. It had every mechanism
for warranted reasoning and no route for the oldest form of it.

This fold reads premises and answers what FOLLOWS from them. The warrant form is
DERIVATION: every step names the rule that licensed it, so the answer is not a
claim to be trusted but a proof to be checked. Six classical forms:

    universal instantiation   all A are B; x is A            -> x is B
    universal transitivity    all A are B; all B are C       -> all A are C
    negative instantiation    no A are B; x is A             -> x is not B
    modus ponens              if P then Q; P                 -> Q
    modus tollens             if P then Q; not Q             -> not P
    disjunctive syllogism     P or Q; not P                  -> Q

Premises accumulate across turns, so "All men are mortal." / "Socrates is a man."
/ "Is Socrates mortal?" works as three exchanges the way a person would say it.

And the discipline that makes it worth having: when the premises do NOT license
the conclusion, it says so and names what is missing. A deduction engine that
answers everything is a guessing engine with better manners.

Hand-authored 2026-08-28 as Phase 1 of the minimal-basis program.
Judged by the gate.
"""

from __future__ import annotations

import re

from oracle_release_runtime_w51 import OracleReleaseRuntimeW51

_ART = re.compile(r'^(?:a|an|the|all|every|some)\s+', re.I)
_SPLIT = re.compile(
    r'[.;?]'
    r'|,\s*(?:and|then|so|therefore)\s+'
    r'|,\s*(?=(?:is|are|was|were|does|do|what|then)\b)'
    r'|\s+and\s+(?=(?:all|every|no|if|either)\b)'
    r'|\s+and\s+(?=(?:a|an|the)\s+\w+\s+(?:is|are)\b)', re.I)
_QUES = re.compile(r'^(?:is|are|was|were|does|do|what|which|can)\b', re.I)

_ALL = re.compile(r'^(?:all|every|each)\s+(.+?)\s+(?:are|is)\s+(.+)$', re.I)
_NO = re.compile(r'^no\s+(.+?)\s+(?:are|is)\s+(.+)$', re.I)
_INST = re.compile(r'^(.+?)\s+is\s+(?:a|an|the)?\s*(.+)$', re.I)
_COND = re.compile(r'^if\s+(.+?)\s*,?\s+then\s+(.+)$', re.I)
_HAVE = re.compile(r'^(?:all|every|each)\s+(.+?)\s+(?:have|has)\s+(.+)$', re.I)
_ASK_HAVE = re.compile(r'^(?:does|do)\s+(.+?)\s+have\s+(.+?)\??$', re.I)
_OR = re.compile(r'^(?:either\s+)?(.+?)\s+or\s+(.+)$', re.I)
_NOT = re.compile(r'^(?:not|it is not (?:the case )?that)\s+(.+)$|^(.+?)\s+is not\s+(.+)$', re.I)

_ASK_IS = re.compile(r'^(?:is|are|was|were)\s+(.+?)\s+(.+?)\??$', re.I)
_ASK_FOLLOW = re.compile(
    r'\b(?:what follows|does (?:it|that) follow|what can (?:we|you) conclude|'
    r'therefore what|what do you conclude)\b', re.I)
_HAS_PREMISE = re.compile(
    r'\b(?:all|every|each|no)\s+\w+\s+(?:are|is|have|has)\b'
    r'|\bif\s+.+\bthen\b|\beither\b.+\bor\b',
    re.I)


_IRREG = {'men': 'man', 'women': 'woman', 'children': 'child', 'people': 'person',
          'feet': 'foot', 'teeth': 'tooth', 'mice': 'mouse', 'geese': 'goose',
          'oxen': 'ox', 'lives': 'life', 'wolves': 'wolf', 'leaves': 'leaf'}


def _norm(t):
    t = ' '.join(str(t).strip().lower().split())
    t = _ART.sub('', t)
    t = t.strip(' ?.!,')
    head = t.split()[-1] if t.split() else t
    if head in _IRREG:
        t = (' '.join(t.split()[:-1]) + ' ' + _IRREG[head]).strip()
    elif t.endswith('s') and not t.endswith(('ss', 'us', 'is')) and len(t) > 3:
        t = t[:-1]
    return t


class OracleReleaseRuntimeW54(OracleReleaseRuntimeW51):
    """Base + deduction. Warrant form: a derivation with every rule named."""

    def _store(self, session_id):
        d = getattr(self, '_premises', None)
        if d is None:
            d = self._premises = {}
        return d.setdefault(session_id, {'all': [], 'no': [], 'inst': [],
                                         'cond': [], 'or': [], 'fact': [],
                                         'nfact': [], 'have': [], 'text': []})

    def _ingest(self, surface, st):
        """Read every premise the surface carries. Returns how many were new."""
        added = 0
        for raw in _SPLIT.split(surface):
            s = ' '.join(str(raw).strip().split()).strip(' ,')
            if not s or len(s) < 4:
                continue
            if s.lower().startswith('if ') and ' then ' not in s.lower():
                s = s[3:].strip()          # a bare "if" with no consequent
            low = s.lower().strip()
            if low.startswith(('is ', 'are ', 'was ', 'were ', 'what ', 'does ')):
                continue                                   # that is the question
            m = _COND.match(s)
            if m:
                st['cond'].append((_norm(m.group(1)), _norm(m.group(2))))
                st['text'].append(s)
                added += 1
                continue
            m = _HAVE.match(s)
            if m:
                st.setdefault('have', []).append((_norm(m.group(1)), _norm(m.group(2))))
                st['text'].append(s)
                added += 1
                continue
            m = _NO.match(s)
            if m:
                st['no'].append((_norm(m.group(1)), _norm(m.group(2))))
                st['text'].append(s)
                added += 1
                continue
            m = _ALL.match(s)
            if m:
                st['all'].append((_norm(m.group(1)), _norm(m.group(2))))
                st['text'].append(s)
                added += 1
                continue
            m = _OR.match(s)
            if m and ' or ' in s.lower():
                st['or'].append((_norm(m.group(1)), _norm(m.group(2))))
                st['text'].append(s)
                added += 1
                continue
            m = _NOT.match(s)
            if m:
                if m.group(1):
                    st['nfact'].append(_norm(m.group(1)))
                else:
                    st['no'].append((_norm(m.group(2)), _norm(m.group(3))))
                    # "the server is not down" is also the denial of the whole
                    # proposition, which is what a disjunctive syllogism needs
                    st['nfact'].append('%s is %s' % (_norm(m.group(2)),
                                                     _norm(m.group(3))))
                st['text'].append(s)
                added += 1
                continue
            m = _INST.match(s)
            if m:
                st['inst'].append((_norm(m.group(1)), _norm(m.group(2))))
                st['text'].append(s)
                added += 1
                continue
            # a bare asserted proposition ("it rains"), which modus ponens needs
            if len(s.split()) <= 8:
                st['fact'].append(_norm(s))
                st['text'].append(s)
                added += 1
        return added

    def _closure(self, st):
        """Transitive closure over universals, recording the path used."""
        edges = {}
        for a, b in st['all']:
            edges.setdefault(a, set()).add(b)
        reach = {}
        for start in list(edges):
            seen, stack, path = {}, [(start, [start])], None
            while stack:
                node, trail = stack.pop()
                for nxt in edges.get(node, ()):
                    if nxt in seen:
                        continue
                    seen[nxt] = trail + [nxt]
                    stack.append((nxt, trail + [nxt]))
            reach[start] = seen
        return reach

    def _try_pair(self, subj, pred, st, reach):
        """Can the premises license 'subj is pred'? Returns (verdict, steps)."""
        for x, cls in st['inst']:
            if x != subj:
                continue
            if cls == pred:
                return ('yes', ['%s is %s (premise)' % (subj, pred)])
            for a, b in st['no']:
                if b == pred and (a == cls or a in reach.get(cls, {})):
                    return ('no', ['no %s are %s (premise)' % (a, b),
                                   '%s is %s (premise)' % (subj, cls),
                                   'by negative instantiation, %s is not %s'
                                   % (subj, pred)])
            if pred in reach.get(cls, {}):
                path = reach[cls][pred]
                steps = ['%s is %s (premise)' % (subj, cls)]
                for i in range(len(path) - 1):
                    steps.append('all %s are %s (premise)' % (path[i], path[i + 1]))
                steps.append('by universal instantiation%s, %s is %s'
                             % (' and transitivity' if len(path) > 2 else '',
                                subj, pred))
                return ('yes', steps)
        return None

    def _derive(self, question, st):
        """Return (verdict, steps) or None if nothing follows."""
        reach = self._closure(st)

        mh = _ASK_HAVE.match(question.strip())
        if mh:
            subj, prop = _norm(mh.group(1)), _norm(mh.group(2))
            for x, cls in st['inst']:
                if x != subj:
                    continue
                for a, b in st.get('have', []):
                    if b == prop and (a == cls or prop in () or a in reach.get(cls, {})):
                        steps = ['%s is %s (premise)' % (subj, cls)]
                        if a != cls:
                            steps.append('all %s are %s (premise)' % (cls, a))
                        steps.append('all %s have %s (premise)' % (a, b))
                        steps.append('by universal instantiation, %s has %s'
                                     % (subj, prop))
                        return ('yes', steps)
        m = _ASK_IS.match(question.strip())
        if m:
            # "is a lizard warm blooded" has no single right split, so try every
            # one and keep the reading the premises can actually license.
            rest = re.sub(r'^(?:is|are|was|were)\s+', '', question.strip(), flags=re.I)
            rest = rest.strip(' ?.!')
            toks = rest.split()
            candidates = []
            for i in range(1, len(toks)):
                candidates.append((_norm(' '.join(toks[:i])),
                                   _norm(' '.join(toks[i:]))))
            known = {x for x, _ in st['inst']}
            candidates.sort(key=lambda sp: (sp[0] not in known, len(sp[0])))
            for subj, pred in candidates:
                got = self._try_pair(subj, pred, st, reach)
                if got is not None:
                    return got
            subj, pred = _norm(m.group(1)), _norm(m.group(2))
            for x, cls in st['inst']:
                if x != subj:
                    continue
                if cls == pred:
                    return ('yes', ['%s is %s (premise)' % (subj, pred)])
                # negative first: a stated exclusion beats a positive chain
                for a, b in st['no']:
                    if b == pred and (a == cls or pred in reach.get(cls, {})):
                        return ('no', ['no %s are %s (premise)' % (a, b),
                                       '%s is %s (premise)' % (subj, cls),
                                       'by negative instantiation, %s is not %s'
                                       % (subj, pred)])
                if pred in reach.get(cls, {}):
                    path = reach[cls][pred]
                    steps = ['%s is %s (premise)' % (subj, cls)]
                    for i in range(len(path) - 1):
                        steps.append('all %s are %s (premise)' % (path[i], path[i + 1]))
                    steps.append('by universal instantiation%s, %s is %s'
                                 % (' and transitivity' if len(path) > 2 else '',
                                    subj, pred))
                    return ('yes', steps)
            # conditional forms on the raw proposition
            q = _norm(question)
            for p, cq in st['cond']:
                if cq == q or cq == pred:
                    if p in [f for f in st['fact']] or any(
                            x + ' is ' + c == p for x, c in st['inst']):
                        return ('yes', ['if %s then %s (premise)' % (p, cq),
                                        '%s (premise)' % p,
                                        'by modus ponens, %s' % cq])
        if _ASK_FOLLOW.search(question):
            for p, q in st['cond']:
                if q in st['nfact']:
                    return ('conclusion', ['if %s then %s (premise)' % (p, q),
                                           'not %s (premise)' % q,
                                           'by modus tollens, not %s' % p])
                if p in st['fact']:
                    return ('conclusion', ['if %s then %s (premise)' % (p, q),
                                           '%s (premise)' % p,
                                           'by modus ponens, %s' % q])
            for a, b in st['or']:
                if a in st['nfact']:
                    return ('conclusion', ['%s or %s (premise)' % (a, b),
                                           'not %s (premise)' % a,
                                           'by disjunctive syllogism, %s' % b])
                if b in st['nfact']:
                    return ('conclusion', ['%s or %s (premise)' % (a, b),
                                           'not %s (premise)' % b,
                                           'by disjunctive syllogism, %s' % a])
            for a in list(reach):
                for b, path in reach[a].items():
                    if len(path) > 2:
                        return ('conclusion',
                                ['all %s are %s (premise)' % (path[i], path[i + 1])
                                 for i in range(len(path) - 1)]
                                + ['by transitivity, all %s are %s' % (a, b)])
        return None

    def _witness_deduce(self, session_id, surface, steps, answered):
        from collections import deque
        hist = getattr(self, '_paths', None)
        if hist is None:
            hist = self._paths = {}
        q = hist.get(session_id)
        if q is None:
            q = hist[session_id] = deque(maxlen=64)
        prev = q[-1].get('turn', 0) if len(q) else 0
        q.append({'turn': prev + 1, 'in_surface': str(surface)[:120],
                  'in_form': ['premises', 'query'], 'operator': 'deduce:derived',
                  'out_status': 'answered' if answered else 'withheld',
                  'in_terms': [], 'out_terms': [],
                  'relation': {'grounded': [], 'grounded_cited': [],
                               'introduced': [], 'unaccounted': []},
                  'carried_from_prior': ['premises'], 'continuity_lexical': True,
                  'continuity': True, 'citations': 0, 'residual': None,
                  'cost_ms': 1.5,
                  'conversion': {'construction': 'DERIVATION',
                                 'from': str(surface)[:80],
                                 'to': steps[-1][:60] if steps else 'no conclusion',
                                 'produced_by': 'deduce_w47'},
                  'verified_warrant': ({'kind': 'deduction', 'steps': steps}
                                       if answered else None)})

    def chat(self, text: str, session_id: str = 'default') -> dict:
        s = ' '.join(str(text).strip().split())
        st = self._store(session_id)
        had = bool(st['all'] or st['no'] or st['cond'] or st['or'] or st['inst'])

        # separate what is asserted from what is asked, so a single sentence
        # carrying both ("all A are B and x is A, is x B?") works like a person
        clauses = [c.strip(' ,') for c in _SPLIT.split(s) if c and c.strip(' ,')]
        question_clauses = [c for c in clauses if _QUES.match(c)]
        premise_clauses = [c for c in clauses if not _QUES.match(c)]
        carries = bool(_HAS_PREMISE.search(' . '.join(premise_clauses)))
        added = 0
        if carries or (had and premise_clauses):
            added = self._ingest(' . '.join(premise_clauses), st)
        query = question_clauses[-1] if question_clauses else s
        asking = bool(question_clauses or _ASK_FOLLOW.search(s))
        if not asking:
            if carries or added:
                # premises stated with no question yet: acknowledge and hold them
                return {'status': 'answered', 'path': 'deduce:premises_held',
                        'response': ('Held as premises: %s. Ask what follows.'
                                     % '; '.join(st['text'][-3:])),
                        'provenance': {'kind': 'deduction', 'premises_held':
                                       len(st['text'])},
                        'latency_ms': 1}
            return super().chat(s, session_id)

        got = self._derive(query, st)
        if got is None:
            if not (st['all'] or st['no'] or st['cond'] or st['or']):
                return super().chat(s, session_id)      # no premises: not our turn
            self._witness_deduce(session_id, s, [], False)
            return {'status': 'withheld', 'path': 'deduce:does_not_follow',
                    'response': ('That does not follow from what I was given. '
                                 'Premises on the table: %s. Nothing in them '
                                 'licenses that conclusion, so I will not assert it.'
                                 % '; '.join(st['text'][-4:])),
                    'provenance': {'kind': 'deduction', 'valid': False,
                                   'reason': 'no_licensing_rule'},
                    'latency_ms': 2}

        verdict, steps = got
        head = {'yes': 'Yes.', 'no': 'No.'}.get(verdict, 'It follows.')
        body = '%s %s.' % (head, '; then '.join(steps))
        self._witness_deduce(session_id, s, steps, True)
        pending = getattr(self, '_pending_conversion', None)
        if pending is None:
            pending = self._pending_conversion = {}
        pending[session_id] = {'construction': 'DERIVATION', 'from': s[:80],
                               'to': verdict, 'produced_by': 'deduce_w47'}
        return {'status': 'answered', 'path': 'deduce:derived',
                'response': body,
                'provenance': {'kind': 'deduction', 'valid': True,
                               'verdict': verdict, 'steps': steps,
                               'rule_count': len(steps)},
                'latency_ms': 2}
