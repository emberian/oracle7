"""speaker - the evidence-bound speaker's helpers that ProseFold uses, copied verbatim from oracle_speak_v3 (2026-09-07):
the 14-question plan, the citation and prefix patterns, the dangling-reference test and the fidelity check (a composed
sentence must carry the content words of its cited parts and nothing else). No language model; nothing here generates."""
import re

FUNCTION = set("""a an the this that these those his her its their our your my
is was are were be been being am s
has have had does do did
of in on at to for from by with as into over under about through between within near around out up off across along
and or but so because if then than while although though yet nor when where which who whom whose what
not no also only one two three both either neither each every all some any many most much few several
it he she they we you them him us me i there here now today
first second third last other another such same very often usually generally typically mainly mostly
more less least much many own new old
, . ; : ( ) ' " - -- ? !""".split())
PUNCT = set(',.;:()"\'-?!')
WORD = re.compile(r"[A-Za-z']+")
TOKRE = re.compile(r"[A-Za-z']+|[.,;:!?()\"]")
def toks(s):
    return TOKRE.findall(str(s))


def content_words(s, verbs):
    return {w.lower() for w in WORD.findall(str(s)) if w.lower() not in FUNCTION and w.lower() not in verbs and len(w) > 1}

CITE = re.compile(r"\s*\[(?:simplewiki|enwiki|wordnet|openstax|conceptnet|self)[a-z_0-9:]*[^\]]*\]")
REF_N = re.compile(r"\[(\d+)\]")
CITED = re.compile(r"(.+?[.!?])\s*\[(\d+)\]", re.S)
PREFIX = re.compile(r"^(?:according to [^,]{1,60}, |the page for [^:]{1,60} records: |[^:]{1,60} also records: |beyond what i already told you on [^:]{1,60}: |"
                    r"[a-z][^:]{1,40} notes that |as [^,]{1,40} has it, |from [^:]{1,40}: |the record states:? |\[ev:[a-z_]+\]\s*)", re.I)
# A sentence that opens by pointing BACK cannot be moved. "That is called conservation of mass" was true on the
# page where the preceding sentence said what "that" was, and says nothing here. Demonstratives and discourse
# connectives bind to a specific preceding proposition, which reordering destroys; personal pronouns bind to the
# paragraph subject, which the opening definition always supplies, so those are left alone.
# a bare demonstrative followed by a verb points at a proposition, not at a thing
DEMONSTRATIVE_BARE = re.compile(r"^(?:that|this|these|those|such|both|either|neither)\s+"
                                r"(?:is|are|was|were|has|have|had|will|would|can|could|may|might|does|do|did|"
                                r"means|refers|makes|made|becomes|became|happens|happened|occurs|occurred)\b", re.I)
# a demonstrative introducing a noun: safe only when the noun restates the subject
DEMONSTRATIVE_NP = re.compile(r"^(?:this|these|those|that|such|both)\s+([a-z][a-z-]{2,})", re.I)
# a connective asserts a relation to something that is no longer in front of it
CONNECTIVE = re.compile(r"^(?:as a result|as such|therefore|thus|hence|however|instead|otherwise|meanwhile|"
                        r"afterwards|afterward|consequently|for this reason|in this case|in that case|"
                        r"on the other hand|by contrast|in contrast|for that reason|because of this|"
                        r"despite this|even so|nonetheless|nevertheless)\b", re.I)
# nouns a page uses to mean "the thing this page is about"
SUBJECT_NOUNS = {'species', 'animal', 'animals', 'plant', 'plants', 'group', 'groups', 'kind', 'kinds', 'type',
                 'types', 'process', 'processes', 'device', 'devices', 'machine', 'machines', 'system', 'systems',
                 'term', 'terms', 'word', 'words', 'name', 'names', 'creature', 'creatures', 'object', 'objects',
                 'material', 'materials', 'substance', 'substances', 'form', 'forms', 'structure', 'structures'}


def dangles(text, topic=''):
    """does this sentence open by pointing at something the new paragraph does not supply?"""
    if CONNECTIVE.match(text) or DEMONSTRATIVE_BARE.match(text):
        return True
    m = DEMONSTRATIVE_NP.match(text)
    if m:
        noun = m.group(1).lower()
        topic_words = {w.lower() for w in re.findall(r"[A-Za-z]{3,}", str(topic or ''))}
        topic_words |= {w.rstrip('s') for w in set(topic_words)}
        return not (noun in SUBJECT_NOUNS or noun in topic_words or noun.rstrip('s') in topic_words)
    return False

# The plan IS the ceiling on the paragraph: the speaker can only say what one of these answers cited.
# Measured over 8 topics: 5 questions surface 4.0 on-topic sentences each, these 15 surface 7.9.
QUESTIONS = [('opening', 'What is a %s?'),
             ('kind', 'What kind of thing is a %s?'),
             ('elaboration', 'Tell me about %s.'),
             ('parts', 'What are the parts of a %s?'),
             ('detail', 'What is %s made of?'),
             ('where', 'Where is %s found?'),
             ('use', 'What is %s used for?'),
             ('mechanism', 'How does a %s work?'),
             ('cause', 'What causes %s?'),
             ('history', 'Give me the history of %s.'),
             ('example', 'What is an example of a %s?'),
             ('similar', 'What is %s similar to?'),
             ('significance', 'Why does %s matter?'),
             ('more', 'What else does the record say about %s?')]


def decomposes(composed, parts, verbs):
    """a composed sentence must carry the content of its parts and nothing else"""
    have = content_words(composed, verbs)
    want = set()
    for p in parts:
        want |= content_words(p, verbs)
    return have <= want, sorted(have - want)[:5]



