#!/usr/bin/env python3
"""oracle_release_runtime_w193 - the kernel WALK (depth one): an essay is a path
through attested structure, not a page.

w181 rendered a concept's kernel from the head's own routes. This fold gives the
renderer depth: after the concept's kernel, it walks one edge to the concept
its mechanism names (the first admitted title mentioned in the mechanism
sentences) and one edge to its contrast neighbor, fills a short kernel for
each (genus and mechanism only), and renders the three in sequence, skipping
any claim the session was already told (the selection state of w191). Every
sentence keeps the claim id its route produced; every empty slot is received
as a vessel. A path with no resolvable edge renders as before. Methods are
prefixed _k193_. Parent: the serving tip, named.
"""

from __future__ import annotations

import importlib
import re

from oracle_release_runtime_w191 import OracleReleaseRuntimeW191 as _Base

_an = importlib.import_module('oracle_release_runtime_an')
_content_terms, CITE_RX = _an.content_terms, _an.CITE
_w181 = importlib.import_module('oracle_release_runtime_w181')
ESSAY_Q, _first_sentences, _strip_prefix, _A = _w181.ESSAY_Q, _w181._first_sentences, _w181._strip_prefix, _w181._A

CAP_NGRAM = re.compile(r"\b([A-Z][a-z]{2,}(?:\s+[A-Z][a-z]{2,}){0,2})\b")
LOW_WORD = re.compile(r"\b([a-z]{4,})\b")


import os
import sqlite3
from pathlib import Path

WIDE_LEAD = re.compile(r"^(?:a|an|the)?\s*(?P<t>[\w][\w \-']{1,60}?)\b[^.]{0,40}?\b(?:is|are|means|refers to|is defined as|denotes|describes|consists of)\b", re.I)


class OracleReleaseRuntimeW193(_Base):
    """Kernel walk: concept, its cause, its neighbor; rendered as a path.
    Also F4 (scorer width): a definitional lead may say "means", "refers to", "is the ...",
    not only "is a/an"; and the cause edge comes from the edge table when one exists."""

    # ---------------------------------------------------------------- F4: wider definitional lead
    def _definitional_turn(self, text: str):
        got = super()._definitional_turn(text)
        if got:
            return got
        m = re.match(r"^what is (?:a |an |the )?(?P<term>[\w][\w \-']{1,60}?)\??$", ' '.join(str(text).split()), re.I)
        if not m:
            return None
        term = m.group('term').strip()
        try:
            bundle = self._bundle(term.title()) or self._bundle(term)
        except Exception:
            bundle = []
        best = None
        for c in bundle[:8]:
            sent = str(c.get('sentence', ''))
            w = WIDE_LEAD.match(sent)
            if w and w.group('t').strip().lower() == term.lower():
                best = c
                break
        if not best:
            return None
        return {'status': 'answered', 'path': 'definitional_encyclopedic|wide_lead',
                'response': '%s [%s]' % (best['sentence'], best['claim_id']),
                'provenance': {'kind': 'dbpedia_page', 'page': best['page'], 'claim_id': best['claim_id'], 'lead_form': 'wide'}}

    # ---------------------------------------------------------------- cause edge from the edge table
    def _k193_edge_cause(self, x: str):
        try:
            bench = os.environ.get('ORACLE_BENCH_BUILD')
            edges = Path(bench).parent / 'edges.sqlite' if bench else None
            if not edges or not edges.exists():
                return None
            pid = self.bench_query.page_id(x) or self.bench_query.page_id(x.title())
            if not pid:
                return None
            con = sqlite3.connect('file:%s?mode=ro' % edges, uri=True)
            rows = con.execute('select dst, count(*) n from edge where src=? group by dst order by n desc limit 6', (pid,)).fetchall()
            con.close()
            for dst, _ in rows:
                row = self.bench_query.connection.execute('select title from article where page_id=?', (dst,)).fetchone()
                if row and row[0].lower() != x.lower() and '(' not in row[0] and len(row[0].split()) <= 3:
                    return row[0]
        except Exception:
            return None
        return None

    def _k193_cause_title(self, x: str, mech_text: str):
        """The first admitted title named in the mechanism sentences, other than the concept."""
        cands = [c for c in CAP_NGRAM.findall(mech_text) if c.lower() != x.lower()]
        cands += [w for w in LOW_WORD.findall(mech_text) if w.lower() != x.lower()][:40]
        seen = set()
        for c in cands:
            k = c.lower()
            if k in seen or k in ('the', 'this', 'that', 'these', 'which', 'when', 'where', 'because'):
                continue
            seen.add(k)
            try:
                if self.bench_query.page_id(c) or self.bench_query.page_id(c.title()):
                    return c
            except Exception:
                continue
        return None

    def _k193_short_kernel(self, y: str, session_id: str) -> dict:
        slots = {}
        for slot, surfaces in (('genus', ('What is %s %s?' % (_A(y), y), 'What is %s?' % y)),
                               ('mechanism', ('What causes %s?' % y, 'How does %s work?' % y))):
            for sf in surfaces:
                r = self._k181_ask(sf, session_id)
                if self._k181_usable(r):
                    slots[slot] = {'text': _strip_prefix(r['response']), 'path': str(r.get('path'))}
                    break
        return slots

    def _k193_untold(self, session_id: str, text: str) -> str:
        """Drop sentences whose citations the session already holds (selection state of w191)."""
        try:
            told = self._s187_state(session_id)['told']
        except Exception:
            return text
        keep = []
        for sent in re.split(r"(?<=\])\s+", text):
            ids = set(CITE_RX.findall(sent))
            if ids and ids <= told:
                continue
            keep.append(sent)
        return ' '.join(keep).strip()

    def _k193_no_repeat(self, s: str, session_id: str, result: dict) -> dict:
        """A wide-lead definition that only repeats what the session was told is replaced by
        untold claims from the same page (the selection rule of w191, applied to this route)."""
        try:
            path = str(result.get('path', ''))
            if 'wide_lead' not in path or result.get('status') != 'answered':
                return result
            st = self._s187_state(session_id)
            cited = set(CITE_RX.findall(str(result.get('response', ''))))
            if not cited or not (cited <= st['told']):
                return result
            page, title = self._s187_page_of(result)
            if not page:
                return result
            picks = self._s187_novel_claims(st, page, 3)
            if not picks:
                return result
            body = 'Beyond what I already told you on %s: ' % (title or page) + ' '.join('%s [%s]' % (f, c) for c, f in picks)
            result = dict(result)
            result['response'] = body
            result['path'] = path + '|select:novel'
            q = self._paths.get(session_id)
            if q and len(q) and q[-1].get('in_surface', '')[:60] == s[:60]:
                rec = q[-1]
                rec['operator'] = result['path']
                self._recite(rec, s, body)
            st['told'] |= set(CITE_RX.findall(body))
            st['terms'] |= set(_content_terms(body))
        except Exception:
            pass
        return result

    def chat(self, text: str, session_id: str = 'default') -> dict:
        s = ' '.join(str(text).strip().split())
        m = ESSAY_Q.match(s)
        if not m:
            return self._k193_no_repeat(s, session_id, super().chat(s, session_id))
        base = super().chat(s, session_id)        # w181's kernel render (with w191's selection state)
        if str(base.get('path', '')) != 'kernel_render':
            return base
        x = (m.group('t') or m.group('t2') or '').strip().lower()
        prov = dict(base.get('provenance') or {})
        filled = prov.get('filled') or {}
        body = str(base.get('response', ''))
        sections = []
        walked = {}
        # edge 1: the cause the mechanism names
        mech = ''
        try:
            mech = self._k181_ask('What causes %s?' % x, session_id).get('response', '') if 'mechanism' in filled else ''
        except Exception:
            mech = ''
        cause = self._k193_edge_cause(x) or (self._k193_cause_title(x, _strip_prefix(mech)) if mech else None)
        if cause:
            k = self._k193_short_kernel(cause.lower(), session_id)
            if 'genus' in k:
                txt = self._k193_untold(session_id, _first_sentences(k['genus']['text'], 2) + (' ' + _first_sentences(k['mechanism']['text'], 2) if 'mechanism' in k else ''))
                if txt:
                    sections.append('One edge along its cause, to %s: %s' % (cause, txt))
                    walked['cause'] = {'title': cause, 'slots': sorted(k)}
        # edge 2: the contrast neighbor already chosen by the renderer
        neighbor = None
        try:
            neighbor = [t for t in self._related_titles(x.title(), cap=6)
                        if t.lower() != x.lower() and '(' not in t and len(t.split()) <= 3
                        and not t.lower().startswith(x.lower() + ' ')][:1]
            neighbor = neighbor[0] if neighbor else None
        except Exception:
            neighbor = None
        if neighbor and neighbor != cause:
            k = self._k193_short_kernel(neighbor.lower(), session_id)
            if 'genus' in k:
                txt = self._k193_untold(session_id, _first_sentences(k['genus']['text'], 2))
                if txt:
                    sections.append('One edge across, to %s, for contrast: %s' % (neighbor, txt))
                    walked['neighbor'] = {'title': neighbor, 'slots': sorted(k)}
        if not sections:
            return base
        # splice the walk before the closing two paragraphs of the kernel render
        paras = body.split('\n\n')
        tail = [p for p in paras if p.startswith('In a system whose rules') or p.startswith('Held and not yet named') or p.endswith('empty slots still hold.')]
        head = [p for p in paras if p not in tail]
        body2 = '\n\n'.join(head + sections + tail)
        result = dict(base)
        result['response'] = body2
        result['path'] = 'kernel_walk'
        prov['walk'] = walked
        result['provenance'] = prov
        try:
            q = self._paths.get(session_id)
            if q and len(q) and q[-1].get('in_surface', '')[:60] == s[:60]:
                rec = q[-1]
                rec['operator'] = 'kernel_walk'
                rec['in_form'] = list(rec.get('in_form') or []) + ['kernel_walk']
                self._recite(rec, s, body2)
        except Exception:
            pass
        try:
            st = self._s187_state(session_id)
            st['told'] |= set(CITE_RX.findall(body2))
            st['terms'] |= set(_content_terms(body2))
            dlg = getattr(self, 'dialogue', None)
            if isinstance(dlg, dict):
                dlg.setdefault(session_id, {})['last_result'] = result
        except Exception:
            pass
        return result
