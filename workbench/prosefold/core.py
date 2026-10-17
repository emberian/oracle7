"""prosefold - essays from Oracle7's own cited answers, with no language model. ProseFold (fold/foldtoys, vendored here as
engine.py + prose.py) measures a text's voice; the essay is a beam search over the FAITHFUL ways of composing the record's
sentences (stop, pronoun, "and", semicolon), keeping the arrangement closest to a target voice corpus on the dimensions a
composition can move. Every word stays the record's; every sentence keeps its record id; every composed sentence must
decompose into its parts. Built 2026-10-16 (Box C prosefold_v1: 20 topics, 205/205 faithful, fold beat random choices on
20/20, a planted word change caught 20/20). Essay QUALITY is not claimed: it waits for blind human scoring.

    from prosefold import essay;  r = essay(engine.chat, "vaccine")   ->  r["essay_md"], r["faithful"], r["distance"] ..."""
from __future__ import annotations

import html
import os
import random
import re
import time
from pathlib import Path

from . import speaker as SP
from .engine import similarity
from .prose import ProseFoldToy

DEFAULT_VOICE = Path(__file__).resolve().parent / "voice_default.md"
MOVABLE = ("comma_density", "sent_len_std", "max_sent_len", "snap_ratio")
SECTIONS = [("What it is", ("opening", "kind", "elaboration")),
            ("How it works", ("parts", "detail", "mechanism", "cause")),
            ("Where and how it is used", ("where", "use", "example")),
            ("History and significance", ("history", "similar", "significance", "more"))]
WRAPPER = re.compile(r"\b(?:also records|I have no admitted|related term|what the record defines|I can't|I won't|I don't|"
                     r"my sources|the record says|beyond what I already)\b", re.I)
AUX = {"is", "was", "are", "were", "has", "have", "had", "can", "could", "will", "would", "may", "might", "must",
       "does", "do", "did", "should"}
PLURAL_AUX = {"are", "were", "have", "do"}
BEAM = 24


# ------------------------------------------------------------------ gathering (the speaker's plan, references kept)
INLINE = re.compile(r"(.+?[.!?])\s*\[((?:simplewiki|enwiki|openstax|wordnet|conceptnet)_[0-9a-f]{6,})\]", re.S)


def gather(topic, sid, ask):
    """the speaker's 14-question plan asked of THIS model in-process; each cited sentence keeps its record id"""
    out, seen = [], []
    for move, q in SP.QUESTIONS:
        try:
            r = ask(q % topic, sid)
        except Exception:  # noqa: BLE001
            continue
        if str(r.get("status")) != "answered":
            continue
        for m in INLINE.finditer(str(r.get("response", ""))):
            for seg in re.split(r"(?<=[.!?])\s+", m.group(1)):
                text = " ".join(html.unescape(SP.PREFIX.sub("", SP.CITE.sub("", seg).strip()).strip()).replace(" ", " ").split())
                text = re.sub(r"^\[ev:[a-z_]+\]\s*", "", text)
                if len(text) < 30 or WRAPPER.search(text) or TIMELINE.match(text) or SP.dangles(text, topic):
                    continue
                if not re.search(r"\b%s" % re.escape(topic.split()[0][:max(4, len(topic.split()[0]) - 2)]), text, re.I):
                    continue                                     # the quote rule: the sentence names its topic
                key = SP.content_words(text, frozenset())
                if any(len(key & k) >= 0.8 * max(1, min(len(key), len(k))) for k in seen):
                    continue
                seen.append(key)
                out.append({"move": move, "claim": m.group(2), "title": topic[:1].upper() + topic[1:], "source": "Wikipedia (CC BY-SA)",
                            "sentence": text if text[-1] in ".!?" else text + "."})
    return out


PAGE_STORE = Path(os.environ.get("ORACLE_WIKIPEDIA_BUILD", "/nonexistent")) / "wikipedia_specialist.sqlite3"   # full release only
ANAPHOR = re.compile(r"^(?:It|It's|Its|They|Their|Them|These|Those|This|That|Such|He|She|His|Her|Both)\b")
FOLLOWS = re.compile(r"^(?:Now|Then|Later|Today|Also|However|But|So|Instead|Still)\b")
TIMELINE = re.compile(r"^\d{3,4}\s*:")


def page_sentences(topic):
    """the topic's own page, sentence by sentence IN PAGE ORDER, each with its record id"""
    import sqlite3
    if not PAGE_STORE.exists():
        return []
    try:
        con = sqlite3.connect("file:%s?mode=ro" % PAGE_STORE, uri=True)
        key = re.sub(r"[^a-z0-9]+", "_", topic.lower()).strip("_")
        row = con.execute("select page_id from title_alias where normalized_title = ?", (key,)).fetchone()
        if not row:
            return []
        out = []
        for cid, fact in con.execute("select c0, c1 from source_rows_content where c3 = ? order by rowid", (row[0],)):
            t = " ".join(html.unescape(str(fact)).replace(" ", " ").split())
            if len(t) >= 20 and not WRAPPER.search(t) and not TIMELINE.match(t):
                out.append({"move": "page", "claim": cid, "title": topic[:1].upper() + topic[1:], "source": "Wikipedia (CC BY-SA)",
                            "sentence": t if t[-1] in ".!?" else t + "."})
        return out
    except Exception:  # noqa: BLE001
        return []


# ------------------------------------------------------------------ the moves
def topic_subject(sentence, topic):
    """-> 'it' / 'they' when the sentence's grammatical subject is the topic itself, else None ("Coffee plant is" is not)"""
    m = re.match(r"^(?:(?:A|An|The)\s+)?(%s(?:e?s)?)\s+([A-Za-z']+)" % re.escape(topic), sentence, re.I)
    if not m:
        return None
    nxt = m.group(2).lower()
    if nxt not in AUX and nxt not in VERBS and not re.match(r"^[a-z]{3,}(?:s|ed)$", nxt):
        return None
    return "they" if nxt in PLURAL_AUX else "it"


def pronominalise(sentence, topic, pron):
    return re.sub(r"^(?:(?:A|An|The)\s+)?%s(?:e?s)?\b" % re.escape(topic), pron.capitalize(), sentence, count=1, flags=re.I)


LOWER_SEEN: set = set()
OPENERS = set("""sometimes however today later earlier during after before since until unlike like many most some several few
all each every both because although though while whereas instead still even once now then also only""".split())


def lower_first(s):
    """after a join the next sentence's first word is lowercased only when it is a common word: a function word, the
    topic, or a word the record itself writes in lower case mid-sentence (so names keep their capital)"""
    w = re.sub(r"[^A-Za-z'-]", "", s.split()[0])
    if w.isupper() and len(w) > 1:
        return s
    lw = w.lower()
    common = lw in SP.FUNCTION or lw in AUX or lw in LOWER_SEEN or lw in OPENERS or (lw.endswith("ly") and len(lw) > 4)
    return s[:1].lower() + s[1:] if common else s


def options(prev_text, prev_subject_is_topic, nxt, topic):
    """the legal ways to place sentence `nxt` after `prev_text` -> [(move, new_prev_text or None, appended_text or None)]"""
    out = [("stop", None, nxt)]
    pron = topic_subject(nxt, topic)
    if pron and prev_subject_is_topic:
        p = pronominalise(nxt, topic, pron)
        out.append(("pron", None, p))
        if prev_text.endswith(".") and ";" not in prev_text:
            out.append(("and", prev_text[:-1] + ", and " + lower_first(p), None))
    if prev_text.endswith(".") and prev_text.count(";") < 1 and _related(prev_text, nxt, topic):
        out.append(("semi", prev_text[:-1] + "; " + lower_first(nxt), None))
    return out


def _related(a, b, topic):
    """a semicolon claims the two sentences belong together: they must share a content word other than the topic's own"""
    stem = topic.split()[0].lower()[:max(4, len(topic.split()[0]) - 2)]
    ka = {w.rstrip("s") for w in SP.content_words(a, frozenset()) if not w.startswith(stem) and len(w) > 3}
    kb = {w.rstrip("s") for w in SP.content_words(b, frozenset()) if not w.startswith(stem) and len(w) > 3}
    return bool(ka & kb)


# ------------------------------------------------------------------ the fold
def voice_of(text):
    return TOY.parameterize(text)


def distance(target, cand):
    """what the search minimises: ProseFold's corrections as a distance - each movable dimension's distance from the
    target, in units of the toy's own tolerance (20% of the target value, from_corpus). The HRR divergence below is
    reported too, but its scalar encoding is periodic (phase), so it is not monotonic in a parameter's error and a
    search cannot follow it (coffee 0.81 vs volcano 0.07 on similar text, 2026-10-16)."""
    d = 0.0
    for k in MOVABLE:
        scale = max(abs(target[k]) * 0.2, 1e-3)
        d += abs(cand[k] - target[k]) / scale
    return d


def divergence(target, cand):
    """ProseFold's HRR divergence on the movable dimensions only (the others are copied from the target)"""
    c = dict(target)
    for k in MOVABLE:
        c[k] = cand[k]
    return 1.0 - similarity(TOY.to_vector(target), TOY.to_vector(c))


def render(paras):
    return "\n\n".join(" ".join(s["text"] for s in p) for p in paras)


def fold_paragraph(units, topic, target, context_paras):
    """beam search over boundary moves inside one paragraph; scored on the whole essay so far"""
    first = dict(units[0], text=units[0]["sentence"], parts=[units[0]], moves=[])
    beam = [([first], 0.0, [])]
    for u in units[1:]:
        nxt_beam = []
        for sents, _, trail in beam:
            prev = sents[-1]
            prev_topic = topic_subject(prev["parts"][-1]["sentence"], topic) is not None
            for move, new_prev, appended in options(prev["text"], prev_topic, u["sentence"], topic):
                s2 = [dict(x) for x in sents]
                if new_prev is not None:
                    s2[-1] = dict(prev, text=new_prev, parts=prev["parts"] + [u], moves=prev["moves"] + [move])
                else:
                    s2.append(dict(u, text=appended, parts=[u], moves=[move] if move != "stop" else []))
                text = render(context_paras + [s2])
                nxt_beam.append((s2, distance(target, voice_of(text)), trail + [move]))
        nxt_beam.sort(key=lambda b: b[1])
        beam = nxt_beam[:BEAM]
    return beam[0]


def essay(ask, topic, voice_path=DEFAULT_VOICE, sid=None):
    global TOY
    TOY = ProseFoldToy.from_corpus(Path(voice_path).read_text(encoding="utf-8"))
    t0 = time.time()
    corpus = Path(voice_path).read_text(encoding="utf-8")
    target = voice_of(corpus)
    plan = gather(topic, sid or "prosefold-%s-%d" % (re.sub(r"\W+", "", topic)[:16], int(t0)), ask)
    page = page_sentences(topic)
    seen = [SP.content_words(c["sentence"], frozenset()) for c in page]
    related = []
    for c in plan:                                          # the plan's answers that the page does not already say
        k = SP.content_words(c["sentence"], frozenset())
        if not any(len(k & x) >= 0.8 * max(1, min(len(k), len(x))) for x in seen):
            seen.append(k)
            related.append(c)
    if not page:                                            # no page of its own: the plan's answers, with no anaphora
        page, related = [c for c in related if not ANAPHOR.match(c["sentence"])], []
    claims = page + related
    for c in claims:
        for w in re.findall(r"(?<=\s)([a-z][a-z'-]+)", c["sentence"]):
            LOWER_SEEN.add(w)
    groups, cur = [], []
    for c in page:                                          # paragraphs of 3-6, cut only before a sentence that stands alone
        stands_alone = not ANAPHOR.match(c["sentence"]) and not FOLLOWS.match(c["sentence"])
        if cur and len(cur) >= 3 and stands_alone:
            groups.append(("", cur))
            cur = []
        cur.append(c)
    if cur:
        groups.append(("", cur))
    if related:
        groups.append(("From related records", [c for c in related if not ANAPHOR.match(c["sentence"])]))
    paras, titles, trail = [], [], []
    for title, units in groups:
        if not units:
            continue
        best, _, tr = fold_paragraph(units, topic, target, paras)
        paras.append(best)
        titles.append(title)
        trail += tr
    # fidelity: every composed sentence carries the content of its parts and nothing else
    faithful, bad = 0, []
    n_sent = 0
    for p in paras:
        for s in p:
            n_sent += 1
            ok, extra = SP.decomposes(s["text"], [x["sentence"] for x in s["parts"]], VERBS)
            faithful += ok
            if not ok:
                bad.append({"text": s["text"], "extra": extra})
    # citations: one number per source claim, in order of first use
    order = []
    for p in paras:
        for s in p:
            for x in s["parts"]:
                if x["claim"] not in order:
                    order.append(x["claim"])
    num = {c: i + 1 for i, c in enumerate(order)}
    body = []
    for title, p in zip(titles, paras):
        text = " ".join("%s [%s]" % (s["text"], ",".join(str(num[x["claim"]]) for x in s["parts"])) for s in p)
        body.append(("## %s\n\n" % title if title else "") + text)
    ref_of = {c["claim"]: c for c in claims}
    refs = ["%d. %s - %s (%s)" % (num[c], ref_of[c].get("title") or topic, ref_of[c].get("source") or "", c) for c in order]
    plain = render(paras)
    echo = "\n\n".join(" ".join(u["sentence"] for u in units) for _, units in groups if units)
    v_fold, v_echo = voice_of(plain), voice_of(echo)
    moves_used = {m: trail.count(m) for m in ("stop", "pron", "and", "semi")}
    # instrument checks: the search must beat RANDOM legal choices (else the fold is not doing the work), and the
    # fidelity check must catch a planted word change (else "faithful" means nothing)
    rnd = []
    for seed in range(5):
        rng, rp = random.Random(seed), []
        for _, units in groups:
            if not units:
                continue
            sents = [dict(units[0], text=units[0]["sentence"], parts=[units[0]], moves=[])]
            for u in units[1:]:
                prev = sents[-1]
                opts = options(prev["text"], topic_subject(prev["parts"][-1]["sentence"], topic) is not None, u["sentence"], topic)
                move, new_prev, appended = rng.choice(opts)
                if new_prev is not None:
                    sents[-1] = dict(prev, text=new_prev, parts=prev["parts"] + [u])
                else:
                    sents.append(dict(u, text=appended, parts=[u]))
            rp.append(sents)
        rnd.append(distance(target, voice_of(render(rp))))
    planted = None
    for p_ in paras:
        for s_ in p_:
            words = s_["text"].split()
            if len(words) > 6:
                bad_text = " ".join(words[:3] + ["purple"] + words[3:])
                planted = not SP.decomposes(bad_text, [x["sentence"] for x in s_["parts"]], VERBS)[0]
                break
        if planted is not None:
            break
    return {
        "topic": topic, "ts": time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime()), "seconds": round(time.time() - t0, 1),
        "voice_corpus": str(voice_path), "claims_seen": len(claims), "sentences": n_sent, "paragraphs": len(paras),
        "faithful": faithful, "unfaithful": bad, "moves": moves_used,
        "distance": {"fold": round(distance(target, v_fold), 3), "echo": round(distance(target, v_echo), 3),
                     "random_mean": round(sum(rnd) / len(rnd), 3)},
        "planted_change_caught": planted,
        "hrr_divergence": {"fold": round(divergence(target, v_fold), 5), "echo": round(divergence(target, v_echo), 5)},
        "voice": {"target": {k: target[k] for k in MOVABLE}, "fold": {k: v_fold[k] for k in MOVABLE}, "echo": {k: v_echo[k] for k in MOVABLE}},
        "fixed_by_the_record": {k: v_fold[k] for k in v_fold if k not in MOVABLE},
        "residual_corrections": TOY.corrections(target, v_fold),
        "essay_md": "# %s\n\n%s\n\n### Sources\n\n%s\n" % (topic[:1].upper() + topic[1:], "\n\n".join(body), "\n".join(refs)),
        "lm_calls": 0, "gradient_steps": 0,
    }



VERBS = frozenset()
TOY = None
