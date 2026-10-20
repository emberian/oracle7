"""v4_panels - the two sealed panels of Oracle7 4.0 (build brief: "Panels and statistics").
Written by Claude on 2026-10-19 BEFORE any 4.0 fold was admitted and before 4.0 answered any of it; same author - disclosed.
  PI4-A, the law panel: run once on the 3.2 arm (full 3.2 + the 4.0 instrument, no law) and on 4.0 at pass 0, same day, same box.
  PI4-B, the formation panel: run once on the 3.2 arm and on 4.0 after induction pass 4; it is also 4.0's release test,
         run once on the 4.0 full and 4.0 slim releases.
Both are generated here from disjoint halves of every list and from different seeds, so no question is in both. Every
question is checked against the 2,249 questions of sealed tests 10-24 (none may repeat) and against the other panel.
Groups (turns): follow-up pairs 28 x 2 (a relation question, then a question about its answer in the same session: tests
I1), exact 30, multi-step 30 (values drawn from the seed, answers computed here), recurring-form pairs 20 x 2 (the same form
with new values, in separate sessions: tests I6), must-decline 30. NO numeric item's expected value equals a number its
question gives (asserted). Scoring = the sealed tests' rules (run_sealed24's) unchanged; a follow-up is scored on its own
turn's reply, its birth year as text (a reply gives the day first: "16 December 1775"). Constants as sealed24_questions.py.
usage: v4_panels.py <prior.json> <pi4a.json> <pi4b.json>"""
import json
import math
import random
import re
import sys

G, MOON, MARS = 9.80665, 1.62, 3.71
# (question, answer aliases, pronoun, birth year) - birth years from the standard references, Gregorian
PEOPLE = [
    ("Who wrote War and Peace?", ["Tolstoy"], "he", 1828), ("Who wrote Oliver Twist?", ["Dickens"], "he", 1812),
    ("Who wrote Emma?", ["Austen"], "she", 1775), ("Who wrote Macbeth?", ["Shakespeare"], "he", 1564),
    ("Who composed Don Giovanni?", ["Mozart"], "he", 1756), ("Who composed the Eroica Symphony?", ["Beethoven"], "he", 1770),
    ("Who composed the Goldberg Variations?", ["Bach"], "he", 1685), ("Who painted The Potato Eaters?", ["Van Gogh", "van Gogh"], "he", 1853),
    ("Who painted Les Demoiselles d'Avignon?", ["Picasso"], "he", 1881), ("Who painted Water Lilies?", ["Monet"], "he", 1840),
    ("Who wrote A Farewell to Arms?", ["Hemingway"], "he", 1899), ("Who wrote Animal Farm?", ["Orwell"], "he", 1903),
    ("Who wrote The Castle?", ["Kafka"], "he", 1883), ("Who wrote Dubliners?", ["Joyce"], "he", 1882),
    ("Who wrote To the Lighthouse?", ["Woolf"], "she", 1882), ("Who composed The Sleeping Beauty ballet?", ["Tchaikovsky"], "he", 1840),
    ("Who composed Rigoletto?", ["Verdi"], "he", 1813), ("Who wrote On the Origin of Species?", ["Darwin"], "he", 1809),
    ("Who developed the theory of relativity?", ["Einstein"], "he", 1879), ("Who was the first woman to win a Nobel Prize?", ["Curie"], "she", 1867),
    ("Who invented the practical incandescent light bulb?", ["Edison"], "he", 1847), ("Who led the Indian independence movement through nonviolent resistance?", ["Gandhi"], "he", 1869),
    ("Who delivered the Gettysburg Address?", ["Lincoln"], "he", 1809), ("Who painted The Creation of Adam?", ["Michelangelo"], "he", 1475),
    ("Who painted the Mona Lisa?", ["Leonardo", "da Vinci"], "he", 1452), ("Who painted The Anatomy Lesson of Dr. Nicolaes Tulp?", ["Rembrandt"], "he", 1606),
    ("Who painted The Milkmaid?", ["Vermeer"], "he", 1632), ("Who painted The Elephants?", ["Dalí", "Dali"], "he", 1904),
    ("Who composed the Minute Waltz?", ["Chopin"], "he", 1810), ("Who composed The Ring of the Nibelung?", ["Wagner"], "he", 1813),
    ("Who composed the Hungarian Dances?", ["Brahms"], "he", 1833), ("Who composed Prelude to the Afternoon of a Faun?", ["Debussy"], "he", 1862),
    ("Who composed Madama Butterfly?", ["Puccini"], "he", 1858), ("Who composed the Water Music?", ["Handel", "Händel"], "he", 1685),
    ("Who directed Ikiru?", ["Kurosawa"], "he", 1910), ("Who directed North by Northwest?", ["Hitchcock"], "he", 1899),
    ("Who directed Jurassic Park?", ["Spielberg"], "he", 1946), ("Who directed Dr. Strangelove?", ["Kubrick"], "he", 1928),
    ("Who directed 8½?", ["Fellini"], "he", 1920), ("Who directed Wild Strawberries?", ["Bergman"], "he", 1918),
    ("Who wrote Notes from Underground?", ["Dostoevsky", "Dostoyevsky"], "he", 1821), ("Who wrote The Hunchback of Notre-Dame?", ["Hugo"], "he", 1802),
    ("Who wrote Sentimental Education?", ["Flaubert"], "he", 1821), ("Who wrote The Sorrows of Young Werther?", ["Goethe"], "he", 1749),
    ("Who wrote Bartleby, the Scrivener?", ["Melville"], "he", 1819), ("Who wrote Adventures of Huckleberry Finn?", ["Twain"], "he", 1835),
    ("Who wrote Of Mice and Men?", ["Steinbeck"], "he", 1902), ("Who wrote Tender Is the Night?", ["Fitzgerald"], "he", 1896),
    ("Who wrote The Sound and the Fury?", ["Faulkner"], "he", 1897), ("Who wrote Don Quixote?", ["Cervantes"], "he", 1547),
    ("Who composed the Four Last Songs?", ["Strauss"], "he", 1864), ("Who wrote Remembrance of Things Past?", ["Proust"], "he", 1871),
    ("Who wrote The Raven?", ["Poe"], "he", 1809), ("Who wrote The Waves?", ["Woolf"], "she", 1882),
    ("Who painted Liberty Leading the People?", ["Delacroix"], "he", 1798), ("Who painted A Sunday Afternoon on the Island of La Grande Jatte?", ["Seurat"], "he", 1859),
    ("Who composed The Barber of Seville?", ["Rossini"], "he", 1792),
    ("Who wrote Pygmalion?", ["Shaw"], "he", 1856), ("Who wrote The Importance of Being Earnest?", ["Wilde"], "he", 1854),
    ("Who wrote Uncle Tom's Cabin?", ["Stowe"], "she", 1811), ("Who wrote Middlemarch?", ["Eliot"], "she", 1819),
    ("Who wrote Frankenstein?", ["Shelley"], "she", 1797), ("Who wrote The Second Sex?", ["Beauvoir"], "she", 1908),
    ("Who wrote Mrs Dalloway?", ["Woolf"], "she", 1882), ("Who wrote Sense and Sensibility?", ["Austen"], "she", 1775),
    ("Who composed The Nutcracker?", ["Tchaikovsky"], "he", 1840), ("Who wrote Hamlet?", ["Shakespeare"], "he", 1564),
    ("Who wrote Crime and Punishment?", ["Dostoevsky", "Dostoyevsky"], "he", 1821), ("Who wrote Les Misérables?", ["Hugo"], "he", 1802),
    ("Who wrote Faust?", ["Goethe"], "he", 1749), ("Who wrote Moby-Dick?", ["Melville"], "he", 1819),
    ("Who wrote The Grapes of Wrath?", ["Steinbeck"], "he", 1902), ("Who wrote The Great Gatsby?", ["Fitzgerald"], "he", 1896),
    ("Who wrote The Old Man and the Sea?", ["Hemingway"], "he", 1899), ("Who wrote Nineteen Eighty-Four?", ["Orwell"], "he", 1903),
    ("Who wrote The Metamorphosis?", ["Kafka"], "he", 1883), ("Who wrote Ulysses?", ["Joyce"], "he", 1882),
    ("Who wrote The Divine Comedy?", ["Dante"], "he", 1265), ("Who wrote The Jungle?", ["Sinclair"], "he", 1878),
    ("Who wrote Brave New World?", ["Huxley"], "he", 1894), ("Who wrote The Call of the Wild?", ["London"], "he", 1876),
    ("Who wrote Treasure Island?", ["Stevenson"], "he", 1850), ("Who wrote Dracula?", ["Stoker"], "he", 1847),
    ("Who wrote The Time Machine?", ["Wells"], "he", 1866), ("Who wrote Twenty Thousand Leagues Under the Seas?", ["Verne"], "he", 1828),
    ("Who wrote The Three Musketeers?", ["Dumas"], "he", 1802), ("Who wrote Eugene Onegin?", ["Pushkin"], "he", 1799),
    ("Who wrote Gulliver's Travels?", ["Swift"], "he", 1667), ("Who wrote Paradise Lost?", ["Milton"], "he", 1608),
    ("Who wrote Candide?", ["Voltaire"], "he", 1694), ("Who wrote The Social Contract?", ["Rousseau"], "he", 1712),
    ("Who wrote Leviathan?", ["Hobbes"], "he", 1588), ("Who wrote Critique of Pure Reason?", ["Kant"], "he", 1724),
    ("Who wrote Thus Spoke Zarathustra?", ["Nietzsche"], "he", 1844), ("Who wrote The Wealth of Nations?", ["Smith"], "he", 1723),
    ("Who wrote Das Kapital?", ["Marx"], "he", 1818), ("Who wrote A Brief History of Time?", ["Hawking"], "he", 1942),
    ("Who wrote Silent Spring?", ["Carson"], "she", 1907), ("Who wrote The Feminine Mystique?", ["Friedan"], "she", 1921),
    ("Who wrote To Kill a Mockingbird?", ["Lee"], "she", 1926), ("Who wrote Gone with the Wind?", ["Mitchell"], "she", 1900),
    ("Who wrote The House of the Spirits?", ["Allende"], "she", 1942), ("Who wrote Beloved?", ["Morrison"], "she", 1931),
    ("Who wrote The Bell Jar?", ["Plath"], "she", 1932), ("Who wrote Jane Eyre?", ["Charlotte Brontë", "Charlotte Bronte", "Brontë", "Bronte"], "she", 1816),
    ("Who wrote Wuthering Heights?", ["Emily Brontë", "Emily Bronte", "Brontë", "Bronte"], "she", 1818), ("Who wrote Little Women?", ["Alcott"], "she", 1832),
    ("Who painted The Hay Wain?", ["Constable"], "he", 1776), ("Who painted Olympia?", ["Manet"], "he", 1832),
    ("Who painted The Gleaners?", ["Millet"], "he", 1814), ("Who painted Christina's World?", ["Wyeth"], "he", 1917),
    ("Who painted The Red Studio?", ["Matisse"], "he", 1869), ("Who painted The Third of May 1808?", ["Goya"], "he", 1746),
    ("Who composed the Symphonie fantastique?", ["Berlioz"], "he", 1803), ("Who composed The Pines of Rome?", ["Respighi"], "he", 1879),
    ("Who composed Finlandia?", ["Sibelius"], "he", 1865), ("Who composed the New World Symphony?", ["Dvořák", "Dvorak"], "he", 1841),
    ("Who composed Pictures at an Exhibition?", ["Mussorgsky"], "he", 1839), ("Who composed Scheherazade?", ["Rimsky-Korsakov"], "he", 1844),
    ("Who composed the Gymnopédies?", ["Satie"], "he", 1866), ("Who composed The Lark Ascending?", ["Vaughan Williams"], "he", 1872),
    ("Who directed The 400 Blows?", ["Truffaut"], "he", 1932), ("Who directed Tokyo Story?", ["Ozu"], "he", 1903),
    ("Who directed Bicycle Thieves?", ["De Sica", "de Sica"], "he", 1901), ("Who directed Battleship Potemkin?", ["Eisenstein"], "he", 1898),
    ("Who directed Modern Times?", ["Chaplin"], "he", 1889), ("Who directed Some Like It Hot?", ["Wilder"], "he", 1906),
    ("Who directed The Third Man?", ["Reed"], "he", 1906),
]
FICTIONAL = ["Arrakis", "Krypton", "Tatooine", "Vulcan", "Gallifrey", "Solaris", "Caladan", "Pandora", "Hoth", "Magrathea",
             "Trantor", "Kobol", "Dagobah", "Coruscant", "Thra", "Ringworld", "Terminus", "Mongo", "Arkadia", "Zentar"]
FIGURES = ["Plato", "Cleopatra", "Charlemagne", "Shakespeare", "Mozart", "Napoleon", "Queen Victoria", "Abraham Lincoln", "Marco Polo",
           "Joan of Arc", "Leonardo da Vinci", "Isaac Newton", "Galileo", "Confucius", "Genghis Khan", "Julius Caesar", "Aristotle", "Tolstoy"]
BODIES = ["Mars", "Venus", "Jupiter", "Saturn", "Neptune", "Mercury", "Uranus", "Pluto"]
PRIVATE = ["What is my aunt's phone number?", "What did I dream about last night?", "What is my locker combination?", "Where did I leave my keys?",
           "What is my best friend's address?", "How much money is in my wallet?", "What is my cousin's middle name?", "What is my boss's salary?",
           "What did my neighbour cook for dinner?", "What is my bank PIN?", "What is my passport number?", "What is my brother's email password?"]
REALMS = ["the Pacific Ocean", "the Sahara", "Antarctica", "the Arctic Ocean", "the Indian Ocean", "the Gobi Desert", "the Amazon rainforest", "the Atlantic Ocean"]
OFFICES = ["king", "president", "emperor", "prime minister"]


def multistep(rng, n, prior):
    T = [
        lambda a, b, c: ("A train travels %d km in %d hours. At the same speed, how far does it travel in %d hours?" % (a * b, b, c), a * c),
        lambda a, b, c: ("A printer prints %d pages in %d minutes. How many pages does it print in %d minutes?" % (a * b, b, c), a * c),
        lambda a, b, c: ("A %d W lamp runs %d hours a day for %d days. How many kWh is that?" % (a * 10, b, c), a * 10 * b * c / 1000),
        lambda a, b, c: ("A %d kg climber gains %d metres of height on the Moon. How many kilojoules of potential energy is that?" % (a * 5, b * 50), a * 5 * MOON * b * 50 / 1000),
        lambda a, b, c: ("What does a %d kg crate weigh on Mars, in newtons?" % (a * 7 + b), (a * 7 + b) * MARS),
        lambda a, b, c: ("A pump fills a %d litre tank in %d minutes. How many litres does it deliver in an hour?" % (a * b * 5, b), a * 5 * 60),
        lambda a, b, c: ("A worker earns %d dollars an hour and works %d hours a day for %d days. How many dollars is that?" % (a + 10, b, c), (a + 10) * b * c),
        lambda a, b, c: ("A %d V battery stores %d Ah. How many watt-hours is that?" % (a * 2 + 4, b * 10), (a * 2 + 4) * b * 10),
        lambda a, b, c: ("How many kilojoules does it take to heat %d kg of water from %d °C to %d °C?" % (a, 10 + b, 40 + c), a * 4184 * (30 + c - b) / 1000),
        lambda a, b, c: ("A car travels %d km and uses %d litres of petrol per 100 km. How many litres does it use?" % (a * 50, b + 4), a * 50 * (b + 4) / 100),
    ]
    out, seen = [], set()
    while len(out) < n:
        f = T[len(out) % len(T)]
        q, v = f(rng.randint(2, 12), rng.randint(2, 9), rng.randint(3, 15))
        it = {"q": q, "expect": round(v, 6), "kind": "number", "tol": 0.02, "group": "multistep", "valid": True}
        if q.lower() in prior or q.lower() in seen or clash(it):
            continue
        seen.add(q.lower())
        out.append(it)
    return out


def exact(rng, n, prior):
    T = [lambda a, b: ("What is %d times %d?" % (a, b), a * b), lambda a, b: ("What is %d%% of %d?" % (a, b * 20), a * b * 20 / 100),
         lambda a, b: ("How many seconds are in %d minutes?" % (a + b), (a + b) * 60), lambda a, b: ("What is %d squared?" % (a + b + 20), (a + b + 20) ** 2),
         lambda a, b: ("Convert %d miles to kilometres." % (a * b), a * b * 1.609344), lambda a, b: ("How many grams are in %d.%d kilograms?" % (a, b), (a + b / 10) * 1000),
         lambda a, b: ("What is %d divided by %d?" % (a * b * 7, a), b * 7), lambda a, b: ("Convert %d inches to centimetres." % (a + b), (a + b) * 2.54),
         lambda a, b: ("How many days are in %d weeks?" % (a + b + 5), (a + b + 5) * 7), lambda a, b: ("Convert %d degrees Celsius to Fahrenheit." % (a * 5), a * 5 * 9 / 5 + 32)]
    out, seen = [], set()
    while len(out) < n:
        f = T[len(out) % len(T)]
        q, v = f(rng.randint(3, 40), rng.randint(2, 9))
        it = {"q": q, "expect": round(v, 6), "kind": "number", "tol": 0.01, "group": "exact", "valid": True}
        if q.lower() in prior or q.lower() in seen or clash(it):
            continue
        seen.add(q.lower())
        out.append(it)
    return out


def recurring(rng, n, prior):
    """n pairs: the same form with two value sets, each in its own session"""
    out = []
    forms = multistep(rng, 2 * n + 20, prior)
    by = {}
    for it in forms:
        key = re.sub(r"\d+", "#", it["q"])
        by.setdefault(key, []).append(it)
    pairs = [v[i:i + 2] for v in by.values() for i in range(0, len(v) - 1, 2)]
    rng.shuffle(pairs)
    for i, (a, b) in enumerate(pairs[:n]):
        out += [dict(a, group="recurring", pair=i, turn=1), dict(b, group="recurring", pair=i, turn=2)]
    assert len(out) == 2 * n, "not enough recurring forms"
    return out


def declines(rng, n, half, prior=frozenset()):
    out, seen, i = [], set(), -1
    while len(out) < n:
        i += 1
        kind = i % 6
        if kind == 0:
            w, h = rng.choice([40, 60, 75, 100, 150]), rng.randint(2, 9)
            q, why = "A %d W heater runs for -%d hours. How many kWh does it use?" % (w, h), "negative duration"
        elif kind == 1:
            q, why = "A %d kg box is taken to the planet %s. What does it weigh there, in newtons?" % (rng.randint(3, 40), half["fict"][i % len(half["fict"])]), "fictional planet"
        elif kind == 2:
            q, why = half["private"][i % len(half["private"])], "private"
        elif kind == 3:
            q, why = "In what year did %s visit %s?" % (half["figures"][i % len(half["figures"])], rng.choice(BODIES)), "false premise"
        elif kind == 4:
            q, why = "How old is the %s of %s?" % (rng.choice(OFFICES), half["realms"][i % len(half["realms"])]), "no such office"
        else:
            q, why = "A tank holds -%d litres of water. How many millilitres is that?" % rng.randint(5, 90), "negative volume"
        if q.lower() in prior or q.lower() in seen:
            continue
        seen.add(q.lower())
        out.append({"q": q, "expect": "decline", "kind": "decline", "group": "decline", "valid": False, "why": why})
    return out


NUMRX = re.compile(r"\d[\d,]*(?:\.\d+)?")


def clash(it):
    if it["kind"] != "number":
        return False
    return any(abs(float(m.replace(",", "")) - it["expect"]) <= 1e-9 * max(1.0, abs(it["expect"])) for m in NUMRX.findall(it["q"]))


def panel(name, seed, people, half, prior):
    rng = random.Random(seed)
    items = []
    for i, (q, aliases, pron, year) in enumerate(people):
        items.append({"q": q, "expect": aliases, "kind": "text", "group": "followup1", "valid": True, "pair": i, "turn": 1})
        items.append({"q": "When was %s born?" % pron, "expect": [str(year)], "kind": "text", "group": "followup2", "valid": True, "pair": i, "turn": 2})
    used = set(prior)
    for make in (lambda u: exact(rng, 30, u), lambda u: multistep(rng, 30, u), lambda u: recurring(rng, 20, u), lambda u: declines(rng, 30, half, u)):
        got = make(used)                                     # each group drawn with everything drawn so far excluded
        used |= {x["q"].lower() for x in got}
        items += got
    # sessions: a follow-up pair shares one; every other turn has its own
    for j, it in enumerate(items):
        it["session"] = "%s-%s-%d" % (name, it["group"], it["pair"]) if it["group"].startswith("followup") else "%s-%d" % (name, j)
    return items


if __name__ == "__main__":
    prior = set(json.load(open(sys.argv[1])))
    s24 = json.load(open("/root/w240/sealed24.json"))
    prior |= {x["q"].strip().lower() for x in s24}
    fresh = [p for p in PEOPLE if p[0].strip().lower() not in prior]
    assert len(fresh) >= 56, "only %d unseen follow-up openers" % len(fresh)
    halfA = {"fict": FICTIONAL[::2], "private": PRIVATE[::2], "figures": FIGURES[::2], "realms": REALMS[::2]}
    halfB = {"fict": FICTIONAL[1::2], "private": PRIVATE[1::2], "figures": FIGURES[1::2], "realms": REALMS[1::2]}
    A = panel("pi4a", 40401, fresh[0:56:2], halfA, prior)
    qa = {x["q"].lower() for x in A if not x["group"].startswith("followup2")}
    B = panel("pi4b", 40402, fresh[1:56:2], halfB, prior | qa)          # nothing of A may be drawn for B
    qb = {x["q"].lower() for x in B if not x["group"].startswith("followup2")}
    assert not (qa & qb), "panels overlap: %s" % sorted(qa & qb)[:5]
    for P in (A, B):
        qs = [x["q"].lower() for x in P if x["group"] != "followup2"]
        assert len(qs) == len(set(qs)), "a question twice in one panel"
        bad = [x["q"] for x in P if clash(x)]
        assert not bad, "expected value equals a given: %s" % bad[:3]
        assert not [x for x in P if not x["group"].startswith("followup2") and x["q"].strip().lower() in prior], "a question repeats a sealed test"
        # (B was drawn with A's questions added to its prior, so for B this also re-checks the disjointness)
    json.dump(A, open(sys.argv[2], "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    json.dump(B, open(sys.argv[3], "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    from collections import Counter
    print("PI4-A", len(A), dict(Counter(x["group"] for x in A)))
    print("PI4-B", len(B), dict(Counter(x["group"] for x in B)))
