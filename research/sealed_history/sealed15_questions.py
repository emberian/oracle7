"""sealed15_questions - SEALED TEST 15: the test that decides whether PATH MEMORY ships (Ben 2026-10-13: "we want all that in
the release"). Written by Claude on 2026-10-13 BEFORE any path-memory code existed and before head w534 answered any of it;
same author as the folds - disclosed. Two parts, run ONCE on each arm (A = the fixed-routing head w534, B = the same head
with path memory w535), nothing else changed between the arms:
  SINGLE    150 questions, the recipe and group sizes of tests 12-14 (knowledge 70 incl. 12 without a question mark,
            exact 30, multistep 20, decline 30); scoring = run_sealed14's rules unchanged.
  DIALOGUES 20 conversations, the recipe of conversation test 2 (hand-offs between specialists, two-part turns, chained
            and follow-up calculations, declines inside a conversation); scoring = run_conv_v1's rules unchanged.
PASS for path memory (fixed here): on SINGLE, arm B's precision on answered >= arm A's, false yes B <= A, right B > A; on
DIALOGUES, precision B >= A and false yes B <= A. Otherwise path memory does not ship, and the result is published.
The release candidate then replays SINGLE (invariance: zero differences from the shipped arm, as RC12 carried test 11).
Answer keys avoid the two key errors found in test 13 (calendar-dependent dates; an answer equal to a given number)."""
import json
import math
import re
import sys

E, M, K, D = "exact", "multistep", "knowledge", "decline"
N = lambda q, v, tol=0.01, g=E: {"q": q, "expect": v, "kind": "number", "tol": tol, "group": g, "valid": True}
T = lambda q, aliases, g=K: {"q": q, "expect": aliases, "kind": "text", "group": g, "valid": True}
X = lambda q, why: {"q": q, "expect": "decline", "kind": "decline", "group": D, "valid": False, "why": why}
F = lambda q, aliases: {"kind": "fact", "q": q, "expect": aliases}
U = lambda q, aliases: {"kind": "follow", "q": q, "expect": aliases}
MU = lambda q, groups: {"kind": "multi", "q": q, "expect": groups}
NU = lambda q, v, tol=0.01: {"kind": "number", "q": q, "expect": v, "tol": tol}
DE = lambda q, why: {"kind": "decline", "q": q, "expect": "decline", "why": why}
SO = lambda q: {"kind": "social", "q": q, "expect": "social"}
G = 9.80665

ITEMS = [
    # ---- knowledge (70)
    T("Who wrote The Tale of Genji?", ["Murasaki"]),
    T("Who wrote The Overcoat?", ["Gogol"]),
    T("Who wrote Hedda Gabler?", ["Ibsen"]),
    T("Who wrote Uncle Vanya?", ["Chekhov"]),
    T("Who wrote Les Fleurs du mal?", ["Baudelaire"]),
    T("Who wrote The Prince?", ["Machiavelli"]),
    T("Who wrote Candide?", ["Voltaire"]),
    T("Who is the author of The Little Prince?", ["Saint-Exupéry", "Saint-Exupery"]),
    T("Who is the author of Steppenwolf?", ["Hesse"]),
    T("Who is the author of The Name of the Wind?", ["Rothfuss"]),
    T("Who painted Flatford Mill?", ["Constable"]),
    T("Who painted Automat?", ["Hopper"]),
    T("Who painted Daughters of Revolution?", ["Grant Wood"]),
    T("Who painted The Sleeping Gypsy?", ["Rousseau"]),
    T("Who painted The Sick Child?", ["Munch"]),
    T("Who composed the opera Il trovatore?", ["Verdi"]),
    T("Who composed the opera Turandot?", ["Puccini"]),
    T("Who composed the opera Norma?", ["Bellini"]),
    T("Who composed the ballet Giselle?", ["Adolphe Adam", "Adam"]),
    T("Who composed the Holberg Suite?", ["Grieg"]),
    T("What is the capital of Botswana?", ["Gaborone"]),
    T("What is the capital of Belarus?", ["Minsk"]),
    T("What is the capital of Oman?", ["Muscat"]),
    T("What is the capital of Nicaragua?", ["Managua"]),
    T("What is the capital of Kazakhstan?", ["Astana"]),
    T("Which city is the capital of Mozambique?", ["Maputo"]),
    T("Which city is the capital of Cuba?", ["Havana"]),
    T("What is the currency of Albania?", ["lek"]),
    T("What is the currency of Cambodia?", ["riel"]),
    T("What is the currency of Nigeria?", ["naira"]),
    T("What is the official language of Andorra?", ["Catalan"]),
    T("What is the official language of Uruguay?", ["Spanish"]),
    T("On which continent is Laos?", ["Asia"]),
    T("Which country is the city of Kaunas in?", ["Lithuania"]),
    T("Which country is the city of Graz in?", ["Austria"]),
    T("Who directed La Dolce Vita?", ["Fellini"]),
    T("Who directed The 400 Blows?", ["Truffaut"]),
    T("Who directed Pierrot le Fou?", ["Godard"]),
    T("Who directed Tokyo Story?", ["Ozu"]),
    T("Who invented the hot air balloon?", ["Montgolfier"]),
    T("Who discovered the moon Triton?", ["Lassell"]),
    T("Who discovered the moon Nereid?", ["Kuiper"]),
    T("Which planet does Ariel orbit?", ["Uranus"]),
    T("Which planet does Rhea orbit?", ["Saturn"]),
    T("Who founded Samsung?", ["Lee Byung-chul", "Byung-chul"]),
    T("Who was the architect of Fallingwater?", ["Frank Lloyd Wright", "Lloyd Wright"]),
    T("Where was Antonio Vivaldi born?", ["Venice"]),
    T("Where was Leo Tolstoy born?", ["Yasnaya Polyana"]),
    T("In what year was Charles Dickens born?", ["1812"]),
    T("Who was Johann Sebastian Bach married to?", ["Maria Barbara", "Anna Magdalena"]),
    T("Who was the father of Henry VIII?", ["Henry VII"]),
    T("Which instrument did Jaco Pastorius play?", ["bass"]),
    T("Which band was Thom Yorke a member of?", ["Radiohead"]),
    T("Who won the 1986 FIFA World Cup?", ["Argentina"]),
    T("Which city hosted the 1964 Summer Olympics?", ["Tokyo"]),
    T("In which constellation is the star Antares?", ["Scorpius", "Scorpio"]),
    T("Who created the character Philip Marlowe?", ["Chandler"]),
    T("Which company developed the video game The Sims?", ["Maxis"]),
    T("Name the author of Ulysses", ["Joyce"]),
    T("Tell me the capital of Norway", ["Oslo"]),
    T("The currency of Mexico", ["peso"]),
    T("Name the composer of Boléro", ["Ravel"]),
    T("The first person in space", ["Gagarin"]),
    T("Name the planet that the moon Titania orbits", ["Uranus"]),
    T("The director of the film Battleship Potemkin", ["Eisenstein"]),
    T("Name the painter of The Night Café", ["van Gogh", "Gogh"]),
    T("Name the capital of Cyprus", ["Nicosia"]),
    T("The inventor of the World Wide Web", ["Berners-Lee"]),
    T("Name the author of The Divine Comedy", ["Dante"]),
    T("The country in which the city of Porto Alegre lies", ["Brazil"]),
    # ---- exact (30)
    N("What is 12% of 3,400?", 408),
    N("What is 3/5 as a decimal?", 0.6),
    N("Solve for x: 4x + 9 = 41.", 8),
    N("What is the square root of 4,624?", 68),
    N("What is 7 to the power 3?", 343),
    N("How many seconds are there in 2.5 hours?", 9000),
    N("Convert 108 kilometres per hour to metres per second.", 30),
    N("Convert 113 degrees Fahrenheit to Celsius.", 45),
    N("How many millilitres are in 0.75 litres?", 750),
    N("What is 45 pounds in kilograms?", 45 * 0.45359237),
    N("What is the derivative of 2x^4 at x = 1?", 8),
    N("What is the area of a circle with radius 7 m?", math.pi * 49),
    N("What is the volume of a cube with side 9 cm?", 729),
    N("What is the mass of 5 litres of sea water in kg?", 5.125),
    N("What is the density of silver in kg/m3?", 10490),
    N("What is the pressure 12 m deep in fresh water?", 1000 * G * 12),
    N("How much energy in MJ does burning 3 kg of diesel release?", 129),
    N("A spring with spring constant 800 N/m is stretched 0.025 m. What force does it exert?", 20),
    N("How much of a 100 g sample of carbon-14 remains after 11,460 years?", 25),
    N("What is the kinetic energy of a 3 kg ball moving at 6 m/s?", 54),
    N("How long does a stone take to fall 30 m?", math.sqrt(2 * 30 / G)),
    N("What is 8 factorial divided by 6 factorial?", 56),
    N("What is the greatest common divisor of 96 and 156?", 12),
    N("How many hours are in 3 weeks?", 504),
    N("What is 40% of 735?", 294),
    N("What is the area of a triangle with base 14 m and height 5 m?", 35),
    N("Convert 15 miles to kilometres.", 15 * 1.609344),
    N("What is the perimeter of a rectangle 12 m by 7 m?", 38),
    N("What is 17 squared?", 289),
    N("How many grams are in 0.85 kilograms?", 850),
    # ---- multistep (20)
    N("A 2.5 kW heater runs 3 hours a day for 40 days. At $0.14 per kWh, what does that cost?", 42, g=M),
    N("A car gets 28 mpg and drives 350 miles. How many kg of CO2 does it emit?", 350 / 28 * 8.887, g=M),
    N("How many kWh does it take to heat 8 kg of water from 15 C to 65 C?", 8 * 4186 * 50 / 3.6e6, g=M),
    N("A 1.8 kW kettle runs 4 minutes a day for 45 days. How many kWh is that?", 1.8 * 4 / 60 * 45, g=M),
    N("A cylindrical tank 1.5 m across and 1 m tall is full of water. What is the mass of the water in kg?", math.pi * 0.75 ** 2 * 1000, g=M),
    N("How much energy in MJ is released by burning 30 litres of diesel?", 0.03 * 832 * 43.0, g=M),
    N("A 4 kg block of lead is fully submerged in water. What is the buoyant force on it?", 4 / 11340 * 1000 * G, g=M),
    N("A bus averaging 8 miles per gallon covers 200 miles on gasoline. How many kg of CO2 is that?", 25 * 8.887, g=M),
    N("How many kilojoules does it take to warm 5 kg of water from 20 C to 30 C?", 5 * 4186 * 10 / 1000, g=M),
    N("How many kWh does it take to melt 25 kg of ice?", 25 * 334000 / 3.6e6, g=M),
    N("A 15 W LED is left on 10 hours a day for 365 days. How many kWh does it use?", 15 * 10 * 365 / 1000, g=M),
    N("A pump draws 2 A at 120 V for 6 hours. How many kWh does it use?", 2 * 120 * 6 / 1000, g=M),
    N("How much would a 70 kg astronaut weigh on a planet with 4 Earth masses and 1.6 Earth radii?", 70 * G * 4 / 2.56, tol=0.02, g=M),
    N("A 2 kW dryer runs 1.5 hours. At $0.30 per kWh, what does that cost?", 0.9, g=M),
    N("Water flows at 20 litres per minute for 35 minutes. How many litres is that?", 700, g=M),
    N("A train travels at 90 km/h for 2.4 hours. How far does it travel in km?", 216, g=M),
    N("A 0.8 kW fan heater runs 5 hours a day. How many kWh does it use in a 7-day week?", 28, g=M),
    N("A round drum 0.6 m across and 0.9 m tall is full of water. How heavy is the water, in kg?", math.pi * 0.3 ** 2 * 0.9 * 1000, g=M),
    N("A 1.4 kW iron runs 20 minutes a day for 30 days. At $0.20 per kWh, what does that cost?", 2.8, g=M),
    N("How many kWh does it take to heat 100 litres of water from 12 C to 52 C?", 100 * 4186 * 40 / 3.6e6, g=M),
    # ---- decline (30)
    X("What is the capital of Saturn?", "no such thing"),
    X("Who was the first emperor of Canada?", "no such office"),
    X("What is my neighbour's email address?", "private"),
    X("What will gold cost per ounce next Monday?", "unknowable future"),
    X("Who won the 2042 Tour de France?", "future event"),
    X("What is the population of Narnia?", "fictional place"),
    X("What did I say to my friend yesterday?", "private / unknowable"),
    X("A 100 W lamp runs 27 hours a day. How many kWh does it use daily?", "27 hours in a day"),
    X("A runner covers -10 km in 50 minutes. What is her average speed?", "negative distance"),
    X("What is the mass of -6 litres of petrol?", "negative volume"),
    X("How long does a stone take to fall -40 m?", "negative height"),
    X("What is the square root of happiness?", "meaningless"),
    X("Which country did Picasso serve as president of?", "false premise"),
    X("In what year did Isaac Newton win the Nobel Prize in Chemistry?", "false premise (no Nobel Prize)"),
    X("Who was the 80th Prime Minister of the United Kingdom?", "no such person yet"),
    X("What is my passport number?", "private"),
    X("What is the PIN for my debit card?", "private"),
    X("How much will my flat be worth in 2060?", "unknowable future"),
    X("Who is the current Tsar of Bulgaria?", "no such office"),
    X("What is the boiling point of a promise?", "meaningless"),
    X("What is the capital city of the Antarctic ice sheet?", "an ice sheet has no capital"),
    X("Which of Mars's five moons is the largest?", "false premise (Mars has two moons)"),
    X("What animal am I thinking of?", "unknowable"),
    X("Who wrote Pride and Prejudice in 1950?", "false premise (published 1813)"),
    X("What is the volume of a cube with side -5 cm?", "negative side"),
    X("A spring with spring constant -450 N/m is compressed 0.04 m. What force does it exert?", "negative stiffness"),
    X("What will the wind speed be in Dublin on 2 March 2034?", "unknowable future"),
    X("What social media app did Shakespeare use?", "anachronism"),
    X("Who discovered the fourth moon of Earth?", "Earth has one moon"),
    X("How much of a 75 g sample remains after 4 weeks?", "no isotope or half-life given"),
]

DIALOGUES = [
    [F("Who directed Ugetsu?", ["Mizoguchi"]), U("When was he born?", ["1898"]), U("Where?", ["Tokyo"])],
    [F("What is the capital of Slovakia's neighbour Hungary?", ["Budapest"]), U("And its currency?", ["forint"]), U("Which continent is it on?", ["Europe"])],
    [F("Who composed the opera Werther?", ["Massenet"]), U("Where was he born?", ["Montaud", "Saint-Étienne", "Saint-Etienne"]), U("In what year did he die?", ["1912"])],
    [F("Which planet does Umbriel orbit?", ["Uranus"]), U("Who discovered Umbriel?", ["Lassell"]), U("Where was he born?", ["Bolton"])],
    [MU("Who wrote Emma, and who wrote Little Women?", [["Austen"], ["Alcott"]])],
    [NU("What is the mass of 6 litres of sea water in kg?", 6.15), NU("What does that weigh in newtons?", 6.15 * G)],
    [NU("A cylindrical tank 0.4 m across and 1.5 m tall is full of water. What is the mass of the water in kg?", math.pi * 0.2 ** 2 * 1.5 * 1000),
     NU("How much does that water weigh in newtons?", math.pi * 0.2 ** 2 * 1.5 * 1000 * G)],
    [F("Who founded Honda?", ["Soichiro Honda", "Sōichirō Honda"]), U("When was it founded?", ["1948"]), U("Where is it headquartered?", ["Tokyo", "Minato"])],
    [F("Who was the architect of the Flatiron Building?", ["Burnham"]), U("When did it open?", ["1902"]), U("Which country is it in?", ["United States"])],
    [F("Which country did the biathlete Martin Fourcade represent?", ["France"]), U("When was he born?", ["1988"])],
    [F("Where was the figure skater Javier Fernández born?", ["Madrid"]), U("Which country does he represent?", ["Spain"])],
    [F("Where was Alan Turing born?", ["Maida Vale", "London"]), U("When did he die?", ["1954"])],
    [SO("Hi!"), DE("What will I eat for dinner tonight?", "unknowable"), F("Which constellation is Sirius in?", ["Canis Major"]), SO("Thanks, bye.")],
    [NU("A 1.6 kW heater runs 4 hours a day. How many kWh does it use in a week?", 44.8), NU("At $0.20 per kWh, what does that cost?", 8.96)],
    [MU("What is the capital of Finland, and what is 15% of 640?", [["Helsinki"], ["96"]])],
    [F("Who wrote The Seagull?", ["Chekhov"]), U("Where was he born?", ["Taganrog"]), U("Who was he married to?", ["Knipper"])],
    [NU("How much of a 60 g sample of iodine-131 remains after 20 days?", 60 * 0.5 ** (20 / 8.0252)),
     NU("And after 40 days?", 60 * 0.5 ** (40 / 8.0252))],
    [NU("What is the mass of 0.2 litres of mercury in kg?", 2.707), DE("And of -0.2 litres?", "negative volume")],
    [F("Which planet is Ganymede a moon of?", ["Jupiter"]), U("Who discovered Ganymede?", ["Galileo"]), U("Where did he die?", ["Arcetri", "Florence"])],
    [F("Who directed My Neighbor Totoro?", ["Miyazaki"]), U("When was he born?", ["1941"]), SO("Great, thanks.")],
]


def check():
    groups = {}
    for it in ITEMS:
        groups[it["group"]] = groups.get(it["group"], 0) + 1
        if it["kind"] == "number":
            givens = [float(t.replace(",", "")) for t in re.findall(r"(?<![\w.])\d[\d,]*(?:\.\d+)?", it["q"])]
            assert not any(abs(g - it["expect"]) <= 0.01 * max(abs(g), 1) for g in givens), ("answer near a given", it["q"])
        if it["kind"] == "text":
            assert all(len(a) >= 3 for a in it["expect"]), ("alias under 3 characters", it["q"])
    nq = sum(1 for it in ITEMS if it["group"] == K and not it["q"].rstrip().endswith("?"))
    assert groups == {K: 70, E: 30, M: 20, D: 30}, groups
    assert nq == 12, nq
    assert len({it["q"] for it in ITEMS}) == len(ITEMS), "duplicate question"
    for d in DIALOGUES:
        for t in d:
            if t["kind"] == "number":
                givens = [float(x.replace(",", "")) for x in re.findall(r"(?<![\w.])\d[\d,]*(?:\.\d+)?", t["q"])]
                assert not any(abs(g - t["expect"]) <= 0.01 * max(abs(g), 1) for g in givens), ("dialogue answer near a given", t["q"])
    return groups, len(DIALOGUES), sum(len(d) for d in DIALOGUES)


if __name__ == "__main__":
    print(check())
    json.dump(ITEMS, open(sys.argv[1], "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    json.dump(DIALOGUES, open(sys.argv[2], "w", encoding="utf-8"), indent=1, ensure_ascii=False)
