"""sealed17_questions - SEALED TEST 17: the release gate for the final candidate with w538 (weight in newtons; same-name guard;
supporting sentences with holes dropped). Written by Claude on 2026-10-13 BEFORE w538 answered any of it; same author -
disclosed. Tests 12-16 are spent; w538 changes single-turn reply text, so test 16's verdict cannot carry by invariance.
Two parts, each run ONCE per release variant (single part) / once on the head (dialogues):
  SINGLE    150 questions, the recipe and group sizes of tests 12-16; scoring = run_sealed16's rules unchanged.
  DIALOGUES 20 conversations (conversation test 5): follow-ups after specialist answers, a numeric follow-up after a computed
            mass, a name shared by two things, two-part turns, declines inside a conversation.
Bars (unchanged): precision on answered >= 0.90, false yes <= 2, zero format defects (single part).
Answer keys avoid the known key errors: calendar-dependent dates, answers near a given number, titles shared by two famous
works, false or convoluted premises in valid questions."""
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
    T("Who wrote Lord Jim?", ["Conrad"]),
    T("Who wrote Cannery Row?", ["Steinbeck"]),
    T("Who wrote Love in the Time of Cholera?", ["García Márquez", "Garcia Marquez"]),
    T("Who wrote Lolita?", ["Nabokov"]),
    T("Who wrote The Stranger, the 1942 novel by a French author?", ["Camus"]),
    T("Who wrote Oliver Twist?", ["Dickens"]),
    T("Who wrote The Castle, the 1926 novel?", ["Kafka"]),
    T("Who is the author of Twenty Years After?", ["Dumas"]),
    T("Who is the author of The Hunchback of Notre-Dame?", ["Hugo"]),
    T("Who is the author of The Wind in the Willows?", ["Grahame"]),
    T("Who painted Lady with an Ermine?", ["Leonardo"]),
    T("Who painted Woman with a Parasol?", ["Monet"]),
    T("Who painted The Descent from the Cross in Antwerp Cathedral?", ["Rubens"]),
    T("Who painted Impression, Sunrise?", ["Monet"]),
    T("Who painted The Sistine Madonna?", ["Raphael"]),
    T("Who composed the opera Nabucco?", ["Verdi"]),
    T("Who composed the opera Tannhäuser?", ["Wagner"]),
    T("Who composed the opera The Bartered Bride?", ["Smetana"]),
    T("Who composed the ballet Romeo and Juliet?", ["Prokofiev"]),
    T("Who composed The Lark Ascending?", ["Vaughan Williams"]),
    T("What is the capital of Burundi?", ["Gitega", "Bujumbura"]),
    T("What is the capital of Bahrain?", ["Manama"]),
    T("What is the capital of Qatar?", ["Doha"]),
    T("What is the capital of Georgia, the country?", ["Tbilisi"]),
    T("What is the capital of Albania?", ["Tirana"]),
    T("Which city is the capital of Ethiopia?", ["Addis Ababa"]),
    T("Which city is the capital of Lithuania?", ["Vilnius"]),
    T("What is the currency of Tunisia?", ["dinar"]),
    T("What is the currency of Botswana?", ["pula"]),
    T("What is the currency of Egypt?", ["pound"]),
    T("What is the official language of Honduras?", ["Spanish"]),
    T("What is the official language of Senegal?", ["French"]),
    T("On which continent is Nepal?", ["Asia"]),
    T("Which country is the city of Debrecen in?", ["Hungary"]),
    T("Which country is the city of Cork in?", ["Ireland"]),
    T("Who directed Lawrence of Arabia?", ["David Lean", "Lean"]),
    T("Who directed Touch of Evil?", ["Welles"]),
    T("Who directed The Third Man?", ["Carol Reed", "Reed"]),
    T("Who directed Paths of Glory?", ["Kubrick"]),
    T("Who invented the electric battery?", ["Volta"]),
    T("Who discovered the moon Tethys?", ["Cassini"]),
    T("Who discovered the moon Dione?", ["Cassini"]),
    T("Which planet does Umbriel orbit?", ["Uranus"]),
    T("Which planet does Proteus orbit?", ["Neptune"]),
    T("Who founded Hewlett-Packard?", ["Hewlett", "Packard"]),
    T("Who was the architect of the Pantheon in Paris?", ["Soufflot"]),
    T("Where was Robert Schumann born?", ["Zwickau"]),
    T("Where was Georg Friedrich Händel born?", ["Halle"]),
    T("In what year was Giuseppe Verdi born?", ["1813"]),
    T("Who was the mother of Louis XIV?", ["Anne of Austria"]),
    T("Who was the father of King Edward VII?", ["Albert"]),
    T("Which instrument did Yehudi Menuhin play?", ["violin"]),
    T("Which band was Ozzy Osbourne a member of?", ["Black Sabbath"]),
    T("Who won the 1982 FIFA World Cup?", ["Italy"]),
    T("Which city hosted the 1988 Summer Olympics?", ["Seoul"]),
    T("In which constellation is the star Altair?", ["Aquila"]),
    T("Who created the character Sam Spade?", ["Hammett"]),
    T("Which company developed the video game Doom?", ["id Software"]),
    T("Name the author of Brave New World", ["Huxley"]),
    T("Tell me the capital of Finland", ["Helsinki"]),
    T("The currency of Austria", ["euro"]),
    T("Name the composer of The Carnival of the Animals", ["Saint-Saëns", "Saint-Saens"]),
    T("The first person to climb Mount Everest with Tenzing Norgay", ["Hillary"]),
    T("Name the planet that the moon Rhea orbits", ["Saturn"]),
    T("The director of the film Rome, Open City", ["Rossellini"]),
    T("Name the painter of Rain, Steam and Speed", ["Turner"]),
    T("Name the capital of the Czech Republic", ["Prague"]),
    T("The inventor of the gramophone", ["Berliner"]),
    T("Name the author of The Odyssey", ["Homer"]),
    T("The country in which the city of Valparaíso lies", ["Chile"]),
    # ---- exact (30)
    N("What is 16% of 3,750?", 600),
    N("What is 9/25 as a decimal?", 0.36),
    N("Solve for x: 8x - 15 = 81.", 12),
    N("What is the square root of 6,889?", 83),
    N("What is 4 to the power 5?", 1024),
    N("How many seconds are there in 4.75 hours?", 17100),
    N("Convert 144 kilometres per hour to metres per second.", 40),
    N("Convert 95 degrees Fahrenheit to Celsius.", 35),
    N("How many millilitres are in 2.85 litres?", 2850),
    N("What is 88 pounds in kilograms?", 88 * 0.45359237),
    N("What is the derivative of 3x^2 at x = 7?", 42),
    N("What is the area of a circle with radius 11 m?", math.pi * 121),
    N("What is the volume of a cube with side 13 cm?", 2197),
    N("What is the mass of 11 litres of sea water in kg?", 11.275),
    N("What is the density of aluminium in kg/m3?", 2700),
    N("What is the pressure 22 m deep in fresh water?", 1000 * G * 22),
    N("How much energy in MJ does burning 6 kg of petrol release?", 6 * 44.3),
    N("A spring with spring constant 420 N/m is stretched 0.05 m. What force does it exert?", 21),
    N("What is the weight in newtons of a 12 kg suitcase on Earth?", 12 * G),
    N("What is the kinetic energy of a 7 kg ball moving at 6 m/s?", 126),
    N("How long does a stone take to fall 65 m?", math.sqrt(2 * 65 / G)),
    N("What is 9 factorial divided by 6 factorial?", 504),
    N("What is the greatest common divisor of 252 and 378?", 126),
    N("How many minutes are in 5.5 days?", 7920),
    N("What is 85% of 740?", 629),
    N("What is the area of a triangle with base 18 m and height 11 m?", 99),
    N("Convert 55 kilometres to miles.", 55 / 1.609344),
    N("What is the perimeter of a rectangle 15 m by 9 m?", 48),
    N("What is 23 squared?", 529),
    N("How many grams are in 5.06 kilograms?", 5060),
    # ---- multistep (20)
    N("A 3.2 kW heater runs 4 hours a day for 25 days. At $0.17 per kWh, what does that cost?", 3.2 * 4 * 25 * 0.17, g=M),
    N("A car gets 26 mpg and drives 390 miles. How many kg of CO2 does it emit?", 15 * 8.887, g=M),
    N("How many kWh does it take to heat 15 kg of water from 12 C to 72 C?", 15 * 4186 * 60 / 3.6e6, g=M),
    N("A 2.4 kW kettle runs 5 minutes a day for 36 days. How many kWh is that?", 2.4 * 5 / 60 * 36, g=M),
    N("A cylindrical tank 1.4 m across and 1.6 m tall is full of water. What is the mass of the water in kg?", math.pi * 0.7 ** 2 * 1.6 * 1000, g=M),
    N("How much energy in MJ is released by burning 35 litres of diesel?", 0.035 * 832 * 43.0, g=M),
    N("A 7 kg block of gold is fully submerged in water. What is the buoyant force on it?", 7 / 19300 * 1000 * G, g=M),
    N("A pickup averaging 16 miles per gallon covers 320 miles on gasoline. How many kg of CO2 is that?", 20 * 8.887, g=M),
    N("How many kilojoules does it take to warm 8 kg of water from 15 C to 40 C?", 8 * 4186 * 25 / 1000, g=M),
    N("How many kWh does it take to melt 40 kg of ice?", 40 * 334000 / 3.6e6, g=M),
    N("A 7 W bulb is left on 14 hours a day for 365 days. How many kWh does it use?", 7 * 14 * 365 / 1000, g=M),
    N("A heater draws 6 A at 230 V for 4 hours. How many kWh does it use?", 6 * 230 * 4 / 1000, g=M),
    N("How much would a 95 kg astronaut weigh on a planet with 1.5 Earth masses and 1.2 Earth radii?", 95 * G * 1.5 / 1.44, tol=0.02, g=M),
    N("A 1.6 kW heater runs 6.5 hours. At $0.21 per kWh, what does that cost?", 1.6 * 6.5 * 0.21, g=M),
    N("Water flows at 22 litres per minute for 55 minutes. How many litres is that?", 1210, g=M),
    N("A coach travels at 76 km/h for 3.25 hours. How far does it travel in km?", 247, g=M),
    N("A 2.1 kW oven runs 1.5 hours a day. How many kWh does it use in a 30-day month?", 94.5, g=M),
    N("A round drum 0.8 m across and 1.3 m tall is full of water. How heavy is the water, in kg?", math.pi * 0.4 ** 2 * 1.3 * 1000, g=M),
    N("A 1.3 kW toaster runs 6 minutes a day for 90 days. At $0.20 per kWh, what does that cost?", 1.3 * 0.1 * 90 * 0.2, g=M),
    N("How many kWh does it take to heat 180 litres of water from 11 C to 51 C?", 180 * 4186 * 40 / 3.6e6, g=M),
    # ---- decline (30)
    X("What is the capital of Uranus?", "no such thing"),
    X("Who was the first emperor of Argentina?", "no such office"),
    X("What is my uncle's favourite food?", "private"),
    X("What will copper cost per tonne next Wednesday?", "unknowable future"),
    X("Who won the 2050 FIFA World Cup?", "future event"),
    X("What is the population of Hogwarts?", "fictional place"),
    X("What did I buy at the shop yesterday?", "private / unknowable"),
    X("A 40 W lamp runs 29 hours a day. How many kWh does it use daily?", "29 hours in a day"),
    X("A swimmer covers -2 km in 40 minutes. What is her average speed?", "negative distance"),
    X("What is the mass of -9 litres of diesel?", "negative volume"),
    X("How long does a pebble take to fall -18 m?", "negative height"),
    X("What is the square root of curiosity?", "meaningless"),
    X("Which country did Charles Dickens rule as king?", "false premise"),
    X("In what year did Ada Lovelace win the Nobel Prize in Chemistry?", "false premise (no Nobel Prize)"),
    X("Who was the 85th Prime Minister of Mongolia?", "no such person yet"),
    X("What is my bank sort code?", "private"),
    X("What is the password for my laptop?", "private"),
    X("How much will my pension be worth in 2070?", "unknowable future"),
    X("Who is the current Czar of Serbia?", "no such office"),
    X("What is the freezing point of an apology?", "meaningless"),
    X("What is the capital city of the Mediterranean Sea?", "a sea has no capital"),
    X("Which of Jupiter's two moons is the larger?", "false premise (Jupiter has many moons)"),
    X("What vegetable am I thinking of?", "unknowable"),
    X("Who composed The Four Seasons in 1990?", "false premise (composed in the 1720s)"),
    X("What is the area of a square with side -7 m?", "negative side"),
    X("A spring with spring constant -90 N/m is stretched 0.4 m. What force does it exert?", "negative stiffness"),
    X("What will the visibility be in Rome on 11 April 2036?", "unknowable future"),
    X("Which streaming service did Mozart subscribe to?", "anachronism"),
    X("Who discovered the first moon of Venus?", "Venus has no moons"),
    X("How much of a 140 g sample remains after 11 days?", "no isotope or half-life given"),
]

DIALOGUES = [
    [F("Who directed Yojimbo?", ["Kurosawa"]), U("When was he born?", ["1910"]), U("When did he die?", ["1998"])],
    [F("What is the capital of Latvia, the Baltic country?", ["Riga"]), U("And its currency?", ["euro"]), U("Which continent is it on?", ["Europe"])],
    [F("Who composed the opera Lohengrin?", ["Wagner"]), U("Where was he born?", ["Leipzig"]), U("In what year did he die?", ["1883"])],
    [F("Which planet does the moon Oberon orbit?", ["Uranus"]), U("Who discovered Oberon?", ["Herschel"]), U("Where was he born?", ["Hanover", "Hannover"])],
    [MU("Who wrote Persuasion, and who wrote Vanity Fair?", [["Austen"], ["Thackeray"]])],
    [NU("What is the mass of 12 litres of sea water in kg?", 12.3), NU("What does that weigh in newtons?", 12.3 * G)],
    [NU("A cylindrical tank 0.5 m across and 1.4 m tall is full of water. What is the mass of the water in kg?", math.pi * 0.25 ** 2 * 1.4 * 1000),
     NU("How much does that water weigh in newtons?", math.pi * 0.25 ** 2 * 1.4 * 1000 * G)],
    [F("Who founded Sony?", ["Ibuka", "Morita"]), U("When was it founded?", ["1946"]), U("Where is it headquartered?", ["Tokyo", "Minato"])],
    [F("Who was the architect of the Empire State Building?", ["Shreve", "Lamb"]), U("When did it open?", ["1931"]), U("Which country is it in?", ["United States"])],
    [F("Which country did the biathlete Emil Hegle Svendsen represent?", ["Norway"]), U("When was he born?", ["1985"])],
    [F("Where was the figure skater Yuna Kim born?", ["Bucheon"]), U("Which country does she represent?", ["South Korea", "Korea"])],
    [F("Where was the engineer Tommy Flowers born?", ["London", "Poplar"]), U("When did he die?", ["1998"])],
    [SO("Hi there."), DE("What will I cook tomorrow?", "unknowable"), F("Which constellation is Aldebaran in?", ["Taurus"]), SO("Thank you, bye.")],
    [NU("A 2.2 kW heater runs 3.5 hours a day. How many kWh does it use in a week?", 53.9), NU("At $0.20 per kWh, what does that cost?", 10.78)],
    [MU("What is the capital of Portugal, and what is 45% of 620?", [["Lisbon"], ["279"]])],
    [F("Who wrote The Lady with the Dog?", ["Chekhov"]), U("Where was he born?", ["Taganrog"]), U("When did he die?", ["1904"])],
    [NU("How much of a 50 g sample of iodine-131 remains after 16 days?", 50 * 0.5 ** (16 / 8.0252)),
     NU("And after 32 days?", 50 * 0.5 ** (32 / 8.0252))],
    [NU("What is the mass of 0.25 litres of mercury in kg?", 3.383), DE("And of -0.25 litres?", "negative volume")],
    [F("Which planet is Io a moon of?", ["Jupiter"]), U("Who discovered Io?", ["Galileo"]), U("Where did he die?", ["Arcetri", "Florence"])],
    [F("Who directed Howl's Moving Castle?", ["Miyazaki"]), U("When was he born?", ["1941"]), SO("Great, thanks.")],
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
