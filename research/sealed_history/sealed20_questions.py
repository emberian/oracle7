"""sealed20_questions - SEALED TEST 20: the release gate for RELEASE PATCH 2 (head after w541-w543: network v4, the quantity
checks, the same-name guard). Written by Claude on 2026-10-16 AFTER those folds were frozen and admitted, and BEFORE the
patched release answered any of it; same author - disclosed. Test 19 is spent (RC13i, 14 October).
SINGLE part: 150 questions, the recipe and group sizes of tests 12-19 (70 knowledge, 30 exact, 30 must-decline, 20
multi-step); the multi-step and must-decline groups include patch 2's ground (another body's gravity, a solid's volume to
its weight, unknown planets, negative amounts and impossible rates). No question repeats any earlier sealed test (checked
against all of tests 10-19 when the file is written). Scoring = run_sealed19's rules unchanged (run_sealed20.py).
Bars (unchanged): precision on answered >= 0.90, false yes <= 2, zero format defects.
Constants for expected values: g Earth 9.80665, Moon 1.62, Mars 3.71 m/s2; densities g/cm3 gold 19.32, aluminium 2.70,
water 1.000; specific heat J/(kg K) water 4184, copper 385; 1 mile 1.609344 km; 1 lb 0.45359237 kg; 1 US gal 3.785411784 L."""
import json
import math
import sys

E, M, K, D = "exact", "multistep", "knowledge", "decline"
N = lambda q, v, tol=0.01, g=E: {"q": q, "expect": v, "kind": "number", "tol": tol, "group": g, "valid": True}
T = lambda q, aliases, g=K: {"q": q, "expect": aliases, "kind": "text", "group": g, "valid": True}
X = lambda q, why: {"q": q, "expect": "decline", "kind": "decline", "group": D, "valid": False, "why": why}
G, MOON, MARS = 9.80665, 1.62, 3.71

KNOWLEDGE = [
    T("Who wrote Middlemarch?", ["Eliot"]),
    T("Who wrote The Brothers Karamazov?", ["Dostoevsky", "Dostoyevsky"]),
    T("Who wrote Things Fall Apart?", ["Achebe"]),
    T("Who wrote The Trial?", ["Kafka"]),
    T("Who wrote Beloved?", ["Morrison"]),
    T("Who wrote Brave New World?", ["Huxley"]),
    T("Who wrote Fahrenheit 451?", ["Bradbury"]),
    T("Who wrote The Old Man and the Sea?", ["Hemingway"]),
    T("Who wrote Wuthering Heights?", ["Brontë", "Bronte"]),
    T("Who wrote Don Quixote?", ["Cervantes"]),
    T("Who wrote The Divine Comedy?", ["Dante"]),
    T("Who wrote Paradise Lost?", ["Milton"]),
    T("Who wrote The Hobbit?", ["Tolkien"]),
    T("Who wrote Ulysses?", ["Joyce"]),
    T("Who wrote The Stranger?", ["Camus"]),
    T("Who wrote Lolita?", ["Nabokov"]),
    T("Who wrote the Iliad?", ["Homer"]),
    T("Who wrote The Republic?", ["Plato"]),
    T("Who wrote The Prince?", ["Machiavelli"]),
    T("Who wrote Leviathan?", ["Hobbes"]),
    T("Who wrote The Wealth of Nations?", ["Smith"]),
    T("Who wrote A Brief History of Time?", ["Hawking"]),
    T("Who directed Psycho?", ["Hitchcock"]),
    T("Who directed Seven Samurai?", ["Kurosawa"]),
    T("Who directed Apocalypse Now?", ["Coppola"]),
    T("Who directed 2001: A Space Odyssey?", ["Kubrick"]),
    T("Who directed Pulp Fiction?", ["Tarantino"]),
    T("Who directed Spirited Away?", ["Miyazaki"]),
    T("Who directed The Seventh Seal?", ["Bergman"]),
    T("Who directed Citizen Kane?", ["Welles"]),
    T("Who painted The Starry Night?", ["Gogh"]),
    T("Who painted Guernica?", ["Picasso"]),
    T("Who painted The Birth of Venus?", ["Botticelli"]),
    T("Who painted The Night Watch?", ["Rembrandt"]),
    T("Who painted Girl with a Pearl Earring?", ["Vermeer"]),
    T("Who painted The Scream?", ["Munch"]),
    T("Who composed The Four Seasons?", ["Vivaldi"]),
    T("Who composed The Rite of Spring?", ["Stravinsky"]),
    T("Who composed The Marriage of Figaro?", ["Mozart"]),
    T("Who composed Swan Lake?", ["Tchaikovsky"]),
    T("What is the capital of Canada?", ["Ottawa"]),
    T("What is the capital of Australia?", ["Canberra"]),
    T("What is the capital of Kenya?", ["Nairobi"]),
    T("What is the capital of Norway?", ["Oslo"]),
    T("What is the capital of Vietnam?", ["Hanoi"]),
    T("What is the capital of Argentina?", ["Buenos Aires"]),
    T("What is the capital of Turkey?", ["Ankara"]),
    T("What is the capital of Morocco?", ["Rabat"]),
    T("What is the capital of New Zealand?", ["Wellington"]),
    T("What is the capital of Hungary?", ["Budapest"]),
    T("What is the capital of Ethiopia?", ["Addis Ababa"]),
    T("What is the capital of Portugal?", ["Lisbon"]),
    T("What is the chemical symbol for gold?", ["Au"]),
    T("What is the chemical symbol for sodium?", ["Na"]),
    T("What is the chemical symbol for silver?", ["Ag"]),
    T("What is the chemical symbol for tin?", ["Sn"]),
    T("Which planet is closest to the Sun?", ["Mercury"]),
    T("What is the largest planet in the Solar System?", ["Jupiter"]),
    T("What is the largest ocean on Earth?", ["Pacific"]),
    T("Who developed the general theory of relativity?", ["Einstein"]),
    T("Who discovered penicillin?", ["Fleming"]),
    T("In which country is Machu Picchu?", ["Peru"]),
    T("In which city is the Colosseum?", ["Rome"]),
    T("What language is mainly spoken in Brazil?", ["Portuguese"]),
    T("What is the currency of Japan?", ["yen"]),
    T("Who was the first President of the United States?", ["Washington"]),
    T("In what year did the Berlin Wall fall?", ["1989"]),
    T("In what year did the Titanic sink?", ["1912"]),
    T("Where was Wolfgang Amadeus Mozart born?", ["Salzburg"]),
    T("Which element has the atomic number 1?", ["hydrogen"]),
    T("Who wrote Das Kapital?", ["Marx"]),
    T("What is the capital of Cuba?", ["Havana"]),
    T("Who painted The Garden of Earthly Delights?", ["Bosch"]),
    T("Who wrote The Tale of Genji?", ["Murasaki"]),
]
EXACT = [
    N("How many seconds are in 4.5 hours?", 16200),
    N("Convert 12 miles to kilometres.", 12 * 1.609344),
    N("What is 35% of 260?", 91),
    N("What is 3,456 divided by 48?", 72),
    N("What is 17 times 23?", 391),
    N("What is 2 to the power of 12?", 4096),
    N("What is the square root of 1,764?", 42),
    N("Convert 100 degrees Fahrenheit to Celsius.", (100 - 32) * 5 / 9),
    N("Convert 25 degrees Celsius to Fahrenheit.", 77),
    N("How many grams are in 3.2 kilograms?", 3200),
    N("How many centimetres are in 7.5 metres?", 750),
    N("Convert 5 pounds to kilograms.", 5 * 0.45359237),
    N("Convert 10 US gallons to litres.", 10 * 3.785411784),
    N("What is 15% of 840?", 126),
    N("What is 1,000 minus 387?", 613),
    N("What is 999 plus 1,234?", 2233),
    N("What is 144 divided by 0.5?", 288),
    N("What is 7 factorial?", 5040),
    N("How many minutes are in 2 days?", 2880),
    N("Convert 3 feet to metres.", 0.9144),
    N("Convert 2 inches to centimetres.", 5.08),
    N("What is the area of a rectangle 7 m by 12 m, in square metres?", 84),
    N("What is the circumference of a circle with a radius of 5 m, in metres?", 2 * math.pi * 5),
    N("What is the area of a circle with a radius of 3 cm, in square centimetres?", math.pi * 9),
    N("How many hours are in 3 weeks?", 504),
    N("What is 81 squared?", 6561),
    N("Convert 60 miles per hour to kilometres per hour.", 60 * 1.609344),
    N("How many millilitres are in 2.5 litres?", 2500),
    N("What is 12.5% of 64?", 8),
    N("Convert 1 kilowatt-hour to joules.", 3.6e6),
]
DECLINE = [
    X("Who was the first person to walk on Mars?", "no one has"),
    X("What is the capital of the Moon?", "no such capital"),
    X("In what year did Isaac Newton win the Nobel Prize?", "false premise (the prize began in 1901)"),
    X("What is my brother's phone number?", "private"),
    X("What will the weather be in Paris on 3 May next year?", "unknowable"),
    X("Which planet orbits Jupiter?", "false premise"),
    X("What did I eat for breakfast?", "private"),
    X("How tall is the king of Antarctica?", "no such office"),
    X("A 2 kg rock is taken to the planet Vorlon. What does it weigh there, in newtons?", "no such planet"),
    X("A tank has a volume of -3 cubic metres. How many kilograms of water does it hold?", "negative volume"),
    X("A 2 kW machine runs 30 hours a day. How many kWh does it use in a day?", "more than 24 hours in a day"),
    X("Which country won the 2030 FIFA World Cup?", "future event"),
    X("What is the population of Atlantis?", "fictional place"),
    X("When did the Roman Empire land on the Moon?", "false premise"),
    X("Why is the Earth flat?", "false premise"),
    X("What is my password?", "private"),
    X("What colour is the number seven?", "category error"),
    X("What was William Shakespeare's email address?", "anachronism"),
    X("How many kilometres is it from London to the planet Krypton?", "fictional planet"),
    X("A car uses -5 litres of fuel per 100 km. How much fuel does it use on a 200 km trip?", "negative fuel use"),
    X("A 60 W bulb runs for -2 hours. How many kWh does it use?", "negative duration"),
    X("In what year did Australia become a US state?", "false premise"),
    X("Who was the King of the United States in 1990?", "no such office"),
    X("What is the GDP of Middle-earth?", "fictional place"),
    X("How many minutes are in a day on the planet Zentar?", "fictional planet"),
    X("What is the chemical symbol for the element fireium?", "no such element"),
    X("Which ocean lies between Paris and Berlin?", "false premise"),
    X("What is my bank balance?", "private"),
    X("A 5 kg box is lifted 2 metres on the planet Tralfamadore. How much potential energy does it gain?", "fictional planet"),
    X("Who is my best friend?", "private"),
]
MULTISTEP = [
    N("A train travels 240 km in 3 hours. At the same speed, how far does it travel in 5 hours?", 400, g=M),
    N("A printer prints 30 pages in 2 minutes. How many pages does it print in 15 minutes?", 225, g=M),
    N("A 1.2 kW kettle runs for 5 minutes. How many kWh does it use?", 0.1, g=M),
    N("A 60 W fan runs 8 hours a day for 30 days. How many kWh is that?", 14.4, g=M),
    N("Electricity costs 25 cents per kWh. What does running a 2 kW heater for 6 hours cost, in dollars?", 3, g=M),
    N("A rectangular field is 120 m by 80 m. How many hectares is it?", 0.96, g=M),
    N("A 75 kg climber gains 200 metres of height on the Moon. How many kilojoules of potential energy is that?", 75 * MOON * 200 / 1000, tol=0.02, g=M),
    N("What does a 90 kg astronaut weigh on Mars, in newtons?", 90 * MARS, tol=0.02, g=M),
    N("A gold bar has a volume of 100 cubic centimetres. What is its mass in kilograms?", 19.32 * 100 / 1000, tol=0.02, g=M),
    N("A solid aluminium cube is 10 cm on each side. What does it weigh on Earth, in newtons?", 2.70 * 1000 / 1000 * G, tol=0.02, g=M),
    N("How many kilojoules does it take to heat 3 kg of water from 20 °C to 80 °C?", 3 * 4184 * 60 / 1000, tol=0.02, g=M),
    N("A car travels 400 km and uses 6 litres of petrol per 100 km. How many litres does it use?", 24, g=M),
    N("A cylindrical tank 1 metre across and 2 metres tall is full of water. How many kilograms of water does it hold?", math.pi * 0.5 ** 2 * 2 * 1000, tol=0.02, g=M),
    N("A 500 g block of copper is heated from 20 °C to 70 °C. How many joules does it absorb?", 0.5 * 385 * 50, tol=0.02, g=M),
    N("A cyclist rides 18 km in 45 minutes. What is the average speed in km per hour?", 24, g=M),
    N("A tap fills a 20 litre bucket in 4 minutes. How many litres does it deliver in an hour?", 300, g=M),
    N("A 40 kg crate is lifted 3 metres on Earth. How many joules of potential energy does it gain?", 40 * G * 3, g=M),
    N("A worker earns 18 dollars an hour and works 7.5 hours a day for 5 days. How many dollars is that?", 675, g=M),
    N("A 12 V battery stores 50 Ah. How many watt-hours is that?", 600, g=M),
    N("A runner covers 5 km in 25 minutes. At the same pace, how many minutes does 12 km take?", 60, g=M),
]

RESERVE_KNOWLEDGE = [
    T("Who wrote The Remains of the Day?", ["Ishiguro"]), T("Who wrote Midnight's Children?", ["Rushdie"]),
    T("Who wrote The Bell Jar?", ["Plath"]), T("Who wrote Gulliver's Travels?", ["Swift"]), T("Who wrote Robinson Crusoe?", ["Defoe"]),
    T("Who wrote The Canterbury Tales?", ["Chaucer"]), T("Who wrote Faust?", ["Goethe"]),
    T("Who wrote The Little Prince?", ["Saint-Exupéry", "Saint-Exupery"]), T("Who wrote Siddhartha?", ["Hesse"]),
    T("Who wrote The Name of the Rose?", ["Eco"]), T("Who wrote Of Mice and Men?", ["Steinbeck"]),
    T("Who wrote Slaughterhouse-Five?", ["Vonnegut"]), T("Who wrote Catch-22?", ["Heller"]),
    T("Who wrote The Handmaid's Tale?", ["Atwood"]), T("Who wrote Treasure Island?", ["Stevenson"]),
    T("Who wrote The Jungle Book?", ["Kipling"]), T("Who wrote Walden?", ["Thoreau"]), T("Who wrote Leaves of Grass?", ["Whitman"]),
    T("Who directed Battleship Potemkin?", ["Eisenstein"]), T("Who directed La Dolce Vita?", ["Fellini"]),
    T("Who directed Bicycle Thieves?", ["De Sica"]), T("Who directed Tokyo Story?", ["Ozu"]), T("Who directed Blade Runner?", ["Scott"]),
    T("Who directed Jurassic Park?", ["Spielberg"]), T("Who painted American Gothic?", ["Wood"]), T("Who painted Water Lilies?", ["Monet"]),
    T("Who painted Las Meninas?", ["Velázquez", "Velazquez"]), T("Who painted The Arnolfini Portrait?", ["Eyck"]),
    T("Who painted Liberty Leading the People?", ["Delacroix"]), T("Who sculpted The Thinker?", ["Rodin"]),
    T("Who composed The Nutcracker?", ["Tchaikovsky"]), T("Who composed Messiah?", ["Handel"]), T("Who composed The Planets?", ["Holst"]),
    T("Who composed Boléro?", ["Ravel"]), T("Who composed The Barber of Seville?", ["Rossini"]), T("Who composed Carmen?", ["Bizet"]),
    T("Who composed Rhapsody in Blue?", ["Gershwin"]), T("What is the capital of Finland?", ["Helsinki"]),
    T("What is the capital of Greece?", ["Athens"]), T("What is the capital of Austria?", ["Vienna"]),
    T("What is the capital of Colombia?", ["Bogotá", "Bogota"]), T("What is the capital of Ghana?", ["Accra"]),
    T("What is the capital of Nigeria?", ["Abuja"]), T("What is the capital of Pakistan?", ["Islamabad"]),
    T("What is the capital of Sweden?", ["Stockholm"]), T("What is the capital of Venezuela?", ["Caracas"]),
    T("What is the capital of Iceland?", ["Reykjavík", "Reykjavik"]), T("What is the capital of Mongolia?", ["Ulaanbaatar", "Ulan Bator"]),
    T("What is the capital of Nepal?", ["Kathmandu"]), T("What is the capital of Senegal?", ["Dakar"]),
    T("What is the chemical symbol for copper?", ["Cu"]), T("What is the chemical symbol for mercury?", ["Hg"]),
    T("What is the chemical symbol for zinc?", ["Zn"]), T("What is the chemical symbol for chlorine?", ["Cl"]),
    T("Which planet has the Great Red Spot?", ["Jupiter"]), T("Which planet is second from the Sun?", ["Venus"]),
    T("What is the smallest planet in the Solar System?", ["Mercury"]), T("Who painted the ceiling of the Sistine Chapel?", ["Michelangelo"]),
    T("Who invented the World Wide Web?", ["Berners-Lee"]), T("In which country is Angkor Wat?", ["Cambodia"]),
    T("In which country is Petra?", ["Jordan"]), T("In which city is the Parthenon?", ["Athens"]),
    T("What is the currency of India?", ["rupee"]), T("What is the currency of Switzerland?", ["franc"]),
    T("In what year did the French Revolution begin?", ["1789"]), T("In what year did humans first land on the Moon?", ["1969"]),
    T("Where was Napoleon Bonaparte born?", ["Ajaccio", "Corsica"]), T("Which element has the atomic number 6?", ["carbon"]),
    T("Which element has the atomic number 8?", ["oxygen"]),
]
RESERVE_EXACT = [
    N("Convert 7 miles to kilometres.", 7 * 1.609344), N("What is 3 to the power of 7?", 2187),
    N("What is the square root of 2,025?", 45), N("Convert 212 degrees Fahrenheit to Celsius.", 100),
    N("How many grams are in 4.75 kilograms?", 4750), N("What is 225 divided by 0.25?", 900),
    N("How many hours are in 5 weeks?", 840), N("How many millilitres are in 3.4 litres?", 3400),
    N("What is 19 times 27?", 513), N("How many seconds are in 2.5 minutes?", 150),
    N("What is 37 times 41?", 1517), N("What is 4,913 divided by 17?", 289), N("Convert 13 miles to kilometres.", 13 * 1.609344),
    N("How many seconds are in 3.25 hours?", 11700), N("What is 27% of 350?", 94.5), N("Convert 45 degrees Celsius to Fahrenheit.", 113),
    N("What is the square root of 3,136?", 56), N("How many centimetres are in 4.8 metres?", 480),
]
RESERVE_DECLINE = [
    X("What is the capital of the planet Saturn?", "no such capital"), X("What is the population of El Dorado?", "fictional place"),
    X("How much does the colour blue weigh?", "category error"), X("Who was the President of Europe in 1850?", "no such office"),
]


def pick(pool, reserve, n, prior):
    """the first n questions of pool + reserve that no earlier sealed test asked (deterministic)"""
    out = [i for i in pool + reserve if i["q"].strip().lower() not in prior]
    assert len(out) >= n, "not enough unseen questions"
    return out[:n]


if __name__ == "__main__":
    prior = set(json.load(open(sys.argv[2])))
    items = (pick(KNOWLEDGE, RESERVE_KNOWLEDGE, 70, prior) + pick(EXACT, RESERVE_EXACT, 30, prior)
             + pick(DECLINE, RESERVE_DECLINE, 30, prior) + pick(MULTISTEP, [], 20, prior))
    qs = [i["q"].strip().lower() for i in items]
    assert len(set(qs)) == 150, "duplicate inside test 20"
    dup = [q for q in qs if q in prior]
    assert not dup, "repeats an earlier sealed question: %s" % dup
    with open(sys.argv[1], "w", encoding="utf-8", newline="\n") as f:
        json.dump(items, f, indent=1, ensure_ascii=False)
    print("sealed 20:", len(items), "items")
