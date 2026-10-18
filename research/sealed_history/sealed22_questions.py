"""sealed22_questions - SEALED TEST 22: the release gate for RELEASE 3.1 (head after w546-w548: network v6 with learned operations,
the 3.1 correctness rules, the specialist after a check; and the fold worker's own admitted folds since patch 3, w416 onward).
Written by Claude on 2026-10-17 AFTER those folds were frozen (submitted to the gate) and BEFORE release 3.1 answered any of it;
same author - disclosed. Test 21 is spent (patch 3).
SINGLE part: 150 questions, the recipe and group sizes of tests 12-21 (70 knowledge, 30 exact, 30 must-decline, 20 multi-step).
Each group is drawn in order from its pool, skipping any question an earlier sealed test (10-21) asked; the pools are new and
fixed here, so the draw is deterministic. Scoring = run_sealed19's rules unchanged (run_sealed22.py).
Bars (unchanged): precision on answered >= 0.90, false yes <= 2, zero format defects.
Constants: g Earth 9.80665, Moon 1.62, Mars 3.71 m/s2; densities g/cm3 gold 19.32, iron 7.874, water 1.000; specific heat
J/(kg K) water 4184, copper 385; 1 mile 1.609344 km; 1 lb 0.45359237 kg; 1 oz 28.349523125 g; 1 US gal 3.785411784 L;
1 inch 2.54 cm; 1 foot 0.3048 m."""
import json
import math
import sys

E, M, K, D = "exact", "multistep", "knowledge", "decline"
N = lambda q, v, tol=0.01, g=E: {"q": q, "expect": v, "kind": "number", "tol": tol, "group": g, "valid": True}
T = lambda q, aliases, g=K: {"q": q, "expect": aliases, "kind": "text", "group": g, "valid": True}
X = lambda q, why: {"q": q, "expect": "decline", "kind": "decline", "group": D, "valid": False, "why": why}
G, MOON, MARS = 9.80665, 1.62, 3.71

KNOWLEDGE = [
    T("Who wrote Middlemarch?", ["Eliot"]), T("Who wrote The Bell Jar?", ["Plath"]), T("Who wrote Catch-22?", ["Heller"]),
    T("Who wrote Slaughterhouse-Five?", ["Vonnegut"]), T("Who wrote The Remains of the Day?", ["Ishiguro"]),
    T("Who wrote The Name of the Rose?", ["Eco"]), T("Who wrote One Hundred Years of Solitude?", ["García Márquez", "Garcia Marquez", "Márquez", "Marquez"]),
    T("Who wrote The Brothers Karamazov?", ["Dostoevsky", "Dostoyevsky"]), T("Who wrote Madame Bovary?", ["Flaubert"]),
    T("Who wrote Things Fall Apart?", ["Achebe"]), T("Who wrote Beloved?", ["Morrison"]), T("Who wrote The Trial?", ["Kafka"]),
    T("Who wrote Brave New World?", ["Huxley"]), T("Who wrote Fahrenheit 451?", ["Bradbury"]), T("Who wrote The Handmaid's Tale?", ["Atwood"]),
    T("Who wrote Jane Eyre?", ["Charlotte Brontë", "Charlotte Bronte", "Brontë", "Bronte"]), T("Who wrote Ulysses?", ["Joyce"]),
    T("Who wrote Don Quixote?", ["Cervantes"]), T("Who wrote The Stranger?", ["Camus"]), T("Who wrote Lolita?", ["Nabokov"]),
    T("Who directed Seven Samurai?", ["Kurosawa"]), T("Who directed 2001: A Space Odyssey?", ["Kubrick"]), T("Who directed Vertigo?", ["Hitchcock"]),
    T("Who directed Spirited Away?", ["Miyazaki"]), T("Who directed Taxi Driver?", ["Scorsese"]), T("Who directed Pulp Fiction?", ["Tarantino"]),
    T("Who directed The Seventh Seal?", ["Bergman"]), T("Who directed Bicycle Thieves?", ["De Sica", "de Sica"]), T("Who directed Metropolis?", ["Lang"]),
    T("Who directed Jaws?", ["Spielberg"]), T("Who directed Blade Runner?", ["Scott"]), T("Who directed Psycho?", ["Hitchcock"]),
    T("Who painted The Starry Night?", ["Van Gogh", "van Gogh"]), T("Who painted Guernica?", ["Picasso"]), T("Who painted The Last Supper?", ["Leonardo", "da Vinci"]),
    T("Who painted The Persistence of Memory?", ["Dalí", "Dali"]), T("Who painted Girl with a Pearl Earring?", ["Vermeer"]),
    T("Who painted The Night Watch?", ["Rembrandt"]), T("Who painted The Birth of Venus?", ["Botticelli"]), T("Who painted The Scream?", ["Munch"]),
    T("Who painted The Kiss?", ["Klimt"]), T("Who painted American Gothic?", ["Wood"]),
    T("Who composed The Four Seasons?", ["Vivaldi"]), T("Who composed The Rite of Spring?", ["Stravinsky"]), T("Who composed Boléro?", ["Ravel"]),
    T("Who composed The Magic Flute?", ["Mozart"]), T("Who composed the Moonlight Sonata?", ["Beethoven"]), T("Who composed Swan Lake?", ["Tchaikovsky"]),
    T("Who composed The Planets?", ["Holst"]), T("Who composed Rhapsody in Blue?", ["Gershwin"]), T("Who composed La traviata?", ["Verdi"]),
    T("What is the capital of Peru?", ["Lima"]), T("What is the capital of Chile?", ["Santiago"]), T("What is the capital of Colombia?", ["Bogotá", "Bogota"]),
    T("What is the capital of Venezuela?", ["Caracas"]), T("What is the capital of Bolivia?", ["Sucre", "La Paz"]), T("What is the capital of Cuba?", ["Havana"]),
    T("What is the capital of Kenya?", ["Nairobi"]), T("What is the capital of Ethiopia?", ["Addis Ababa"]), T("What is the capital of Ghana?", ["Accra"]),
    T("What is the capital of Nigeria?", ["Abuja"]), T("What is the capital of Senegal?", ["Dakar"]), T("What is the capital of Morocco?", ["Rabat"]),
    T("What is the capital of Vietnam?", ["Hanoi"]), T("What is the capital of Thailand?", ["Bangkok"]), T("What is the capital of Indonesia?", ["Jakarta"]),
    T("What is the capital of Pakistan?", ["Islamabad"]), T("What is the capital of Nepal?", ["Kathmandu"]), T("What is the capital of Mongolia?", ["Ulaanbaatar", "Ulan Bator"]),
    T("What is the capital of Iran?", ["Tehran"]), T("What is the capital of Finland?", ["Helsinki"]), T("What is the capital of Hungary?", ["Budapest"]),
    T("What is the capital of Portugal?", ["Lisbon"]), T("What is the capital of Ireland?", ["Dublin"]), T("What is the capital of Iceland?", ["Reykjavík", "Reykjavik"]),
    T("What is the chemical symbol for potassium?", ["K"]), T("What is the chemical symbol for sodium?", ["Na"]), T("What is the chemical symbol for tin?", ["Sn"]),
    T("What is the chemical symbol for lead?", ["Pb"]), T("What is the chemical symbol for mercury?", ["Hg"]), T("What is the chemical symbol for tungsten?", ["W"]),
    T("What is the largest moon of Neptune?", ["Triton"]), T("Which planet is closest to the Sun?", ["Mercury"]),    T("Who wrote The Leopard?", ["Lampedusa"]), T("Who wrote Pedro Páramo?", ["Rulfo"]), T("Who wrote Siddhartha?", ["Hesse"]),
    T("Who wrote The Magic Mountain?", ["Mann"]), T("Who wrote Germinal?", ["Zola"]), T("Who wrote The Red and the Black?", ["Stendhal"]),
    T("Who wrote Dead Souls?", ["Gogol"]), T("Who wrote Fathers and Sons?", ["Turgenev"]), T("Who wrote Blindness?", ["Saramago"]),
    T("Who wrote The Book of Disquiet?", ["Pessoa"]), T("Who wrote Ficciones?", ["Borges"]), T("Who wrote Hopscotch?", ["Cortázar", "Cortazar"]),
    T("Who wrote The Tale of Genji?", ["Murasaki"]), T("Who wrote Snow Country?", ["Kawabata"]), T("Who wrote Wide Sargasso Sea?", ["Rhys"]),
    T("Who wrote A Passage to India?", ["Forster"]), T("Who wrote Under the Volcano?", ["Lowry"]), T("Who wrote The Sea, the Sea?", ["Murdoch"]),
    T("Who wrote Gilead?", ["Robinson"]), T("Who wrote White Noise?", ["DeLillo"]), T("Who wrote Infinite Jest?", ["Wallace"]),
    T("Who wrote The Corrections?", ["Franzen"]), T("Who wrote Season of Migration to the North?", ["Salih"]), T("Who wrote The Sound of Waves?", ["Mishima"]),
    T("Who wrote The Good Soldier?", ["Ford"]), T("Who wrote The Age of Innocence?", ["Wharton"]), T("Who wrote My Ántonia?", ["Cather"]),
    T("Who wrote Native Son?", ["Wright"]), T("Who wrote Their Eyes Were Watching God?", ["Hurston"]), T("Who wrote Rabbit, Run?", ["Updike"]),
    T("Who directed Tokyo Story?", ["Ozu"]), T("Who directed The 400 Blows?", ["Truffaut"]), T("Who directed Breathless?", ["Godard"]),
    T("Who directed La Dolce Vita?", ["Fellini"]), T("Who directed Stalker?", ["Tarkovsky"]), T("Who directed Persona?", ["Bergman"]),
    T("Who directed Battleship Potemkin?", ["Eisenstein"]), T("Who directed Nosferatu?", ["Murnau"]), T("Who directed The Rules of the Game?", ["Renoir"]),
    T("Who directed Aguirre, the Wrath of God?", ["Herzog"]), T("Who directed Wings of Desire?", ["Wenders"]), T("Who directed In the Mood for Love?", ["Wong"]),
    T("Who directed Pather Panchali?", ["Ray"]), T("Who directed Fitzcarraldo?", ["Herzog"]), T("Who directed L'Avventura?", ["Antonioni"]),
    T("Who directed The Battle of Algiers?", ["Pontecorvo"]), T("Who directed Paths of Glory?", ["Kubrick"]), T("Who directed Sunset Boulevard?", ["Wilder"]),
    T("Who painted The Garden of Earthly Delights?", ["Bosch"]), T("Who painted Las Meninas?", ["Velázquez", "Velazquez"]),
    T("Who painted The Arnolfini Portrait?", ["van Eyck", "Van Eyck"]), T("Who painted Liberty Leading the People?", ["Delacroix"]),
    T("Who painted The Raft of the Medusa?", ["Géricault", "Gericault"]), T("Who painted Wanderer above the Sea of Fog?", ["Friedrich"]),
    T("Who painted A Sunday Afternoon on the Island of La Grande Jatte?", ["Seurat"]), T("Who painted Olympia?", ["Manet"]),
    T("Who painted The Gleaners?", ["Millet"]), T("Who painted The Ambassadors?", ["Holbein"]), T("Who painted The Swing?", ["Fragonard"]),
    T("Who composed The Barber of Seville?", ["Rossini"]), T("Who composed Madama Butterfly?", ["Puccini"]), T("Who composed Messiah?", ["Handel"]),
    T("Who composed The Creation?", ["Haydn"]), T("Who composed Symphonie fantastique?", ["Berlioz"]), T("Who composed Carmen?", ["Bizet"]),
    T("Who composed Pomp and Circumstance?", ["Elgar"]), T("Who composed Appalachian Spring?", ["Copland"]), T("Who composed The Moldau?", ["Smetana"]),
    T("Who composed Ride of the Valkyries?", ["Wagner"]), T("Who composed Don Giovanni?", ["Mozart"]), T("Who composed Aida?", ["Verdi"]),
    T("What is the capital of Kazakhstan?", ["Astana"]), T("What is the capital of Uzbekistan?", ["Tashkent"]), T("What is the capital of Kyrgyzstan?", ["Bishkek"]),
    T("What is the capital of Tajikistan?", ["Dushanbe"]), T("What is the capital of Moldova?", ["Chișinău", "Chisinau"]), T("What is the capital of Belarus?", ["Minsk"]),
    T("What is the capital of Cambodia?", ["Phnom Penh"]), T("What is the capital of Laos?", ["Vientiane"]), T("What is the capital of Namibia?", ["Windhoek"]),
    T("What is the capital of Botswana?", ["Gaborone"]), T("What is the capital of Rwanda?", ["Kigali"]), T("What is the capital of Mali?", ["Bamako"]),
    T("What is the capital of Niger?", ["Niamey"]), T("What is the capital of Honduras?", ["Tegucigalpa"]), T("What is the capital of Nicaragua?", ["Managua"]),
    T("What is the capital of Costa Rica?", ["San José", "San Jose"]), T("What is the capital of Fiji?", ["Suva"]), T("What is the capital of New Zealand?", ["Wellington"]),
    T("What is the capital of Bhutan?", ["Thimphu"]), T("What is the capital of Brunei?", ["Bandar Seri Begawan"]), T("What is the capital of Burkina Faso?", ["Ouagadougou"]),
    T("What is the capital of Eritrea?", ["Asmara"]), T("What is the capital of Malawi?", ["Lilongwe"]), T("What is the capital of Turkmenistan?", ["Ashgabat"]),
    T("What is the chemical symbol for silicon?", ["Si"]), T("What is the chemical symbol for zinc?", ["Zn"]), T("What is the chemical symbol for chlorine?", ["Cl"]),
    T("What is the chemical symbol for argon?", ["Ar"]), T("What is the chemical symbol for bismuth?", ["Bi"]), T("What is the chemical symbol for cobalt?", ["Co"]),
    T("What is the chemical symbol for iodine?", ["I"]), T("What is the chemical symbol for uranium?", ["U"]), T("What is the chemical symbol for arsenic?", ["As"]),
    T("What is the chemical symbol for barium?", ["Ba"]), T("What is the largest moon of Uranus?", ["Titania"]), T("Which planet has the moon Phobos?", ["Mars"]),
    T("Which planet has the moon Io?", ["Jupiter"]), T("Which planet has the moon Enceladus?", ["Saturn"]), T("Which planet has the moon Miranda?", ["Uranus"]),
    T("What is the capital of Malta?", ["Valletta"]), T("What is the capital of Cyprus?", ["Nicosia"]), T("What is the capital of Montenegro?", ["Podgorica"]),
    T("What is the capital of North Macedonia?", ["Skopje"]), T("What is the capital of Bosnia and Herzegovina?", ["Sarajevo"]),
    T("What is the capital of Mauritania?", ["Nouakchott"]), T("What is the capital of Gabon?", ["Libreville"]), T("What is the capital of Cameroon?", ["Yaoundé", "Yaounde"]),
    T("What is the capital of Chad?", ["N'Djamena", "Ndjamena"]), T("What is the capital of Sudan?", ["Khartoum"]), T("What is the capital of Somalia?", ["Mogadishu"]),
    T("What is the capital of Yemen?", ["Sanaa", "Sana'a"]), T("What is the capital of Bahrain?", ["Manama"]), T("What is the capital of Guatemala?", ["Guatemala City"]),
    T("What is the capital of Panama?", ["Panama City"]),
]
EXACT = [
    N("How many seconds are in 9 minutes?", 540), N("Convert 25 miles to kilometres.", 25 * 1.609344), N("What is 35% of 620?", 217),
    N("What is 7,056 divided by 84?", 84), N("What is 37 times 43?", 1591), N("What is 3 to the power of 7?", 2187),
    N("What is the square root of 6,889?", 83), N("Convert 59 degrees Fahrenheit to Celsius.", 15), N("Convert 25 degrees Celsius to Fahrenheit.", 77),
    N("How many grams are in 3.75 kilograms?", 3750), N("How many centimetres are in 4.6 metres?", 460), N("Convert 20 pounds to kilograms.", 20 * 0.45359237),
    N("Convert 5 US gallons to litres.", 5 * 3.785411784), N("What is 12% of 875?", 105), N("What is 8,000 minus 2,468?", 5532),
    N("What is 3,456 plus 6,789?", 10245), N("What is 360 divided by 0.6?", 600), N("What is 7 factorial?", 5040),
    N("Convert 15 feet to metres.", 15 * 0.3048), N("Convert 9 inches to centimetres.", 22.86),
    N("What is the area of a rectangle 12 m by 17 m, in square metres?", 204),
    N("What is the circumference of a circle with a radius of 9 m, in metres?", 2 * math.pi * 9),
    N("What is the area of a circle with a radius of 6 cm, in square centimetres?", math.pi * 36), N("How many days are in 13 weeks?", 91),
    N("What is 47 squared?", 2209), N("Convert 80 kilometres per hour to miles per hour.", 80 / 1.609344), N("How many millilitres are in 2.4 litres?", 2400),
    N("What is 62.5% of 128?", 80), N("Convert 3 kilowatt-hours to joules.", 1.08e7), N("What is 2,025 divided by 45?", 45),
    N("What is 19 times 53?", 1007), N("What is 2 to the power of 12?", 4096), N("Convert 12 miles to kilometres.", 12 * 1.609344),
    N("What is 16% of 450?", 72), N("Convert 12 ounces to grams.", 12 * 28.349523125), N("What is the square root of 7,744?", 88),    N("What is 27 times 58?", 1566), N("What is 15% of 1,240?", 186), N("How many minutes are in 6.5 hours?", 390),
]
DECLINE = [
    X("Who was the first person to walk on Jupiter?", "no one has"), X("What is the capital of the Atlantic Ocean?", "no such capital"),
    X("In what year did Queen Victoria visit the Moon?", "false premise"), X("What is my aunt's phone number?", "private"),
    X("What will I eat for breakfast tomorrow?", "unknowable, private"), X("Which moon orbits the Sun directly?", "false premise"),
    X("What is the name of my dog?", "private"), X("How old is the king of the Sahara Desert?", "no such office"),
    X("A 4 kg drum is taken to the planet Gethen. What does it weigh there, in newtons?", "no such planet"),
    X("A tank has a volume of -3 cubic metres. How many kilograms of water does it hold?", "negative volume"),
    X("A 2 kW heater runs 30 hours a day. How many kWh does it use in a day?", "more than 24 hours in a day"),
    X("Who won the 2034 football World Cup final?", "future event"), X("What is the population of Middle-earth?", "fictional place"),
    X("When did Shakespeare land on Mars?", "false premise"), X("Why is the Sun made of ice?", "false premise"),
    X("What is my bank password?", "private"), X("How much does the colour blue weigh?", "category error"),
    X("What was Isaac Newton's email address?", "anachronism"),
    X("How many kilometres is it from London to the planet Gallifrey?", "fictional planet"),
    X("A truck uses -9 litres of fuel per 100 km. How much fuel does it use on a 200 km trip?", "negative fuel use"),
    X("A 60 W bulb runs for -3 hours. How many kWh does it use?", "negative duration"),
    X("In what year did Mexico become a Canadian province?", "false premise"), X("Who was the Emperor of Switzerland in 1900?", "no such office"),
    X("What is the GDP of Atlantis?", "fictional place"), X("How many hours are in a day on the planet Tralfamadore?", "fictional planet"),
    X("What is the chemical symbol for the element unobtainium?", "no such element"),
    X("Which sea lies between Madrid and Lisbon?", "false premise"), X("What is my passport number?", "private"),
    X("A 9 kg crate is lifted 3 metres on the planet Pern. How much potential energy does it gain?", "fictional planet"),
    X("Who is my best friend?", "private"), X("What did my sister buy yesterday?", "private"),
    X("Who was the first king of the Arctic Ocean?", "no such office"), X("What is my house worth?", "private"),
    X("How many moons does the planet Vulcan have?", "fictional planet"),    X("What is my grandmother's maiden name?", "private"), X("In what year did the Roman Empire launch its first satellite?", "anachronism"),
    X("Who was the first emperor of the Moon?", "no such office"), X("What is the population of Wakanda?", "fictional place"),
]
MULTISTEP = [
    N("A coach travels 240 km in 3 hours. At the same speed, how far does it travel in 5 hours?", 400, g=M),
    N("A copier prints 45 pages in 3 minutes. How many pages does it print in 18 minutes?", 270, g=M),
    N("A 2 kW kettle runs for 6 minutes. How many kWh does it use?", 0.2, g=M),
    N("A 50 W lamp runs 8 hours a day for 30 days. How many kWh is that?", 12, g=M),
    N("Electricity costs 25 cents per kWh. What does running a 2 kW heater for 3 hours cost, in dollars?", 1.5, g=M),
    N("A rectangular field is 400 m by 75 m. How many hectares is it?", 3, g=M),
    N("A 60 kg hiker gains 200 metres of height on Mars. How many kilojoules of potential energy is that?", 60 * MARS * 200 / 1000, tol=0.02, g=M),
    N("What does a 90 kg astronaut weigh on the Moon, in newtons?", 90 * MOON, tol=0.02, g=M),
    N("A gold nugget has a volume of 20 cubic centimetres. What is its mass in kilograms?", 19.32 * 20 / 1000, tol=0.02, g=M),
    N("A solid iron cube is 4 cm on each side. What does it weigh on Earth, in newtons?", 7.874 * 64 / 1000 * G, tol=0.02, g=M),
    N("How many kilojoules does it take to heat 6 kg of water from 20 °C to 70 °C?", 6 * 4184 * 50 / 1000, tol=0.02, g=M),
    N("A car travels 420 km and uses 6 litres of petrol per 100 km. How many litres does it use?", 25.2, g=M),
    N("A cylindrical tank 1 metre across and 2 metres tall is full of water. How many kilograms of water does it hold?", math.pi * 0.25 * 2 * 1000, tol=0.02, g=M),
    N("A 500 g block of copper is heated from 20 °C to 80 °C. How many joules does it absorb?", 0.5 * 385 * 60, tol=0.02, g=M),
    N("A runner covers 21 km in 1.75 hours. What is the average speed in km per hour?", 12, g=M),
    N("A pump fills a 120 litre tank in 4 minutes. How many litres does it deliver in an hour?", 1800, g=M),
    N("A 40 kg sack is lifted 5 metres on Earth. How many joules of potential energy does it gain?", 40 * G * 5, g=M),
    N("A courier earns 18 dollars an hour and works 7 hours a day for 5 days. How many dollars is that?", 630, g=M),
    N("A 12 V battery stores 80 Ah. How many watt-hours is that?", 960, g=M),
    N("A walker covers 6 km in 72 minutes. At the same pace, how many minutes does 10 km take?", 120, g=M),
    N("A 3 kg bag is lifted 2 metres on Earth. How many joules of potential energy does it gain?", 3 * G * 2, g=M),
    N("A 1,500 W heater runs for 40 minutes. How many kWh is that?", 1, g=M),
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
    assert len(set(qs)) == 150, "duplicate inside test 22"
    with open(sys.argv[1], "w", encoding="utf-8", newline="\n") as f:
        json.dump(items, f, indent=1, ensure_ascii=False)
    print("sealed 22:", len(items), "items")
