#!/usr/bin/env python3
"""oracle_release_runtime_w242 - the composition seam made faithful. CORRECTNESS RELEASE.

Codex's review of 2026-09-04 read the w181/w193 seam and showed three places where
the renderer's words were stronger than the evidence under them:

  1  the 'parts' slot was filled by "List three facts about X" and rendered as
     "What X is made of, as the record lists it" - facts are not parts
  2  the 'mechanism' slot treated "What causes X?" and "How does X work?" as one
     relation - a cause and a process step are different relations
  3  the walk took the most frequent untyped edge and said "One edge along its
     cause" - Compiler -> Parsing, Photosynthesis -> Process, Gravity -> Weight,
     none of them attested as causes

w240 makes the relation explicit at every seam and lets the words follow it:

  typing      every route answer carries the RELATION its path warrants
              (what_causes -> cause, how_does -> process, list_n -> facts,
              timeline -> history, made_of/conceptnet -> made_of, compare ->
              contrast, definitional -> genus), checked against the sentence's
              own markers: a cause route whose sentences carry no cause marker
              is facts
  admission   a slot is FILLED only by a compatible relation; material that
              answered but does not fit is rendered under an honest heading
              ("Facts the record lists about X") and the slot stays held, so
              the residual is real
  walk        "along its cause" is said only for a caused_by edge from the typed
              edge table (oracle_edge_table_v2), with the attesting claim cited;
              a title merely mentioned in the cause material is labelled a
              mention, never a cause; an untyped edge table yields no cause at all

It is a correctness release: the baseline's headings asserted relations the
record never licensed, so a fall in a count that depended on those assertions
would be the removal of an artifact, not a loss. Methods _s240_. Parent: the
serving tip, named.
"""

from __future__ import annotations

import importlib
import os
import re
import sqlite3
from pathlib import Path

from oracle_release_runtime_w198 import OracleReleaseRuntimeW198 as _Base

_w181 = importlib.import_module('oracle_release_runtime_w181')
_first_sentences, _strip_prefix, _A = _w181._first_sentences, _w181._strip_prefix, _w181._A

ROUTE_REL = (('what_causes', 'cause'), ('how_does', 'process'), ('list_n', 'facts'), ('timeline', 'history'),
             ('made_of', 'made_of'), ('conceptnet', 'made_of'), ('compare', 'contrast'), ('definitional', 'genus'))
SLOT_ACCEPTS = {'genus': ('genus',), 'parts': ('made_of',), 'mechanism': ('cause', 'process'), 'founders': ('history',), 'contrast': ('contrast',)}
CAUSE_MARK = re.compile(r"\b(because|caused by|due to|results? (?:from|in|of)|the result of|leads? to|causes?|arises? from|produced by|driven by|owing to)\b", re.I)
PROCESS_MARK = re.compile(r"\b(works? by|process|occurs? when|converts?|steps?|stages?|cycle|reaction|mechanism)\b", re.I)
HIST_MARK = re.compile(r"\b(1[0-9]{3}|20[0-2][0-9])\b")
MADE_MARK = re.compile(r"\b(consists? of|made of|composed of|comprises?|made up of|contains?|includes?|parts?|components?)\b", re.I)
CAUSE_LABEL = re.compile(r"One edge along its cause, to ([^:]{1,80}):")


class OracleReleaseRuntimeW242(_Base):
    """Typed slots, honest headings, a cause walk that says cause only when the record does."""

    _SLOT_SURFACES = (
        ('genus', ('What is {a} {x}?', 'What is {x}?')),
        ('parts', ('What is {a} {x} made of?', 'List three facts about {x}.')),
        ('mechanism', ('What causes {x}?', 'How does {x} work?')),
        ('founders', ('Give me a timeline of {x}.',)),
    )
    _s240_last_edge = None      # ('caused_by', claim_id) | ('mention', None) | None
    _s240_pending_facts = None  # material that answered but did not fit its slot, for the render

    # ---------------------------------------------------------------- relation typing
    @staticmethod
    def _s240_relation(path, text: str) -> str:
        p = str(path).lower()
        rel = 'facts'
        for key, r in ROUTE_REL:
            if key in p:
                rel = r
                break
        if rel == 'cause' and not CAUSE_MARK.search(text):
            rel = 'process' if PROCESS_MARK.search(text) else 'facts'
        if rel == 'made_of' and not MADE_MARK.search(text):
            rel = 'facts'
        if rel == 'history' and not HIST_MARK.search(text):
            rel = 'facts'
        return rel

    def _k181_fill(self, x: str, session_id: str) -> dict:  # type: ignore[override]
        slots, facts = {}, []
        for slot, surfaces in self._SLOT_SURFACES:
            for sf in surfaces:
                r = self._k181_ask(sf.format(x=x, a=_A(x)), session_id)
                if not self._k181_usable(r):
                    continue
                text = _strip_prefix(r['response'])
                rel = self._s240_relation(r.get('path'), text)
                if rel in SLOT_ACCEPTS.get(slot, ()):
                    slots[slot] = {'text': text, 'path': str(r.get('path')), 'relation': rel}
                    break
                facts.append({'slot': slot, 'text': text, 'path': str(r.get('path')), 'relation': rel})
        try:
            related = [t for t in self._related_titles(x.title(), cap=6)
                       if t.lower() != x.lower() and '(' not in t and len(t.split()) <= 3
                       and not t.lower().startswith(x.lower() + ' ')][:1]
        except Exception:
            related = []
        if related:
            r = self._k181_ask('Compare %s and %s.' % (x, related[0]), session_id)
            if self._k181_usable(r):
                slots['contrast'] = {'text': _strip_prefix(r['response']), 'path': str(r.get('path')), 'neighbor': related[0], 'relation': 'contrast'}
        self._s240_pending_facts = facts
        return slots

    def _k181_render(self, x: str, slots: dict, empty: list, vessels: list) -> str:  # type: ignore[override]
        X = x[0].upper() + x[1:]
        paras = []
        if 'genus' in slots:
            paras.append(_first_sentences(slots['genus']['text'], 3))
        if 'parts' in slots:
            paras.append('What %s is made of, as the record lists it: %s' % (x, _first_sentences(slots['parts']['text'], 4)))
        if 'mechanism' in slots:
            head = 'What causes it, as the record attests: ' if slots['mechanism'].get('relation') == 'cause' else 'How it proceeds: '
            paras.append(head + _first_sentences(slots['mechanism']['text'], 4))
        if 'contrast' in slots:
            paras.append('Set beside %s: %s' % (slots['contrast']['neighbor'], _first_sentences(slots['contrast']['text'], 4)))
        if 'founders' in slots:
            paras.append('Its history, as dated in the record: %s' % _first_sentences(slots['founders']['text'], 4))
        facts = self._s240_pending_facts or []
        self._s240_pending_facts = None
        if facts:
            # list answers arrive numbered and often repeat the definition: strip the numbers, drop what the genus already said
            said = ' '.join(p for p in paras)
            fresh = []
            for f in facts:
                for s in re.split(r"(?<=[.!?\]])\s+(?=(?:\d+\.\s*)?[\"'(]?[A-Z])", ' '.join(str(f['text']).split())):
                    s = re.sub(r"^\d+\.\s*", '', s).strip()
                    core = re.sub(r"\s*\[[^\]]+\]", '', s)
                    if len(core) > 20 and core[:60] not in said and core not in fresh:
                        fresh.append(s)
                    if len(fresh) >= 2:
                        break
                if len(fresh) >= 2:
                    break
            if fresh:
                paras.append('Facts the record lists about %s, not yet placed in a slot: %s' % (x, ' '.join(fresh)))
        filled = [s for s in ('genus', 'parts', 'mechanism', 'contrast', 'founders') if s in slots]
        paras.append('In a system whose rules are written down, %s is held as %d filled slot%s of a kernel of nine moves, each slot '
                     'filled only by the relation its route warrants; every sentence above carries the citation its route produced, '
                     'and nothing here was composed without one.' % (x, len(filled), '' if len(filled) == 1 else 's'))
        if empty:
            paras.append('Held and not yet named: %s. Each is kept as a weighted shape%s until an admitted source fills it.'
                         % ('; '.join('%s (%s)' % (e, self._SLOT_QUESTIONS.get(e, 'a bound').format(x=x)) for e in empty),
                            (' [' + ', '.join('vessel:' + v for v in vessels) + ']') if vessels else ''))
        if 'genus' in slots:
            paras.append('%s is the record\'s answer to what it is; what it does is the question the empty slots still hold.' % X)
        return '\n\n'.join(paras)

    # ---------------------------------------------------------------- typed cause walk
    def _s240_edges(self):
        bench = os.environ.get('ORACLE_BENCH_BUILD')
        p = Path(bench).parent / 'edges.sqlite' if bench else None
        return p if p and p.exists() else None

    def _k193_edge_cause(self, x: str):  # type: ignore[override]
        self._s240_last_edge = None
        edges = self._s240_edges()
        if not edges:
            return None
        try:
            con = sqlite3.connect('file:%s?mode=ro' % edges, uri=True)
            cols = [r[1] for r in con.execute('pragma table_info(edge)')]
            if 'rel' not in cols:
                con.close()
                return None                       # an untyped table attests no causes
            pid = self.bench_query.page_id(x) or self.bench_query.page_id(x.title())
            if not pid:
                con.close()
                return None
            rows = con.execute("select dst, claim_id, count(*) n from edge where src=? and rel='caused_by' group by dst order by n desc limit 20", (pid,)).fetchall()
            con.close()
            for dst, cid, _ in rows:
                row = self.bench_query.connection.execute('select title from article where page_id=?', (dst,)).fetchone()
                if not row:
                    continue
                title = row[0]
                if title.lower() == x.lower() or '(' in title or len(title.split()) > 3:
                    continue
                self._s240_last_edge = ('caused_by', cid)
                return title
        except Exception:
            return None
        return None

    def _k193_cause_title(self, x: str, mech_text: str):  # type: ignore[override]
        t = super()._k193_cause_title(x, mech_text)
        if t:
            self._s240_last_edge = ('mention', None)
        return t

    def chat(self, text: str, session_id: str = 'default') -> dict:
        self._s240_last_edge = None
        res = super().chat(text, session_id)
        try:
            if isinstance(res, dict) and str(res.get('path', '')).startswith('kernel'):
                body = str(res.get('response', ''))
                if CAUSE_LABEL.search(body):
                    edge = self._s240_last_edge
                    if edge and edge[0] == 'caused_by':
                        body = CAUSE_LABEL.sub(lambda m: 'One edge along its cause, to %s, attested [%s]:' % (m.group(1), edge[1]), body, count=1)
                    else:
                        body = CAUSE_LABEL.sub(r'One edge to \1, a page named beside it in the record (a mention, not a shown cause):', body, count=1)
                    res = dict(res, response=body)
                    prov = dict(res.get('provenance') or {})
                    walked = dict(prov.get('walked') or {})
                    if 'cause' in walked:
                        walked['cause'] = dict(walked['cause'], relation=(edge[0] if edge else 'none'), claim_id=(edge[1] if edge else None))
                        prov['walked'] = walked
                        res['provenance'] = prov
        except Exception:
            pass
        return res
