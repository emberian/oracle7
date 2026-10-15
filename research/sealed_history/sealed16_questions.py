"""sealed16_questions - SEALED TEST 16: the release gate for the final candidate (head after w536: receipts name both ends of a
fact; relation-family precedence learned from path memory's credit data). Written by Claude on 2026-10-13 BEFORE w536 was
measured on any of it; same author - disclosed. Tests 12-15 are spent (15 passed every bar on head w534; w536 changes
single-turn answers on relation questions, so 15's verdict cannot carry). Two parts, each run ONCE per release variant:
  SINGLE    150 questions, the recipe and group sizes of tests 12-15; scoring = run_sealed15's rules unchanged.
  DIALOGUES 20 conversations, the recipe of conversation tests 2-3 (hand-offs between specialists, follow-ups after a
            specialist's answer, two-part turns, chained calculations, declines inside a conversation).
Bars (unchanged): precision on answered >= 0.90, false yes <= 2, zero format defects (single part). Answer keys avoid the
known key errors (calendar-dependent dates; an answer equal or close to a given number; titles shared by two famous works)."""
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
    T("Who wrote Nostromo?", ["Conrad"]),
    T("Who wrote The Tales of Mother Goose?", ["Perrault"]),
    T("Who wrote The Foundation Pit?", ["Platonov"]),
    T("Who wrote Père Goriot?", ["Balzac"]),
    T("Who wrote The Sorrows of Young Werther?", ["Goethe"]),
    T("Who wrote Rhinoceros, the absurdist play?", ["Ionesco"]),
    T("Who wrote The Bell Jar?", ["Plath"]),
    T("Who is the author of Invisible Cities?", ["Calvino"]),
    T("Who is the author of Blindness, the 1995 novel?", ["Saramago"]),
    T("Who is the author of The House of the Spirits?", ["Allende"]),
    T("Who painted The Garden at Sainte-Adresse?", ["Monet"]),
    T("Who painted The Card Players?", ["Cézanne", "Cezanne"]),
    T("Who painted The Ghent Altarpiece?", ["van Eyck", "Eyck"]),
    T("Who painted Olympia, the 1863 painting?", ["Manet"]),
    T("Who painted The Blue Boy?", ["Gainsborough"]),
    T("Who composed the opera Salome?", ["Strauss"]),
    T("Who composed the opera Wozzeck?", ["Berg"]),
    T("Who composed the opera Dido and Aeneas?", ["Purcell"]),
    T("Who composed the ballet The Sleeping Beauty?", ["Tchaikovsky"]),
    T("Who composed An American in Paris?", ["Gershwin"]),
    T("What is the capital of Mauritius?", ["Port Louis"]),
    T("What is the capital of Azerbaijan?", ["Baku"]),
    T("What is the capital of Panama?", ["Panama City"]),
    T("What is the capital of Rwanda?", ["Kigali"]),
    T("What is the capital of Uzbekistan?", ["Tashkent"]),
    T("Which city is the capital of Venezuela?", ["Caracas"]),
    T("Which city is the capital of Sudan?", ["Khartoum"]),
    T("What is the currency of Kenya?", ["shilling"]),
    T("What is the currency of Vietnam's neighbour Laos?", ["kip"]),
    T("What is the currency of Iceland?", ["króna", "krona"]),
    T("What is the official language of Brazil's neighbour Suriname?", ["Dutch"]),
    T("What is the official language of Costa Rica?", ["Spanish"]),
    T("On which continent is Paraguay?", ["South America"]),
    T("Which country is the city of Arequipa in?", ["Peru"]),
    T("Which country is the city of Mombasa in?", ["Kenya"]),
    T("Who directed Fanny and Alexander?", ["Bergman"]),
    T("Who directed Amarcord?", ["Fellini"]),
    T("Who directed The Rules of the Game?", ["Renoir"]),
    T("Who directed Late Spring?", ["Ozu"]),
    T("Who invented the Davy lamp?", ["Davy"]),
    T("Who discovered the moon Enceladus?", ["Herschel"]),
    T("Who discovered the moon Mimas?", ["Herschel"]),
    T("Which planet does Iapetus orbit?", ["Saturn"]),
    T("Which planet does Hyperion orbit?", ["Saturn"]),
    T("Who founded the Lego Group?", ["Ole Kirk Christiansen", "Kirk Christiansen"]),
    T("Who was the architect of the Guggenheim Museum in New York?", ["Frank Lloyd Wright", "Lloyd Wright"]),
    T("Where was Franz Liszt born?", ["Raiding", "Doborján"]),
    T("Where was Henrik Ibsen born?", ["Skien"]),
    T("In what year was Johannes Brahms born?", ["1833"]),
    T("Who was Gustav Mahler married to?", ["Alma"]),
    T("Who was the father of Elizabeth II?", ["George VI"]),
    T("Which instrument did Pablo Casals play?", ["cello"]),
    T("Which band was Roger Waters a member of?", ["Pink Floyd"]),
    T("Who won the 1974 FIFA World Cup?", ["West Germany", "Germany"]),
    T("Which city hosted the 1972 Summer Olympics?", ["Munich"]),
    T("In which constellation is the star Deneb?", ["Cygnus"]),
    T("Who created the character Miss Marple?", ["Agatha Christie", "Christie"]),
    T("Which company developed the video game Portal?", ["Valve"]),
    T("Name the author of The Old Curiosity Shop", ["Dickens"]),
    T("Tell me the capital of Denmark", ["Copenhagen"]),
    T("The currency of India", ["rupee"]),
    T("Name the composer of The Moldau", ["Smetana"]),
    T("The first person to fly solo across the Atlantic", ["Lindbergh"]),
    T("Name the planet that the moon Nereid orbits", ["Neptune"]),
    T("The director of the film Ran", ["Kurosawa"]),
    T("Name the painter of The Embarkation for Cythera", ["Watteau"]),
    T("Name the capital of Romania", ["Bucharest"]),
    T("The inventor of the diesel engine", ["Rudolf Diesel", "Diesel"]),
    T("Name the author of The Waste Land", ["Eliot"]),
    T("The country in which the city of Medellín lies", ["Colombia"]),
    # ---- exact (30)
    N("What is 14% of 2,850?", 399),
    N("What is 7/20 as a decimal?", 0.35),
    N("Solve for x: 5x - 8 = 47.", 11),
    N("What is the square root of 5,329?", 73),
    N("What is 6 to the power 4?", 1296),
    N("How many seconds are there in 3.25 hours?", 11700),
    N("Convert 126 kilometres per hour to metres per second.", 35),
    N("Convert 77 degrees Fahrenheit to Celsius.", 25),
    N("How many millilitres are in 1.35 litres?", 1350),
    N("What is 64 pounds in kilograms?", 64 * 0.45359237),
    N("What is the derivative of 4x^3 at x = 3?", 108),
    N("What is the area of a circle with radius 8 m?", math.pi * 64),
    N("What is the volume of a cube with side 11 cm?", 1331),
    N("What is the mass of 7 litres of sea water in kg?", 7.175),
    N("What is the density of copper in kg/m3?", 8960),
    N("What is the pressure 18 m deep in fresh water?", 1000 * G * 18),
    N("How much energy in MJ does burning 4 kg of natural gas release?", 192),
    N("A spring with spring constant 350 N/m is stretched 0.06 m. What force does it exert?", 21),
    N("How much of a 90 g sample of iodine-131 remains after 24.08 days?", 90 * 0.5 ** (24.08 / 8.0252)),
    N("What is the kinetic energy of a 5 kg ball moving at 8 m/s?", 160),
    N("How long does a stone take to fall 50 m?", math.sqrt(2 * 50 / G)),
    N("What is 11 factorial divided by 9 factorial?", 110),
    N("What is the greatest common divisor of 210 and 330?", 30),
    N("How many minutes are in 4.5 days?", 6480),
    N("What is 65% of 920?", 598),
    N("What is the area of a triangle with base 16 m and height 9 m?", 72),
    N("Convert 42 kilometres to miles.", 42 / 1.609344),
    N("What is the perimeter of a rectangle 13 m by 8 m?", 42),
    N("What is 19 squared?", 361),
    N("How many grams are in 3.04 kilograms?", 3040),
    # ---- multistep (20)
    N("A 2.4 kW heater runs 5 hours a day for 30 days. At $0.15 per kWh, what does that cost?", 54, g=M),
    N("A car gets 32 mpg and drives 480 miles. How many kg of CO2 does it emit?", 15 * 8.887, g=M),
    N("How many kWh does it take to heat 12 kg of water from 18 C to 78 C?", 12 * 4186 * 60 / 3.6e6, g=M),
    N("A 2.2 kW kettle runs 3 minutes a day for 50 days. How many kWh is that?", 2.2 * 3 / 60 * 50, g=M),
    N("A cylindrical tank 1.2 m across and 1.8 m tall is full of water. What is the mass of the water in kg?", math.pi * 0.6 ** 2 * 1.8 * 1000, g=M),
    N("How much energy in MJ is released by burning 45 litres of diesel?", 0.045 * 832 * 43.0, g=M),
    N("A 6 kg block of silver is fully submerged in water. What is the buoyant force on it?", 6 / 10490 * 1000 * G, g=M),
    N("A van averaging 18 miles per gallon covers 270 miles on gasoline. How many kg of CO2 is that?", 15 * 8.887, g=M),
    N("How many kilojoules does it take to warm 6 kg of copper from 25 C to 75 C?", 6 * 385 * 50 / 1000, g=M),
    N("How many kWh does it take to melt 30 kg of ice?", 30 * 334000 / 3.6e6, g=M),
    N("A 9 W bulb is left on 12 hours a day for 365 days. How many kWh does it use?", 9 * 12 * 365 / 1000, g=M),
    N("A motor draws 4 A at 230 V for 5 hours. How many kWh does it use?", 4 * 230 * 5 / 1000, g=M),
    N("How much would an 85 kg astronaut weigh on a planet with 2.5 Earth masses and 1.4 Earth radii?", 85 * G * 2.5 / 1.96, tol=0.02, g=M),
    N("A 1.2 kW heater runs 7.5 hours. At $0.24 per kWh, what does that cost?", 2.16, g=M),
    N("Water flows at 18 litres per minute for 45 minutes. How many litres is that?", 810, g=M),
    N("A ferry travels at 32 km/h for 2.75 hours. How far does it travel in km?", 88, g=M),
    N("A 1.8 kW oven runs 2.5 hours a day. How many kWh does it use in a 7-day week?", 31.5, g=M),
    N("A round drum 0.7 m across and 1.1 m tall is full of water. How heavy is the water, in kg?", math.pi * 0.35 ** 2 * 1.1 * 1000, g=M),
    N("A 0.9 kW blender runs 10 minutes a day for 60 days. At $0.25 per kWh, what does that cost?", 2.25, g=M),
    N("How many kWh does it take to heat 120 litres of water from 14 C to 54 C?", 120 * 4186 * 40 / 3.6e6, g=M),
    # ---- decline (30)
    X("What is the capital of Neptune?", "no such thing"),
    X("Who was the first king of Switzerland?", "no such office"),
    X("What is my cousin's date of birth?", "private"),
    X("What will oil cost per barrel next Thursday?", "unknowable future"),
    X("Who won the 2046 Olympic 100 metres final?", "future event"),
    X("What is the population of Middle-earth?", "fictional place"),
    X("What did I write in my diary last week?", "private / unknowable"),
    X("A 60 W lamp runs 31 hours a day. How many kWh does it use daily?", "31 hours in a day"),
    X("A boat sails -30 km in 2 hours. What is its average speed?", "negative distance"),
    X("What is the mass of -8 litres of seawater?", "negative volume"),
    X("How long does an apple take to fall -12 m?", "negative height"),
    X("What is the cube root of loneliness?", "meaningless"),
    X("Which country did Van Gogh rule as emperor?", "false premise"),
    X("In what year did Galileo win the Nobel Prize in Physics?", "false premise (no Nobel Prize)"),
    X("Who was the 75th President of Germany?", "no such person yet"),
    X("What is my national insurance number?", "private"),
    X("What is the alarm code for my house?", "private"),
    X("How much will my shares be worth in 2055?", "unknowable future"),
    X("Who is the current Kaiser of Austria?", "no such office"),
    X("What is the melting point of a rumour?", "meaningless"),
    X("What is the capital city of the Southern Ocean?", "an ocean has no capital"),
    X("Which of Venus's three moons is the smallest?", "false premise (Venus has no moons)"),
    X("What fruit am I thinking of?", "unknowable"),
    X("Who composed the Moonlight Sonata in 1950?", "false premise (composed 1801)"),
    X("What is the area of a circle with radius -9 m?", "negative radius"),
    X("A spring with spring constant -120 N/m is stretched 0.3 m. What force does it exert?", "negative stiffness"),
    X("What will the humidity be in Lima on 8 May 2037?", "unknowable future"),
    X("Which email provider did Napoleon use?", "anachronism"),
    X("Who discovered the second moon of Mercury?", "Mercury has no moons"),
    X("How much of a 120 g sample remains after 9 days?", "no isotope or half-life given"),
]

DIALOGUES = [
    [F("Who directed Throne of Blood?", ["Kurosawa"]), U("When was he born?", ["1910"]), U("When did he die?", ["1998"])],
    [F("What is the capital of Slovenia, the country?", ["Ljubljana"]), U("And its currency?", ["euro"]), U("Which continent is it on?", ["Europe"])],
    [F("Who composed the opera Mignon?", ["Ambroise Thomas", "Thomas"]), U("Where was he born?", ["Metz"]), U("In what year did he die?", ["1896"])],
    [F("Which planet does the moon Titania orbit?", ["Uranus"]), U("Who discovered Titania?", ["Herschel"]), U("Where was he born?", ["Hanover", "Hannover"])],
    [MU("Who wrote Daniel Deronda, and who wrote Cranford?", [["Eliot"], ["Gaskell"]])],
    [NU("What is the mass of 9 litres of sea water in kg?", 9.225), NU("What does that weigh in newtons?", 9.225 * G)],
    [NU("A cylindrical tank 0.6 m across and 1.2 m tall is full of water. What is the mass of the water in kg?", math.pi * 0.3 ** 2 * 1.2 * 1000),
     NU("How much does that water weigh in newtons?", math.pi * 0.3 ** 2 * 1.2 * 1000 * G)],
    [F("Who founded Toyota Motor Corporation?", ["Kiichiro Toyoda", "Toyoda"]), U("When was it founded?", ["1937"]), U("Where is it headquartered?", ["Toyota"])],
    [F("Who was the architect of the Woolworth Building?", ["Cass Gilbert", "Gilbert"]), U("When did it open?", ["1913"]),
     U("Which country is it in?", ["United States"])],
    [F("Which country did the biathlete Johannes Thingnes Bø represent?", ["Norway"]), U("When was he born?", ["1993"])],
    [F("Where was the figure skater Evgeni Plushenko born?", ["Solnechny", "Solnechnyy"]), U("Which country does he represent?", ["Russia"])],
    [F("Where was Grace Hopper born?", ["New York"]), U("When did she die?", ["1992"])],
    [SO("Good morning!"), DE("What will I do this weekend?", "unknowable"), F("Which constellation is Rigel in?", ["Orion"]), SO("Thanks, that's all.")],
    [NU("A 2.6 kW heater runs 3 hours a day. How many kWh does it use in a week?", 54.6), NU("At $0.20 per kWh, what does that cost?", 10.92)],
    [MU("What is the capital of Ireland, and what is 35% of 840?", [["Dublin"], ["294"]])],
    [F("Who wrote The Three Sisters?", ["Chekhov"]), U("Where was he born?", ["Taganrog"]), U("When did he die?", ["1904"])],
    [NU("How much of a 70 g sample of iodine-131 remains after 12 days?", 70 * 0.5 ** (12 / 8.0252)),
     NU("And after 36 days?", 70 * 0.5 ** (36 / 8.0252))],
    [NU("What is the mass of 0.3 litres of mercury in kg?", 4.06), DE("And of -0.3 litres?", "negative volume")],
    [F("Which planet is Callisto a moon of?", ["Jupiter"]), U("Who discovered Callisto?", ["Galileo", "Marius"]), U("Where was he born?", ["Pisa", "Gunzenhausen"])],
    [F("Who directed Princess Mononoke?", ["Miyazaki"]), U("When was he born?", ["1941"]), SO("Lovely, thank you.")],
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
