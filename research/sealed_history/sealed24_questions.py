"""sealed24_questions - SEALED TEST 24: the release gate for the FULL RELEASE 3.2 (head after w556: owner-first needs givens;
negative amounts withheld; evidence must name what the question names; arithmetic is not read from a sentence) and for
oracle7-slim 3.2 at the same head.
Written by Claude on 2026-10-19 BEFORE w556 was admitted and before the full release 3.2 answered any of it; same author -
disclosed. Test 23 is spent (3.2 slim released; 3.2 full held).
SINGLE part: 162 questions = the recipe and group sizes of tests 12-23 (70 knowledge, 30 exact, 30 must-decline, 20
multi-step) + a group of 12 for what the full 3.2 adds (orbits through owner-first, star and decay specialists, rate word
problems, and must-declines of the kinds w556 guards: negative amounts, an office that does not exist, a false premise
naming a real body). Each group is drawn in order from its pool, skipping any question an earlier sealed test (10-23) asked;
the draw is deterministic. New pools: tests 10-23 used up the old ones.
NO NUMERIC ITEM'S EXPECTED VALUE EQUALS A NUMBER THE QUESTION GIVES (asserted below): the scorer skips a reply number that
equals a given, so such an item can only be scored wrong (two of sealed 23's "wrong" answers were this).
Scoring = run_sealed23's rules unchanged (run_sealed24.py). Bars (unchanged): precision on answered >= 0.90, false yes <= 2,
zero format defects.
Constants: g Earth 9.80665, Moon 1.62, Mars 3.71 m/s2; densities g/cm3 gold 19.32, iron 7.874, water 1.000; specific heat
J/(kg K) water 4184, copper 385; 1 mile 1.609344 km; 1 lb 0.45359237 kg; 1 oz 28.349523125 g; 1 US gal 3.785411784 L;
1 inch 2.54 cm; 1 foot 0.3048 m. Orbits: GM Earth 398,600.4418 km3/s2, mean radius 6,371 km; GM Mars 42,828.37 km3/s2,
mean radius 3,389.5 km. Stars (IAU 2015): T_sun 5,772 K, R_sun 109.076 Earth radii; caesium-137 half-life 30.08 years."""
import json
import math
import re
import sys

E, M, K, D, F = "exact", "multistep", "knowledge", "decline", "full32"
N = lambda q, v, tol=0.01, g=E: {"q": q, "expect": v, "kind": "number", "tol": tol, "group": g, "valid": True}
T = lambda q, aliases, g=K: {"q": q, "expect": aliases, "kind": "text", "group": g, "valid": True}
X = lambda q, why, g=D: {"q": q, "expect": "decline", "kind": "decline", "group": g, "valid": False, "why": why}
G, MOON, MARS = 9.80665, 1.62, 3.71
TS, RE = 5772.0, 695700.0 / 6378.1
MU_E, R_E, MU_M, R_M = 398600.4418, 6371.0, 42828.37, 3389.5


def rr(*cats):
    """round-robin merge, so a draw of the first n mixes every kind"""
    out, i = [], 0
    while any(i < len(c) for c in cats):
        out += [c[i] for c in cats if i < len(c)]
        i += 1
    return out


AUTHORS = [T("Who wrote The Brothers Karamazov?", ["Dostoevsky", "Dostoyevsky"]), T("Who wrote Don Quixote?", ["Cervantes"]),
           T("Who wrote Ulysses?", ["Joyce"]), T("Who wrote Lolita?", ["Nabokov"]),
           T("Who wrote One Hundred Years of Solitude?", ["García Márquez", "Garcia Marquez", "Márquez", "Marquez"]),
           T("Who wrote The Trial?", ["Kafka"]), T("Who wrote Madame Bovary?", ["Flaubert"]), T("Who wrote The Stranger?", ["Camus"]),
           T("Who wrote Brave New World?", ["Huxley"]), T("Who wrote Fahrenheit 451?", ["Bradbury"]), T("Who wrote Jane Eyre?", ["Charlotte Brontë", "Charlotte Bronte", "Brontë", "Bronte"]),
           T("Who wrote Beloved?", ["Morrison"]), T("Who wrote The Hobbit?", ["Tolkien"]), T("Who wrote Treasure Island?", ["Stevenson"]),
           T("Who wrote Things Fall Apart?", ["Achebe"]), T("Who wrote The Bell Jar?", ["Plath"]), T("Who wrote Slaughterhouse-Five?", ["Vonnegut"]),
           T("Who wrote Catch-22?", ["Heller"]), T("Who wrote The Handmaid's Tale?", ["Atwood"]), T("Who wrote Little Women?", ["Alcott"]),
           T("Who wrote Walden?", ["Thoreau"]), T("Who wrote Leaves of Grass?", ["Whitman"]), T("Who wrote The Prince?", ["Machiavelli"]),
           T("Who wrote Siddhartha?", ["Hesse"]), T("Who wrote Doctor Zhivago?", ["Pasternak"]), T("Who wrote The Name of the Rose?", ["Eco"])]
DIRECTORS = [T("Who directed Vertigo?", ["Hitchcock"]), T("Who directed Seven Samurai?", ["Kurosawa"]), T("Who directed 2001: A Space Odyssey?", ["Kubrick"]),
             T("Who directed Pan's Labyrinth?", ["del Toro", "Del Toro"]), T("Who directed Jaws?", ["Spielberg"]), T("Who directed Taxi Driver?", ["Scorsese"]),
             T("Who directed Pulp Fiction?", ["Tarantino"]), T("Who directed Spirited Away?", ["Miyazaki"]), T("Who directed Metropolis?", ["Lang"]),
             T("Who directed Psycho?", ["Hitchcock"]), T("Who directed The Seventh Seal?", ["Bergman"]), T("Who directed La Dolce Vita?", ["Fellini"]),
             T("Who directed Blade Runner?", ["Scott"]), T("Who directed E.T. the Extra-Terrestrial?", ["Spielberg"])]
ART = [T("Who painted The Starry Night?", ["Van Gogh", "van Gogh"]), T("Who painted Guernica?", ["Picasso"]),
       T("Who painted The Persistence of Memory?", ["Dalí", "Dali"]), T("Who painted The Last Supper?", ["Leonardo", "da Vinci"]),
       T("Who painted The Birth of Venus?", ["Botticelli"]), T("Who painted The Scream?", ["Munch"]), T("Who painted Girl with a Pearl Earring?", ["Vermeer"]),
       T("Who painted The Night Watch?", ["Rembrandt"]), T("Who painted American Gothic?", ["Wood"])]
MUSIC = [T("Who composed The Four Seasons?", ["Vivaldi"]), T("Who composed Swan Lake?", ["Tchaikovsky"]), T("Who composed The Magic Flute?", ["Mozart"]),
         T("Who composed Carmen?", ["Bizet"]), T("Who composed La traviata?", ["Verdi"]), T("Who composed Boléro?", ["Ravel"]),
         T("Who composed The Rite of Spring?", ["Stravinsky"]), T("Who composed Rhapsody in Blue?", ["Gershwin"]), T("Who composed The Planets?", ["Holst"]),
         T("Who composed Messiah?", ["Handel", "Händel"])]
CAPITALS = [T("What is the capital of Kenya?", ["Nairobi"]), T("What is the capital of Peru?", ["Lima"]), T("What is the capital of Chile?", ["Santiago"]),
            T("What is the capital of Colombia?", ["Bogotá", "Bogota"]), T("What is the capital of Nigeria?", ["Abuja"]), T("What is the capital of Ethiopia?", ["Addis Ababa"]),
            T("What is the capital of Vietnam?", ["Hanoi"]), T("What is the capital of Thailand?", ["Bangkok"]), T("What is the capital of Indonesia?", ["Jakarta"]),
            T("What is the capital of the Philippines?", ["Manila"]), T("What is the capital of Iran?", ["Tehran"]), T("What is the capital of Iraq?", ["Baghdad"]),
            T("What is the capital of Saudi Arabia?", ["Riyadh"]), T("What is the capital of Pakistan?", ["Islamabad"]), T("What is the capital of Finland?", ["Helsinki"]),
            T("What is the capital of Hungary?", ["Budapest"]), T("What is the capital of Portugal?", ["Lisbon"]), T("What is the capital of Ireland?", ["Dublin"]),
            T("What is the capital of the Czech Republic?", ["Prague"]), T("What is the capital of Romania?", ["Bucharest"]), T("What is the capital of New Zealand?", ["Wellington"]),
            T("What is the capital of Morocco?", ["Rabat"]), T("What is the capital of Ghana?", ["Accra"]), T("What is the capital of Cuba?", ["Havana"]),
            T("What is the capital of Venezuela?", ["Caracas"])]
SCIENCE = [T("What is the chemical symbol for lead?", ["Pb"]), T("What is the chemical symbol for sodium?", ["Na"]), T("What is the chemical symbol for tin?", ["Sn"]),
           T("What is the chemical symbol for mercury?", ["Hg"]), T("What is the chemical symbol for zinc?", ["Zn"]), T("What is the chemical symbol for calcium?", ["Ca"]),
           T("What is the chemical symbol for chlorine?", ["Cl"]), T("What is the chemical symbol for platinum?", ["Pt"]),
           T("Which planet has the moon Io?", ["Jupiter"]), T("Which planet has the moon Triton?", ["Neptune"]), T("Which planet has the moon Miranda?", ["Uranus"]),
           T("Which planet has the moon Enceladus?", ["Saturn"]), T("Which planet has the moon Phobos?", ["Mars"]), T("What is the largest moon of Neptune?", ["Triton"]),
           T("What is the largest moon of Uranus?", ["Titania"])]
CURRENCY = [T("Which currency is used in Switzerland?", ["franc"]), T("Which currency is used in India?", ["rupee"]), T("Which currency is used in Mexico?", ["peso"]),
            T("Which currency is used in South Africa?", ["rand"]), T("Which currency is used in Poland?", ["złoty", "zloty"]), T("Which currency is used in Turkey?", ["lira"]),
            T("Which currency is used in South Korea?", ["won"]), T("Which currency is used in Brazil?", ["real"]), T("Which currency is used in Sweden?", ["krona"]),
            T("Which currency is used in Russia?", ["ruble", "rouble"])]
LANGUAGE = [T("What is the official language of Brazil?", ["Portuguese"]), T("What is the official language of Iran?", ["Persian", "Farsi"]),
            T("What is the official language of Ethiopia?", ["Amharic"]), T("What is the official language of Israel?", ["Hebrew"]),
            T("What is the official language of Argentina?", ["Spanish"]), T("What is the official language of Austria?", ["German"]),
            T("What is the official language of Greece?", ["Greek"]), T("What is the official language of Hungary?", ["Hungarian"])]
CITY = [T("In which country is the city of Marrakesh located?", ["Morocco"]), T("In which country is the city of Kyoto located?", ["Japan"]),
        T("In which country is the city of Kraków located?", ["Poland"]), T("In which country is the city of Porto located?", ["Portugal"]),
        T("In which country is the city of Seville located?", ["Spain"]), T("In which country is the city of Mumbai located?", ["India"]),
        T("In which country is the city of Timbuktu located?", ["Mali"]), T("In which country is the city of Salzburg located?", ["Austria"]),
        T("In which country is the city of Antwerp located?", ["Belgium"]), T("In which country is the city of Valparaíso located?", ["Chile"])]
CONTINENT = [T("On which continent is Mongolia?", ["Asia"]), T("On which continent is Paraguay?", ["South America"]), T("On which continent is Madagascar?", ["Africa"]),
             T("On which continent is Iceland?", ["Europe"]), T("On which continent is Bolivia?", ["South America"]), T("On which continent is Nepal?", ["Asia"])]
INVENT = [T("Who invented the telephone?", ["Bell"]), T("Who invented the phonograph?", ["Edison"]), T("Who invented the World Wide Web?", ["Berners-Lee"]),
          T("Who invented dynamite?", ["Nobel"]), T("Who invented the printing press?", ["Gutenberg"]), T("Who invented the cotton gin?", ["Whitney"]),
          T("Who discovered penicillin?", ["Fleming"]), T("Who discovered radium?", ["Curie"]), T("Who discovered the electron?", ["Thomson"]),
          T("Who discovered Pluto?", ["Tombaugh"]), T("Who proposed the theory of evolution by natural selection?", ["Darwin"])]
GEO = [T("What is the longest river in Africa?", ["Nile"]), T("What is the highest mountain in Africa?", ["Kilimanjaro"]), T("What is the largest ocean?", ["Pacific"]),
       T("Which ocean lies between Africa and Australia?", ["Indian"]), T("What is the highest mountain in South America?", ["Aconcagua"]),
       T("What is the longest river in South America?", ["Amazon"]), T("Which strait separates Spain and Morocco?", ["Gibraltar"]),
       T("What is the largest island in the Mediterranean Sea?", ["Sicily"]), T("Which river flows through Vienna?", ["Danube"]),
       T("Which river flows through Baghdad?", ["Tigris"]), T("Which river flows through London?", ["Thames"])]
ELEMENTS = [T("Which element has the atomic number 6?", ["carbon"]), T("Which element has the atomic number 8?", ["oxygen"]),
            T("Which element has the atomic number 26?", ["iron"]), T("Which element has the atomic number 79?", ["gold"]),
            T("Which element has the atomic number 1?", ["hydrogen"]), T("What is the hardest natural mineral?", ["diamond"]),
            T("Which planet is closest to the Sun?", ["Mercury"]), T("Which planet is known as the Red Planet?", ["Mars"]),
            T("What is the largest planet in the Solar System?", ["Jupiter"])]
HISTORY = [T("Who was the first president of the United States?", ["Washington"]), T("Who was the first person in space?", ["Gagarin"]),
           T("Who painted the ceiling of the Sistine Chapel?", ["Michelangelo"]), T("Which empire built Machu Picchu?", ["Inca"]),
           T("Which city was the capital of the Byzantine Empire?", ["Constantinople"]), T("Who led the Salt March in 1930?", ["Gandhi"]),
           T("Who co-wrote The Communist Manifesto with Karl Marx?", ["Engels"]), T("Which ship sank in 1912 after hitting an iceberg?", ["Titanic"]),
           T("Who was the Greek god of the sea?", ["Poseidon"])]
LETTERS = [T("Who wrote The Tale of Genji?", ["Murasaki"]), T("Who wrote The Waste Land?", ["Eliot"]), T("Who wrote The Master and Margarita?", ["Bulgakov"]),
           T("Who wrote Dead Souls?", ["Gogol"]), T("Who wrote The Magic Mountain?", ["Mann"]), T("Who wrote Germinal?", ["Zola"]), T("Who wrote Ivanhoe?", ["Scott"]),
           T("Who wrote The Jungle Book?", ["Kipling"]), T("Who wrote Gone with the Wind?", ["Mitchell"]), T("Who wrote The Call of the Wild?", ["London"]),
           T("Who wrote A Doll's House?", ["Ibsen"]), T("Who wrote Waiting for Godot?", ["Beckett"]), T("Who wrote The Cherry Orchard?", ["Chekhov"]),
           T("Who wrote Death of a Salesman?", ["Miller"]), T("Who wrote A Streetcar Named Desire?", ["Williams"])]
MAKERS = [T("Who sculpted The Thinker?", ["Rodin"]), T("Who designed the Statue of Liberty?", ["Bartholdi"]), T("Who designed the Sydney Opera House?", ["Utzon"]),
          T("Who designed Fallingwater?", ["Wright"]), T("Who designed the Guggenheim Museum Bilbao?", ["Gehry"]),
          T("Which country gave the Statue of Liberty to the United States?", ["France"]), T("Who composed the opera Aida?", ["Verdi"]),
          T("Who composed the Moonlight Sonata?", ["Beethoven"]), T("Who composed The Lark Ascending?", ["Vaughan Williams"]),
          T("Who composed the opera The Barber of Seville?", ["Rossini"])]
PLACES = [T("In which city is the Colosseum?", ["Rome"]), T("In which city is the Acropolis?", ["Athens"]), T("In which city is the Taj Mahal?", ["Agra"]),
          T("In which city is the Alhambra?", ["Granada"]), T("In which city is the Brandenburg Gate?", ["Berlin"]),
          T("In which city is the Golden Gate Bridge?", ["San Francisco"]), T("In which city is Big Ben?", ["London"]),
          T("In which city is the Hagia Sophia?", ["Istanbul"]), T("In which city is the Forbidden City?", ["Beijing"]),
          T("In which city is the Sagrada Família?", ["Barcelona"]), T("What is the smallest planet in the Solar System?", ["Mercury"])]
KNOWLEDGE = rr(AUTHORS, DIRECTORS, ART, MUSIC, CAPITALS, SCIENCE, CURRENCY, LANGUAGE, CITY, CONTINENT, INVENT, GEO, ELEMENTS, HISTORY, LETTERS, MAKERS, PLACES)

EXACT = [
    N("How many seconds are in 23 minutes?", 1380), N("Convert 65 miles to kilometres.", 65 * 1.609344), N("What is 35% of 840?", 294),
    N("What is 7,776 divided by 96?", 81), N("What is 58 times 37?", 2146), N("What is 3 to the power of 7?", 2187),
    N("What is the square root of 6,889?", 83), N("Convert 113 degrees Fahrenheit to Celsius.", 45), N("Convert 25 degrees Celsius to Fahrenheit.", 77),
    N("How many grams are in 3.75 kilograms?", 3750), N("How many centimetres are in 4.6 metres?", 460), N("Convert 80 pounds to kilograms.", 80 * 0.45359237),
    N("Convert 5 US gallons to litres.", 5 * 3.785411784), N("What is 12% of 950?", 114), N("What is 8,000 minus 2,468?", 5532),
    N("What is 3,456 plus 6,789?", 10245), N("What is 630 divided by 0.7?", 900), N("What is 7 factorial?", 5040),
    N("Convert 30 feet to metres.", 30 * 0.3048), N("Convert 9 inches to centimetres.", 22.86),
    N("What is the area of a rectangle 18 m by 26 m, in square metres?", 468),
    N("What is the circumference of a circle with a radius of 9 m, in metres?", 2 * math.pi * 9),
    N("What is the area of a circle with a radius of 6 cm, in square centimetres?", math.pi * 36), N("How many days are in 23 weeks?", 161),
    N("What is 67 squared?", 4489), N("Convert 90 kilometres per hour to miles per hour.", 90 / 1.609344), N("How many millilitres are in 2.4 litres?", 2400),
    N("What is 62.5% of 128?", 80), N("Convert 3 kilowatt-hours to joules.", 1.08e7), N("What is 43 times 59?", 2537),
    N("What is 2 to the power of 13?", 8192), N("What is the square root of 7,056?", 84), N("How many minutes are in 3.75 hours?", 225),
    N("How many seconds are in 1.25 hours?", 4500), N("Convert 12 ounces to grams.", 12 * 28.349523125), N("What is 27 times 33?", 891),
    N("What is 1,000,000 divided by 125?", 8000), N("Convert 15 kilometres to miles.", 15 / 1.609344), N("What is 48% of 250?", 120),
    N("How many hours are in 3 weeks?", 504),
    N("How many seconds are in 37 minutes?", 2220), N("What is 46 times 52?", 2392), N("What is 9% of 1,400?", 126),
    N("What is 5,040 divided by 35?", 144), N("What is 4 to the power of 6?", 4096), N("What is the square root of 2,601?", 51),
    N("Convert 59 degrees Fahrenheit to Celsius.", 15), N("Convert 30 degrees Celsius to Fahrenheit.", 86), N("How many grams are in 0.85 kilograms?", 850),
    N("Convert 26 miles to kilometres.", 26 * 1.609344), N("What is 7,500 minus 4,875?", 2625), N("Convert 45 kilograms to pounds.", 45 / 0.45359237),
    N("How many days are in 31 weeks?", 217), N("What is 89 squared?", 7921), N("Convert 2.5 kilowatt-hours to megajoules.", 9),
    N("What is 15% of 2,460?", 369),
]
DECLINE = rr(
    [X("In what year did Mozart visit Mars?", "false premise"), X("When did Shakespeare land on Jupiter?", "false premise"),
     X("Which sea lies between Paris and Prague?", "false premise"), X("In what year did Canada become a Spanish colony?", "false premise"),
     X("Why is the Sun cold?", "false premise"), X("Who was the first person to walk on Mercury?", "false premise"),
     X("In what year did Isaac Newton visit Uranus?", "false premise")],
    [X("What is my sister's birthday?", "private"), X("What is my bank balance?", "private"), X("Where did I park my car?", "private"),
     X("What is my doctor's name?", "private"), X("What did I have for breakfast?", "private"), X("What is my wifi password?", "private")],
    [X("What is the population of Wakanda?", "fictional place"), X("How many moons does the planet Vulcan have?", "fictional planet"),
     X("A 10 kg crate is taken to the planet Tatooine. What does it weigh there, in newtons?", "fictional planet"),
     X("How far is it from London to the planet Arrakis?", "fictional planet"), X("What is the GDP of Atlantis?", "fictional place"),
     X("How many hours are in a day on the planet Gallifrey?", "fictional planet")],
    [X("A 60 W fan runs for -3 hours. How many kWh does it use?", "negative duration"),
     X("A recipe needs -200 grams of flour for 4 people. How much flour is needed for 6 people?", "negative mass"),
     X("A tank holds -50 litres of water. How many millilitres is that?", "negative volume"),
     X("A worker earns 20 dollars an hour for -8 hours. How many dollars is that?", "negative duration"),
     X("A heater runs 30 hours a day. How many hours does it run in a week?", "more than 24 hours in a day")],
    [X("Who was the Emperor of Australia in 1990?", "no such office"), X("What is the capital of the Atlantic Ocean?", "no such capital"),
     X("Who is the king of the Sahara Desert?", "no such office"), X("How tall is the president of the Arctic Ocean?", "no such office"),
     X("Who won the 2041 World Cup?", "future event"), X("What was Cleopatra's email address?", "anachronism"),
     X("In what year did the Roman Empire launch its first satellite?", "anachronism"), X("How much does the colour blue weigh?", "category error"),
     X("What is the chemical symbol for the element vibranium?", "no such element")],
    [X("In what year did Beethoven visit Venus?", "false premise"), X("What is my mother's maiden name?", "private"),
     X("What is the population of Middle-earth?", "fictional place"), X("A 50 W radio plays for -6 hours. How many kWh does it use?", "negative duration"),
     X("Who was the first king of the Atlantic Ocean?", "no such office"), X("What was Napoleon's mobile phone number?", "anachronism"),
     X("How many legs does the number nine have?", "category error"), X("What is the boiling point of the element kryptonite?", "no such element")])

MULTISTEP = [
    N("A train travels 240 km in 3 hours. At the same speed, how far does it travel in 5 hours?", 400, g=M),
    N("A printer prints 45 pages in 3 minutes. How many pages does it print in 16 minutes?", 240, g=M),
    N("A 2 kW kettle runs for 6 minutes. How many kWh does it use?", 0.2, g=M),
    N("A 60 W lamp runs 5 hours a day for 30 days. How many kWh is that?", 9, g=M),
    N("Electricity costs 25 cents per kWh. What does running a 2 kW heater for 3 hours cost, in dollars?", 1.5, g=M),
    N("A rectangular field is 400 m by 150 m. How many hectares is it?", 6, g=M),
    N("A 60 kg climber gains 200 metres of height on Earth. How many kilojoules of potential energy is that?", 60 * G * 200 / 1000, tol=0.02, g=M),
    N("What does a 90 kg astronaut weigh on Mars, in newtons?", 90 * MARS, tol=0.02, g=M),
    N("A gold coin has a volume of 2 cubic centimetres. What is its mass in grams?", 2 * 19.32, tol=0.02, g=M),
    N("An iron block has a volume of 300 cubic centimetres. What is its mass in kilograms?", 300 * 7.874 / 1000, tol=0.02, g=M),
    N("How many kilojoules does it take to heat 3 kg of water from 20 °C to 60 °C?", 3 * 4184 * 40 / 1000, tol=0.02, g=M),
    N("A car travels 420 km and uses 6 litres of petrol per 100 km. How many litres does it use?", 25.2, g=M),
    N("A 3 kg block of copper is heated from 20 °C to 50 °C. How many joules does it absorb?", 3 * 385 * 30, tol=0.02, g=M),
    N("A runner covers 21 km in 1.75 hours. What is the average speed in km per hour?", 12, g=M),
    N("A pump fills a 300 litre tank in 6 minutes. How many litres does it deliver in an hour?", 3000, g=M),
    N("A 40 kg sack is lifted 5 metres on Earth. How many joules of potential energy does it gain?", 40 * G * 5, g=M),
    N("A gardener earns 25 dollars an hour and works 6 hours a day for 3 days. How many dollars is that?", 450, g=M),
    N("A 12 V battery stores 80 Ah. How many watt-hours is that?", 960, g=M),
    N("A cyclist covers 12 km in 40 minutes. At the same pace, how many minutes does 21 km take?", 70, g=M),
    N("A 1,500 W heater runs for 40 minutes. How many kWh is that?", 1, g=M),
    N("An 800 W microwave runs for 9 minutes. How many kWh is that?", 0.12, g=M),
    N("What does a 120 kg crate weigh on the Moon, in newtons?", 120 * MOON, tol=0.02, g=M),
    N("An athlete runs 100 m in 12.5 seconds. What is the speed in km per hour?", 28.8, g=M),
    N("A swimmer covers 1,500 m in 25 minutes. At the same pace, how many minutes do 2,400 m take?", 40, g=M),
    N("A bakery sells 120 loaves a day at 5 dollars each. How many dollars does it take in over 7 days?", 4200, g=M),
    N("A cube-shaped tank 20 cm on each side is full of water. How many kilograms of water does it hold?", 8, g=M),
    N("A 5 kg stone is lifted 10 metres on the Moon. How many joules of potential energy does it gain?", 5 * MOON * 10, g=M),
    N("A truck travels 90 km in 1.5 hours. At the same speed, how many hours does 300 km take?", 5, g=M),
]


def period_min(mu, r):
    return 2 * math.pi * math.sqrt(r ** 3 / mu) / 60.0


FULL32 = [
    N("What is the orbital period, in minutes, of a satellite in a circular orbit 500 km above Earth?", period_min(MU_E, R_E + 500), tol=0.02, g=F),
    N("What is the orbital speed, in km/s, of a satellite in a circular orbit 400 km above Earth?", math.sqrt(MU_E / (R_E + 400)), tol=0.02, g=F),
    N("What is the orbital period, in minutes, of a circular orbit 300 km above Mars?", period_min(MU_M, R_M + 300), tol=0.02, g=F),
    N("What is the luminosity of a star with a radius of 0.7 solar radii and a temperature of 4,500 K?", 0.49 * (4500 / TS) ** 4, g=F),
    N("A planet transits a star of 0.5 solar radii with a depth of 1,600 ppm. What is the planet's radius in Earth radii?", 0.5 * math.sqrt(1600e-6) * RE, g=F),
    N("A sample has 80 g of caesium-137. How much remains after 60.16 years, in milligrams?", 20000, g=F),
    N("A cyclist covers 15 km in 45 minutes. At the same pace, how many minutes does 25 km take?", 75, g=F),
    N("A pump moves 40 litres in 8 minutes. At the same rate, how many minutes do 150 litres take?", 30, g=F),
    X("A 75 W lamp runs for -4 hours. How many kWh does it use?", "negative duration", g=F),
    X("A truck carries -300 kg of sand. How many grams is that?", "negative mass", g=F),
    X("How old is the queen of the Pacific Ocean?", "no such office", g=F),
    X("In what year did Galileo visit Saturn?", "false premise", g=F),
]

NUMRX = re.compile(r"\d[\d,]*(?:\.\d+)?")


def given_clash(it):
    """a numeric item whose expected value equals a number in its own question: the scorer would skip the right answer"""
    if it["kind"] != "number":
        return False
    for m in NUMRX.findall(it["q"]):
        g = float(m.replace(",", ""))
        if abs(g - it["expect"]) <= 1e-9 * max(1.0, abs(g)):
            return True
    return False


def pick(pool, n, prior):
    """the first n questions of the pool that no earlier sealed test asked (deterministic)"""
    out = [i for i in pool if i["q"].strip().lower() not in prior]
    assert len(out) >= n, "not enough unseen questions: %d < %d" % (len(out), n)
    return out[:n]


if __name__ == "__main__":
    prior = set(json.load(open(sys.argv[2])))
    items = pick(KNOWLEDGE, 70, prior) + pick(EXACT, 30, prior) + pick(DECLINE, 30, prior) + pick(MULTISTEP, 20, prior) + pick(FULL32, 12, prior)
    clash = [i["q"] for i in items if given_clash(i)]
    assert not clash, "expected value equals a given: %s" % clash
    qs = [i["q"].strip().lower() for i in items]
    assert len(set(qs)) == 162, "duplicate inside test 24"
    with open(sys.argv[1], "w", encoding="utf-8", newline="\n") as f:
        json.dump(items, f, indent=1, ensure_ascii=False)
    print("sealed 24:", len(items), "items")
