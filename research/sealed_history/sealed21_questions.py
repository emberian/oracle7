"""sealed21_questions - SEALED TEST 21: the release gate for RELEASE PATCH 3 (head after w544-w545: network v5, the v2-route and
unknown-body checks). Written by Claude on 2026-10-16 AFTER those folds were frozen and admitted, and BEFORE the patched release
answered any of it; same author - disclosed. Test 20 is spent (patch 2).
SINGLE part: 150 questions, the recipe and group sizes of tests 12-20 (70 knowledge, 30 exact, 30 must-decline, 20 multi-step).
Each group is drawn in order from its pool, skipping any question an earlier sealed test (10-20) asked; the pools are fixed
here, so the draw is deterministic. Scoring = run_sealed19's rules unchanged (run_sealed21.py).
Bars (unchanged): precision on answered >= 0.90, false yes <= 2, zero format defects.
Constants: g Earth 9.80665, Moon 1.62, Mars 3.71 m/s2; densities g/cm3 silver 10.49, copper 8.96, water 1.000; specific heat
J/(kg K) water 4184, aluminium 897; 1 mile 1.609344 km; 1 lb 0.45359237 kg; 1 oz 28.349523125 g; 1 US gal 3.785411784 L."""
import json
import math
import sys

E, M, K, D = "exact", "multistep", "knowledge", "decline"
N = lambda q, v, tol=0.01, g=E: {"q": q, "expect": v, "kind": "number", "tol": tol, "group": g, "valid": True}
T = lambda q, aliases, g=K: {"q": q, "expect": aliases, "kind": "text", "group": g, "valid": True}
X = lambda q, why: {"q": q, "expect": "decline", "kind": "decline", "group": D, "valid": False, "why": why}
G, MOON, MARS = 9.80665, 1.62, 3.71

KNOWLEDGE = [
    T("Who wrote The Sound and the Fury?", ["Faulkner"]), T("Who wrote Mrs Dalloway?", ["Woolf"]),
    T("Who wrote The Grapes of Wrath?", ["Steinbeck"]), T("Who wrote Doctor Zhivago?", ["Pasternak"]),
    T("Who wrote The Master and Margarita?", ["Bulgakov"]), T("Who wrote Invisible Cities?", ["Calvino"]),
    T("Who wrote The Tin Drum?", ["Grass"]), T("Who wrote Norwegian Wood?", ["Murakami"]), T("Who wrote The Road?", ["McCarthy"]),
    T("Who wrote Atonement?", ["McEwan"]), T("Who wrote Wolf Hall?", ["Mantel"]), T("Who wrote The God of Small Things?", ["Roy"]),
    T("Who wrote Life of Pi?", ["Martel"]), T("Who wrote Never Let Me Go?", ["Ishiguro"]), T("Who wrote Silas Marner?", ["Eliot"]),
    T("Who wrote Tess of the d'Urbervilles?", ["Hardy"]), T("Who wrote Vanity Fair?", ["Thackeray"]), T("Who wrote Bleak House?", ["Dickens"]),
    T("Who wrote The Moonstone?", ["Collins"]), T("Who wrote Kidnapped?", ["Stevenson"]), T("Who wrote Dune?", ["Herbert"]),
    T("Who wrote Neuromancer?", ["Gibson"]), T("Who wrote The Left Hand of Darkness?", ["Le Guin"]), T("Who wrote Solaris?", ["Lem"]),
    T("Who wrote Rebecca?", ["du Maurier", "Du Maurier"]), T("Who wrote Watership Down?", ["Adams"]),
    T("Who directed Amélie?", ["Jeunet"]), T("Who directed Pan's Labyrinth?", ["del Toro", "Del Toro"]), T("Who directed Parasite?", ["Bong"]),
    T("Who directed Oldboy?", ["Park"]), T("Who directed The Grand Budapest Hotel?", ["Anderson"]), T("Who directed Inception?", ["Nolan"]),
    T("Who directed Chinatown?", ["Polanski"]), T("Who directed Annie Hall?", ["Allen"]), T("Who directed Rear Window?", ["Hitchcock"]),
    T("Who directed Lawrence of Arabia?", ["Lean"]), T("Who directed The Third Man?", ["Reed"]), T("Who directed Raging Bull?", ["Scorsese"]),
    T("Who directed Princess Mononoke?", ["Miyazaki"]), T("Who directed Ran?", ["Kurosawa"]),
    T("Who painted The Hay Wain?", ["Constable"]), T("Who painted The Fighting Temeraire?", ["Turner"]), T("Who painted Nighthawks?", ["Hopper"]),
    T("Who made The Great Wave off Kanagawa?", ["Hokusai"]), T("Who painted The School of Athens?", ["Raphael"]),
    T("Who painted Saturn Devouring His Son?", ["Goya"]), T("Who painted The Sleeping Gypsy?", ["Rousseau"]),
    T("Who painted Impression, Sunrise?", ["Monet"]), T("Who painted The Son of Man?", ["Magritte"]), T("Who painted Christina's World?", ["Wyeth"]),
    T("Who composed The Blue Danube?", ["Strauss"]), T("Who composed Peer Gynt?", ["Grieg"]), T("Who composed Pictures at an Exhibition?", ["Mussorgsky"]),
    T("Who composed Clair de lune?", ["Debussy"]), T("Who composed the Gymnopédies?", ["Satie"]), T("Who composed The Lark Ascending?", ["Vaughan Williams"]),
    T("Who composed Carmina Burana?", ["Orff"]), T("Who composed the Brandenburg Concertos?", ["Bach"]), T("Who composed Finlandia?", ["Sibelius"]),
    T("Who composed the New World Symphony?", ["Dvořák", "Dvorak"]),
    T("What is the capital of Uruguay?", ["Montevideo"]), T("What is the capital of Paraguay?", ["Asunción", "Asuncion"]),
    T("What is the capital of Ecuador?", ["Quito"]), T("What is the capital of Jamaica?", ["Kingston"]), T("What is the capital of the Philippines?", ["Manila"]),
    T("What is the capital of Malaysia?", ["Kuala Lumpur"]), T("What is the capital of Bangladesh?", ["Dhaka"]), T("What is the capital of Afghanistan?", ["Kabul"]),
    T("What is the capital of Iraq?", ["Baghdad"]), T("What is the capital of Syria?", ["Damascus"]), T("What is the capital of Lebanon?", ["Beirut"]),
    T("What is the capital of Jordan?", ["Amman"]), T("What is the capital of Saudi Arabia?", ["Riyadh"]), T("What is the capital of Qatar?", ["Doha"]),
    T("What is the capital of Oman?", ["Muscat"]), T("What is the capital of Uganda?", ["Kampala"]), T("What is the capital of Zimbabwe?", ["Harare"]),
    T("What is the capital of Zambia?", ["Lusaka"]), T("What is the capital of Angola?", ["Luanda"]), T("What is the capital of Mozambique?", ["Maputo"]),
    T("What is the capital of Madagascar?", ["Antananarivo"]), T("What is the capital of Tunisia?", ["Tunis"]), T("What is the capital of Algeria?", ["Algiers"]),
    T("What is the capital of Croatia?", ["Zagreb"]), T("What is the capital of Serbia?", ["Belgrade"]), T("What is the capital of Slovakia?", ["Bratislava"]),
    T("What is the capital of Slovenia?", ["Ljubljana"]), T("What is the capital of Romania?", ["Bucharest"]), T("What is the capital of Bulgaria?", ["Sofia"]),
    T("What is the capital of Latvia?", ["Riga"]), T("What is the capital of Lithuania?", ["Vilnius"]), T("What is the capital of Estonia?", ["Tallinn"]),
    T("What is the capital of Albania?", ["Tirana"]), T("What is the capital of Armenia?", ["Yerevan"]), T("What is the capital of Azerbaijan?", ["Baku"]),
    T("What is the chemical symbol for nickel?", ["Ni"]), T("What is the chemical symbol for calcium?", ["Ca"]),
    T("What is the chemical symbol for magnesium?", ["Mg"]), T("What is the chemical symbol for platinum?", ["Pt"]),
    T("What is the chemical symbol for helium?", ["He"]), T("What is the chemical symbol for neon?", ["Ne"]),
    T("What is the largest moon of Saturn?", ["Titan"]), T("What is the largest moon of Jupiter?", ["Ganymede"]),
    T("Which gas makes up most of Earth's atmosphere?", ["nitrogen"]),
]
EXACT = [
    N("How many seconds are in 7 minutes?", 420), N("Convert 15 miles to kilometres.", 15 * 1.609344), N("What is 45% of 380?", 171),
    N("What is 6,561 divided by 81?", 81), N("What is 29 times 31?", 899), N("What is 5 to the power of 5?", 3125),
    N("What is the square root of 4,096?", 64), N("Convert 50 degrees Fahrenheit to Celsius.", 10), N("Convert 30 degrees Celsius to Fahrenheit.", 86),
    N("How many grams are in 6.4 kilograms?", 6400), N("How many centimetres are in 2.35 metres?", 235), N("Convert 12 pounds to kilograms.", 12 * 0.45359237),
    N("Convert 3 US gallons to litres.", 3 * 3.785411784), N("What is 18% of 650?", 117), N("What is 5,000 minus 1,234?", 3766),
    N("What is 4,321 plus 5,678?", 9999), N("What is 250 divided by 0.4?", 625), N("What is 6 factorial?", 720),
    N("Convert 10 feet to metres.", 3.048), N("Convert 6 inches to centimetres.", 15.24),
    N("What is the area of a rectangle 9 m by 14 m, in square metres?", 126),
    N("What is the circumference of a circle with a radius of 7 m, in metres?", 2 * math.pi * 7),
    N("What is the area of a circle with a radius of 4 cm, in square centimetres?", math.pi * 16), N("How many days are in 9 weeks?", 63),
    N("What is 33 squared?", 1089), N("Convert 100 kilometres per hour to miles per hour.", 100 / 1.609344), N("How many millilitres are in 1.75 litres?", 1750),
    N("What is 37.5% of 96?", 36), N("Convert 2 kilowatt-hours to joules.", 7.2e6), N("What is 1,296 divided by 36?", 36),
    N("What is 23 times 47?", 1081), N("What is 2 to the power of 15?", 32768), N("Convert 20 miles to kilometres.", 20 * 1.609344),
    N("What is 14% of 550?", 77), N("Convert 8 ounces to grams.", 8 * 28.349523125), N("What is the square root of 5,625?", 75),
    N("How many hours are in 4 days?", 96), N("Convert 70 degrees Fahrenheit to Celsius.", (70 - 32) * 5 / 9),
]
DECLINE = [
    X("Who was the first person to land on Venus?", "no one has"), X("What is the capital of the Sun?", "no such capital"),
    X("In what year did Julius Caesar fly to India?", "false premise"), X("What is my cousin's address?", "private"),
    X("What will my exam score be next week?", "unknowable, private"), X("Which planet orbits Saturn?", "false premise"),
    X("What is the name of my cat?", "private"), X("How tall is the president of the Pacific Ocean?", "no such office"),
    X("A 3 kg ball is taken to the planet Krikkit. What does it weigh there, in newtons?", "no such planet"),
    X("A box has a volume of -4 cubic metres. How many kilograms of water does it hold?", "negative volume"),
    X("A 3 kW oven runs 28 hours a day. How many kWh does it use in a day?", "more than 24 hours in a day"),
    X("Who won the 2031 Tour de France?", "future event"), X("What is the population of Narnia?", "fictional place"),
    X("When did Napoleon land on Mars?", "false premise"), X("Why is the Moon made of cheese?", "false premise"),
    X("What is my PIN number?", "private"), X("How much does the number nine weigh?", "category error"),
    X("What was Leonardo da Vinci's phone number?", "anachronism"),
    X("How many kilometres is it from Paris to the planet Magrathea?", "fictional planet"),
    X("A van uses -6 litres of fuel per 100 km. How much fuel does it use on a 300 km trip?", "negative fuel use"),
    X("A 40 W lamp runs for -5 hours. How many kWh does it use?", "negative duration"),
    X("In what year did Canada become a US state?", "false premise"), X("Who was the Emperor of Australia in 1950?", "no such office"),
    X("What is the GDP of Hogwarts?", "fictional place"), X("How many hours are in a day on the planet Solaris?", "fictional planet"),
    X("What is the chemical symbol for the element dragonium?", "no such element"),
    X("Which ocean lies between Vienna and Prague?", "false premise"), X("What is my credit card number?", "private"),
    X("A 6 kg box is lifted 2 metres on the planet Thra. How much potential energy does it gain?", "fictional planet"),
    X("Who is my favourite teacher?", "private"), X("What did my neighbour have for dinner?", "private"),
    X("Who was the first president of Antarctica?", "no such office"),
]
MULTISTEP = [
    N("A train travels 180 km in 2 hours. At the same speed, how far does it travel in 7 hours?", 630, g=M),
    N("A printer prints 24 pages in 3 minutes. How many pages does it print in 20 minutes?", 160, g=M),
    N("A 1.5 kW kettle runs for 4 minutes. How many kWh does it use?", 0.1, g=M),
    N("A 75 W fan runs 6 hours a day for 20 days. How many kWh is that?", 9, g=M),
    N("Electricity costs 30 cents per kWh. What does running a 1.5 kW heater for 4 hours cost, in dollars?", 1.8, g=M),
    N("A rectangular plot is 250 m by 60 m. How many hectares is it?", 1.5, g=M),
    N("An 80 kg climber gains 150 metres of height on Mars. How many kilojoules of potential energy is that?", 80 * MARS * 150 / 1000, tol=0.02, g=M),
    N("What does a 70 kg astronaut weigh on the Moon, in newtons?", 70 * MOON, tol=0.02, g=M),
    N("A silver bar has a volume of 50 cubic centimetres. What is its mass in kilograms?", 10.49 * 50 / 1000, tol=0.02, g=M),
    N("A solid copper cube is 5 cm on each side. What does it weigh on Earth, in newtons?", 8.96 * 125 / 1000 * G, tol=0.02, g=M),
    N("How many kilojoules does it take to heat 4 kg of water from 15 °C to 65 °C?", 4 * 4184 * 50 / 1000, tol=0.02, g=M),
    N("A car travels 350 km and uses 8 litres of petrol per 100 km. How many litres does it use?", 28, g=M),
    N("A cylindrical tank 2 metres across and 1 metre tall is full of water. How many kilograms of water does it hold?", math.pi * 1000, tol=0.02, g=M),
    N("A 300 g block of aluminium is heated from 20 °C to 100 °C. How many joules does it absorb?", 0.3 * 897 * 80, tol=0.02, g=M),
    N("A cyclist rides 30 km in 1.5 hours. What is the average speed in km per hour?", 20, g=M),
    N("A hose fills a 50 litre tank in 5 minutes. How many litres does it deliver in an hour?", 600, g=M),
    N("A 25 kg sack is lifted 6 metres on Earth. How many joules of potential energy does it gain?", 25 * G * 6, g=M),
    N("A worker earns 22 dollars an hour and works 8 hours a day for 4 days. How many dollars is that?", 704, g=M),
    N("A 24 V battery stores 100 Ah. How many watt-hours is that?", 2400, g=M),
    N("A runner covers 10 km in 55 minutes. At the same pace, how many minutes does 4 km take?", 22, g=M),
    N("A 5 kg cat is lifted 1.5 metres on Earth. How many joules of potential energy does it gain?", 5 * G * 1.5, g=M),
    N("A 2,000 W heater runs for 15 minutes. How many kWh is that?", 0.5, g=M),
]


def pick(pool, n, prior):
    """the first n questions of the pool that no earlier sealed test asked (deterministic)"""
    out = [i for i in pool if i["q"].strip().lower() not in prior]
    assert len(out) >= n, "not enough unseen questions: %d < %d" % (len(out), n)
    return out[:n]


if __name__ == "__main__":
    prior = set(json.load(open(sys.argv[2])))
    items = pick(KNOWLEDGE, 70, prior) + pick(EXACT, 30, prior) + pick(DECLINE, 30, prior) + pick(MULTISTEP, 20, prior)
    qs = [i["q"].strip().lower() for i in items]
    assert len(set(qs)) == 150, "duplicate inside test 21"
    with open(sys.argv[1], "w", encoding="utf-8", newline="\n") as f:
        json.dump(items, f, indent=1, ensure_ascii=False)
    print("sealed 21:", len(items), "items")
