#!/usr/bin/env python3
"""oracle_release_runtime_w492 - question FORMS that name their relation, answered from typed relations; and a
resolved pronoun handed to the relation organ.

(A) RELATION FORMS (relation_forms_v1 over oracle_tritree_v2, frozen e89d0cfe / ff52020e). "Where is X", "capital of X",
"what currency does X use", "where was X born", "who wrote X" name their relation in Wikidata's own vocabulary, but
carry no words the mined lexicon matches, so the relation organ found nothing. Each form lists its properties by
SPECIFICITY and they are tried one at a time (only=True); every check still applies (type, one value, corroborating
sentence, verb licence). A lowercase argument ("jamarcus russell") is TRUECASED through the store's own title - people
type lowercase and the reader links only capitalised spans. Measured on WebQuestions (plain wh-questions, Freebase
keys, answer identity) on questions carrying a form:
  train (504): served head answers 212, right 52; with this fold 63 right (+11), wrong unchanged
  TEST, run once, frozen (262): head right 27 -> 33 (+6), wrong 80 -> 79
  (keys are single Freebase containments: "where" answers true at another granularity count as wrong, e.g. Kakadu ->
  Australia vs key Northern Territory; one key is simply wrong: the capital of Ontario is Toronto, key says Ottawa).
  The form answer replaces the chain's only for the families the pairing showed weaker (WEAK) or a decline.
(B) ANAPHORA: found by the first proposer brief.

The first proposer brief ranked conversational follow-ups ("where is it?", "who discovered it?") among the heaviest
unanswered questions people asked. Measured on the gate corpus's DEVELOPMENT scripts (discourse_ab_v1.py, 81 scripts,
serving head w490): ANAPHORA turns 54, answered 39, on-topic 29. The misses are not discourse failures: the chain
resolves the pronoun correctly ("I took "it" to mean Amazon River") and then has no attested fact - a knowledge-reach
gap, which is what the relation organ (typed Wikidata relations, three-tree search, corroborating sentence) exists for.
This fold: where the chain declined with a resolved referent, the person's question is rewritten with the referent in
place of the pronoun and put to the relation organ; its answer is released only if the organ answers (typed, checked,
cited) - otherwise the chain's honest decline stands. The reply says how the pronoun was read.
Parent: the serving tip, named. Methods _c492_.
"""

from __future__ import annotations

import re

from oracle_release_runtime_w490 import OracleReleaseRuntimeW490 as _Base

try:
    import oracle_release_runtime_w480 as _w480
    _run = _w480._run
except Exception:  # noqa: BLE001
    _run = None
try:
    import os as _os
    _os.environ.setdefault("TT_RULES", "A,B")
    import oracle_tritree_v2 as _tt2
    import relation_forms_v1 as _forms
except Exception:  # noqa: BLE001
    _tt2 = _forms = None

# route families the paired WebQuestions measurement showed the typed form answer outranks (never operators, games,
# code or the other organs)
WEAK = ('deliberation', 'factoid', 'arb', 'corpus_query', 'document_runtime', 'compose', 'resolve')
RESOLVED = re.compile(r'I took "(?P<pron>it|he|she|they|them|that|this|its|his|her|their)" to mean (?P<ref>.+?), but', re.I)


class OracleReleaseRuntimeW492(_Base):

    def _c492_tt(self):
        o = getattr(self, '_c492_t', None)
        if o is None and _tt2 is not None and _forms is not None:
            try:
                o = self._c492_t = _tt2.TriTree()
            except Exception:  # noqa: BLE001
                o = self._c492_t = False
        return o or None

    def _c480_dispatch(self, text, session_id, res):
        out = super()._c480_dispatch(text, session_id, res)
        if _run is None:
            return out
        # (A) a PLAIN question whose form names its relation ("where is X", "capital of X", "what currency does X use")
        fam = re.split(r'[|>:]', str(out.get('path', '')))[0]
        if _forms is not None and _forms.form_of(text) and (not self._c480_answered(out) or fam in WEAK):
            tt2 = self._c492_tt()
            got = _run(_forms.answer, tt2, text) if tt2 is not None else None
            if got and got[0]:
                a, form = got
                new = self._c480_rel_reply(out, a, fam)
                new['path'] = 'organ:relation>form:%s>' % form + '>'.join(a.get('trace') or [])
                prov = dict(new.get('provenance') or {})
                prov['form'] = form
                new['provenance'] = prov
                return new
        if self._c480_answered(out):
            return out
        m = RESOLVED.search(str(out.get('response', '')))
        if not m:
            return out
        pron, ref = m.group('pron'), m.group('ref').strip().rstrip('.')
        if not ref or len(ref) > 80:
            return out
        rewritten, n = re.subn(r'\b%s\b' % re.escape(pron), ref, text, count=1, flags=re.I)
        if not n:
            return out
        a, form = None, None
        tt2 = self._c492_tt()
        if tt2 is not None:                               # the question FORM names the relation ("where is X")
            got = _run(_forms.answer, tt2, rewritten)
            if got:
                a, form = got
        if not a:
            org = self._c480_rel()
            a = _run(org.answer, rewritten) if org else None
        if not a:
            return out
        new = self._c480_rel_reply(out, a, '')
        new['response'] = 'Taking "%s" to mean %s: %s' % (pron, ref, new['response'])
        new['path'] = 'organ:relation>anaphora>' + '>'.join(a.get('trace') or [])
        prov = dict(new.get('provenance') or {})
        prov.update({'anaphora': {'pronoun': pron, 'referent': ref, 'rewritten': rewritten}})
        new['provenance'] = prov
        return new
