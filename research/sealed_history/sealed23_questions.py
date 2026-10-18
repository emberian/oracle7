"""sealed23_questions - SEALED TEST 23: the release gate for RELEASE 3.2 (head after w551, the proved cross-check with the
veri7vn kernels; the four star specialists #214-217; decay-r2, an amount in the mass unit asked).
Written by Claude on 2026-10-18 BEFORE release 3.2 answered any of it and before its code froze; same author - disclosed.
Test 22 is spent (3.1).
SINGLE part: 162 questions = the recipe and group sizes of tests 12-22 (70 knowledge, 30 exact, 30 must-decline, 20 multi-step)
+ a new group of 12 for what 3.2 adds (10 star-specialist and unit-asked questions, 2 must-decline). Each group is drawn in
order from its pool, skipping any question an earlier sealed test (10-22) asked; the draw is deterministic.
Scoring = run_sealed22's rules unchanged (run_sealed23.py); the new group is scored by the same rules.
Bars (unchanged): precision on answered >= 0.90, false yes <= 2, zero format defects.
Constants: g Earth 9.80665, Moon 1.62, Mars 3.71 m/s2; densities g/cm3 gold 19.32, iron 7.874, water 1.000; specific heat
J/(kg K) water 4184, copper 385; 1 mile 1.609344 km; 1 lb 0.45359237 kg; 1 oz 28.349523125 g; 1 US gal 3.785411784 L;
1 inch 2.54 cm; 1 foot 0.3048 m. Stars (IAU 2015): T_sun 5,772 K, R_sun 109.076 Earth radii, 1 AU 215.032 solar radii,
1 year 365.25 days; caesium-137 half-life 30.08 years."""
import json
import math
import sys

E, M, K, D, S = "exact", "multistep", "knowledge", "decline", "stars"
N = lambda q, v, tol=0.01, g=E: {"q": q, "expect": v, "kind": "number", "tol": tol, "group": g, "valid": True}
T = lambda q, aliases, g=K: {"q": q, "expect": aliases, "kind": "text", "group": g, "valid": True}
X = lambda q, why, g=D: {"q": q, "expect": "decline", "kind": "decline", "group": g, "valid": False, "why": why}
G, MOON, MARS = 9.80665, 1.62, 3.71
TS, AUR, RE, YR = 5772.0, 149597870.7 / 695700.0, 695700.0 / 6378.1, 365.25
TEQ1 = TS * math.sqrt(1.0 / (2.0 * AUR))

KNOWLEDGE = [
    T("Who wrote War and Peace?", ["Tolstoy"]), T("Who wrote Anna Karenina?", ["Tolstoy"]), T("Who wrote Crime and Punishment?", ["Dostoevsky", "Dostoyevsky"]),
    T("Who wrote The Great Gatsby?", ["Fitzgerald"]), T("Who wrote Moby-Dick?", ["Melville"]), T("Who wrote Wuthering Heights?", ["Emily Brontë", "Emily Bronte", "Brontë", "Bronte"]),
    T("Who wrote Frankenstein?", ["Shelley"]), T("Who wrote Dracula?", ["Stoker"]), T("Who wrote The Picture of Dorian Gray?", ["Wilde"]),
    T("Who wrote Great Expectations?", ["Dickens"]), T("Who wrote Pride and Prejudice?", ["Austen"]), T("Who wrote The Catcher in the Rye?", ["Salinger"]),
    T("Who wrote To Kill a Mockingbird?", ["Lee"]), T("Who wrote Nineteen Eighty-Four?", ["Orwell"]), T("Who wrote The Old Man and the Sea?", ["Hemingway"]),
    T("Who wrote The Grapes of Wrath?", ["Steinbeck"]), T("Who wrote Invisible Man?", ["Ellison"]), T("Who wrote The Sun Also Rises?", ["Hemingway"]),
    T("Who wrote Mrs Dalloway?", ["Woolf"]), T("Who wrote Heart of Darkness?", ["Conrad"]), T("Who wrote The Metamorphosis?", ["Kafka"]),
    T("Who wrote Candide?", ["Voltaire"]), T("Who wrote Les Misérables?", ["Hugo"]), T("Who wrote The Count of Monte Cristo?", ["Dumas"]),
    T("Who wrote the Divine Comedy?", ["Dante"]), T("Who wrote The Canterbury Tales?", ["Chaucer"]), T("Who wrote Paradise Lost?", ["Milton"]),
    T("Who wrote Gulliver's Travels?", ["Swift"]), T("Who wrote Robinson Crusoe?", ["Defoe"]), T("Who wrote The Little Prince?", ["Saint-Exupéry", "Saint-Exupery"]),
    T("Who directed Citizen Kane?", ["Welles"]), T("Who directed The Godfather?", ["Coppola"]), T("Who directed Rashomon?", ["Kurosawa"]),
    T("Who directed Schindler's List?", ["Spielberg"]), T("Who directed Apocalypse Now?", ["Coppola"]), T("Who directed Lawrence of Arabia?", ["Lean"]),
    T("Who directed Casablanca?", ["Curtiz"]), T("Who directed The Shining?", ["Kubrick"]), T("Who directed Raging Bull?", ["Scorsese"]),
    T("Who directed Amélie?", ["Jeunet"]), T("Who directed Alien?", ["Scott"]), T("Who directed Rear Window?", ["Hitchcock"]),
    T("Who painted the Mona Lisa?", ["Leonardo", "da Vinci"]), T("Who painted Sunflowers?", ["Van Gogh", "van Gogh"]), T("Who painted The Hay Wain?", ["Constable"]),
    T("Who painted The Fighting Temeraire?", ["Turner"]), T("Who painted Nighthawks?", ["Hopper"]), T("Who painted The Son of Man?", ["Magritte"]),
    T("Who made The Great Wave off Kanagawa?", ["Hokusai"]), T("Who painted Campbell's Soup Cans?", ["Warhol"]), T("Who painted Impression, Sunrise?", ["Monet"]),
    T("Who composed The Nutcracker?", ["Tchaikovsky"]), T("Who composed The Marriage of Figaro?", ["Mozart"]), T("Who composed the Brandenburg Concertos?", ["Bach"]),
    T("Who composed Eine kleine Nachtmusik?", ["Mozart"]), T("Who composed Clair de lune?", ["Debussy"]), T("Who composed The Blue Danube?", ["Strauss"]),
    T("Who composed the Peer Gynt suite?", ["Grieg"]), T("Who composed Tosca?", ["Puccini"]), T("Who composed The Firebird?", ["Stravinsky"]),
    T("What is the capital of Egypt?", ["Cairo"]), T("What is the capital of Argentina?", ["Buenos Aires"]), T("What is the capital of Australia?", ["Canberra"]),
    T("What is the capital of Canada?", ["Ottawa"]), T("What is the capital of Turkey?", ["Ankara"]), T("What is the capital of Brazil?", ["Brasília", "Brasilia"]),
    T("What is the capital of South Korea?", ["Seoul"]), T("What is the capital of Poland?", ["Warsaw"]), T("What is the capital of Sweden?", ["Stockholm"]),
    T("What is the capital of Norway?", ["Oslo"]), T("What is the capital of Greece?", ["Athens"]), T("What is the capital of Uruguay?", ["Montevideo"]),
    T("What is the capital of Paraguay?", ["Asunción", "Asuncion"]), T("What is the capital of Ecuador?", ["Quito"]), T("What is the capital of Uganda?", ["Kampala"]),
    T("What is the capital of Zambia?", ["Lusaka"]), T("What is the capital of Austria?", ["Vienna"]), T("What is the capital of Denmark?", ["Copenhagen"]),
    T("What is the chemical symbol for iron?", ["Fe"]), T("What is the chemical symbol for gold?", ["Au"]), T("What is the chemical symbol for silver?", ["Ag"]),
    T("What is the chemical symbol for copper?", ["Cu"]), T("What is the chemical symbol for helium?", ["He"]), T("What is the chemical symbol for magnesium?", ["Mg"]),
    T("What is the chemical symbol for nickel?", ["Ni"]), T("What is the largest moon of Saturn?", ["Titan"]), T("What is the largest moon of Jupiter?", ["Ganymede"]),
    T("Which planet has the moon Titan?", ["Saturn"]), T("Which planet has the moon Europa?", ["Jupiter"]), T("Which planet has the moon Deimos?", ["Mars"]),
    T("Who wrote Middlesex?", ["Eugenides"]), T("Who wrote The Kite Runner?", ["Hosseini"]), T("Who wrote Life of Pi?", ["Martel"]),
    T("Who wrote The Road?", ["McCarthy"]), T("Who wrote Blood Meridian?", ["McCarthy"]), T("Who wrote Atonement?", ["McEwan"]),
    T("Who wrote Never Let Me Go?", ["Ishiguro"]), T("Who wrote Wolf Hall?", ["Mantel"]), T("Who wrote The God of Small Things?", ["Roy"]),
    T("Who wrote Midnight's Children?", ["Rushdie"]), T("Who wrote White Teeth?", ["Smith"]), T("Who wrote The Color Purple?", ["Walker"]),
    T("Who wrote Song of Solomon?", ["Morrison"]), T("Who wrote A Clockwork Orange?", ["Burgess"]), T("Who wrote Lord of the Flies?", ["Golding"]),
    T("Who wrote The Hobbit?", ["Tolkien"]), T("Who wrote Dune?", ["Herbert"]), T("Who wrote Neuromancer?", ["Gibson"]),
    T("Who wrote Foundation?", ["Asimov"]), T("Who wrote The Left Hand of Darkness?", ["Le Guin"]), T("Who wrote The Master and Margarita?", ["Bulgakov"]),
    T("Who wrote Doctor Zhivago?", ["Pasternak"]), T("Who wrote The Tin Drum?", ["Grass"]), T("Who wrote All Quiet on the Western Front?", ["Remarque"]),
    T("Who wrote The Plague?", ["Camus"]), T("Who wrote Nausea?", ["Sartre"]), T("Who wrote The Shadow of the Wind?", ["Zafón", "Zafon"]),
    T("Who wrote Norwegian Wood?", ["Murakami"]), T("Who wrote Kafka on the Shore?", ["Murakami"]), T("Who wrote The Unbearable Lightness of Being?", ["Kundera"]),
    T("Who wrote Love in the Time of Cholera?", ["García Márquez", "Garcia Marquez", "Márquez", "Marquez"]), T("Who wrote The House of the Spirits?", ["Allende"]),
    T("Who wrote The Alchemist?", ["Coelho"]), T("Who wrote Steppenwolf?", ["Hesse"]), T("Who wrote Rebecca?", ["du Maurier", "Du Maurier"]),
    T("Who wrote Brideshead Revisited?", ["Waugh"]), T("Who wrote Howards End?", ["Forster"]), T("Who wrote Vanity Fair?", ["Thackeray"]),
    T("Who wrote Tess of the d'Urbervilles?", ["Hardy"]), T("Who wrote Northanger Abbey?", ["Austen"]), T("Who wrote Silas Marner?", ["Eliot"]),
    T("Who wrote The Turn of the Screw?", ["James"]), T("Who wrote Of Mice and Men?", ["Steinbeck"]), T("Who wrote East of Eden?", ["Steinbeck"]),
    T("Who wrote Light in August?", ["Faulkner"]), T("Who wrote As I Lay Dying?", ["Faulkner"]), T("Who wrote On the Road?", ["Kerouac"]),
    T("Who wrote Gone with the Wind?", ["Mitchell"]), T("Who wrote Little Women?", ["Alcott"]), T("Who wrote Uncle Tom's Cabin?", ["Stowe"]),
    T("Who wrote The Scarlet Letter?", ["Hawthorne"]), T("Who wrote Walden?", ["Thoreau"]),
    T("Who directed Chinatown?", ["Polanski"]), T("Who directed Annie Hall?", ["Allen"]), T("Who directed Mulholland Drive?", ["Lynch"]),
    T("Who directed Barry Lyndon?", ["Kubrick"]), T("Who directed The Third Man?", ["Reed"]), T("Who directed Ran?", ["Kurosawa"]),
    T("Who directed Late Spring?", ["Ozu"]), T("Who directed City of God?", ["Meirelles"]), T("Who directed Pan's Labyrinth?", ["del Toro", "Del Toro"]),
    T("Who directed Oldboy?", ["Park"]), T("Who directed The Grand Budapest Hotel?", ["Anderson"]), T("Who directed No Country for Old Men?", ["Coen"]),
    T("Who painted Christina's World?", ["Wyeth"]), T("Who painted The Hunters in the Snow?", ["Bruegel", "Brueghel"]), T("Who painted Saturn Devouring His Son?", ["Goya"]),
    T("Who painted The Third of May 1808?", ["Goya"]), T("Who painted The Death of Marat?", ["David"]), T("Who painted Luncheon of the Boating Party?", ["Renoir"]),
    T("Who painted The Card Players?", ["Cézanne", "Cezanne"]), T("Who painted Les Demoiselles d'Avignon?", ["Picasso"]), T("Who painted The Treachery of Images?", ["Magritte"]),
    T("Who composed The Lark Ascending?", ["Vaughan Williams"]), T("Who composed the Gymnopédies?", ["Satie"]), T("Who composed Peter and the Wolf?", ["Prokofiev"]),
    T("Who composed Carmina Burana?", ["Orff"]), T("Who composed Pictures at an Exhibition?", ["Mussorgsky"]), T("Who composed Scheherazade?", ["Rimsky-Korsakov"]),
    T("Who composed Finlandia?", ["Sibelius"]), T("Who composed Adagio for Strings?", ["Barber"]), T("Who composed The Hebrides overture?", ["Mendelssohn"]),
    T("What is the capital of Slovakia?", ["Bratislava"]), T("What is the capital of Slovenia?", ["Ljubljana"]), T("What is the capital of Croatia?", ["Zagreb"]),
    T("What is the capital of Serbia?", ["Belgrade"]), T("What is the capital of Albania?", ["Tirana"]), T("What is the capital of Latvia?", ["Riga"]),
    T("What is the capital of Lithuania?", ["Vilnius"]), T("What is the capital of Estonia?", ["Tallinn"]), T("What is the capital of Armenia?", ["Yerevan"]),
    T("What is the capital of Azerbaijan?", ["Baku"]), T("What is the capital of Jordan?", ["Amman"]), T("What is the capital of Lebanon?", ["Beirut"]),
    T("What is the capital of Oman?", ["Muscat"]), T("What is the capital of Qatar?", ["Doha"]), T("What is the capital of the Philippines?", ["Manila"]),
    T("What is the capital of Malaysia?", ["Kuala Lumpur"]), T("What is the capital of Zimbabwe?", ["Harare"]), T("What is the capital of Mozambique?", ["Maputo"]),
    T("What is the capital of Angola?", ["Luanda"]), T("What is the capital of Tunisia?", ["Tunis"]), T("What is the capital of Algeria?", ["Algiers"]),
    T("What is the capital of Jamaica?", ["Kingston"]), T("What is the chemical symbol for antimony?", ["Sb"]),
    T("What is the largest moon of Mars?", ["Phobos"]), T("Which planet has the moon Callisto?", ["Jupiter"]), T("Which planet has the moon Ariel?", ["Uranus"]),
    T("Which planet has the moon Rhea?", ["Saturn"]), T("Which planet has the moon Nereid?", ["Neptune"]),
]
EXACT = [
    N("How many seconds are in 14 minutes?", 840), N("Convert 40 miles to kilometres.", 40 * 1.609344), N("What is 45% of 360?", 162),
    N("What is 9,072 divided by 72?", 126), N("What is 64 times 29?", 1856), N("What is 5 to the power of 5?", 3125),
    N("What is the square root of 5,184?", 72), N("Convert 104 degrees Fahrenheit to Celsius.", 40), N("Convert 35 degrees Celsius to Fahrenheit.", 95),
    N("How many grams are in 6.2 kilograms?", 6200), N("How many centimetres are in 2.85 metres?", 285), N("Convert 50 pounds to kilograms.", 50 * 0.45359237),
    N("Convert 3 US gallons to litres.", 3 * 3.785411784), N("What is 18% of 650?", 117), N("What is 10,000 minus 3,725?", 6275),
    N("What is 4,321 plus 5,678?", 9999), N("What is 450 divided by 0.9?", 500), N("What is 6 factorial?", 720),
    N("Convert 22 feet to metres.", 22 * 0.3048), N("Convert 14 inches to centimetres.", 35.56),
    N("What is the area of a rectangle 15 m by 23 m, in square metres?", 345),
    N("What is the circumference of a circle with a radius of 7 m, in metres?", 2 * math.pi * 7),
    N("What is the area of a circle with a radius of 5 cm, in square centimetres?", math.pi * 25), N("How many days are in 17 weeks?", 119),
    N("What is 53 squared?", 2809), N("Convert 120 kilometres per hour to miles per hour.", 120 / 1.609344), N("How many millilitres are in 3.6 litres?", 3600),
    N("What is 37.5% of 96?", 36), N("Convert 2 kilowatt-hours to joules.", 7.2e6), N("What is 3,969 divided by 63?", 63),
    N("What is 23 times 47?", 1081), N("What is 2 to the power of 11?", 2048), N("Convert 18 miles to kilometres.", 18 * 1.609344),
    N("What is 24% of 375?", 90), N("Convert 8 ounces to grams.", 8 * 28.349523125), N("What is the square root of 9,409?", 97),
    N("What is 34 times 61?", 2074), N("How many minutes are in 4.25 hours?", 255),
    N("What is 72 times 18?", 1296), N("What is the square root of 3,136?", 56), N("How many seconds are in 2.5 hours?", 9000),
    N("Convert 7 feet to metres.", 7 * 0.3048), N("What is 15% of 980?", 147), N("What is 84 times 26?", 2184),
]
DECLINE = [
    X("Who was the first person to swim across the Sun?", "false premise"), X("What is the capital of the Pacific Ocean?", "no such capital"),
    X("In what year did Napoleon visit Neptune?", "false premise"), X("What is my neighbour's phone number?", "private"),
    X("What will I dream about tonight?", "unknowable, private"), X("Which star orbits the Earth?", "false premise"),
    X("What is the name of my cat?", "private"), X("How old is the president of Antarctica?", "no such office"),
    X("A 6 kg box is taken to the planet Arrakis. What does it weigh there, in newtons?", "fictional planet"),
    X("A pool has a volume of -40 cubic metres. How many litres of water does it hold?", "negative volume"),
    X("A 1 kW fan runs 26 hours a day. How many kWh does it use in a day?", "more than 24 hours in a day"),
    X("Who won the 2038 Olympic marathon?", "future event"), X("What is the population of Narnia?", "fictional place"),
    X("When did Charles Darwin land on the Moon?", "false premise"), X("Why is the ocean made of sand?", "false premise"),
    X("What is my email password?", "private"), X("How much does the number seven weigh?", "category error"),
    X("What was Julius Caesar's phone number?", "anachronism"),
    X("How many kilometres is it from Paris to the planet Krypton?", "fictional planet"),
    X("A van uses -7 litres of fuel per 100 km. How much fuel does it use on a 300 km trip?", "negative fuel use"),
    X("A 100 W bulb runs for -5 hours. How many kWh does it use?", "negative duration"),
    X("In what year did Brazil become a French province?", "false premise"), X("Who was the Emperor of Canada in 1950?", "no such office"),
    X("What is the GDP of Hogwarts?", "fictional place"), X("How many hours are in a day on the planet Solaris?", "fictional planet"),
    X("What is the chemical symbol for the element adamantium?", "no such element"),
    X("Which sea lies between Berlin and Vienna?", "false premise"), X("What is my social security number?", "private"),
    X("A 5 kg stone is lifted 2 metres on the planet Caladan. How much potential energy does it gain?", "fictional planet"),
    X("Who is my favourite teacher?", "private"), X("What did my brother eat for lunch?", "private"),
    X("Who was the first king of the Indian Ocean?", "no such office"), X("What is my car worth?", "private"),
    X("How many moons does the planet Krypton have?", "fictional planet"), X("What is my grandfather's middle name?", "private"),
    X("In what year did the Aztec Empire open its first railway?", "anachronism"),
    X("Who was the first person to walk on Venus?", "false premise"), X("What is the capital of the Moon?", "no such capital"),
    X("In what year did Einstein visit Saturn?", "false premise"), X("What is the population of Gotham City?", "fictional place"),
    X("What will the weather be on my birthday in 2040?", "unknowable, private"), X("What is my PIN number?", "private"),
    X("How tall is the king of the Pacific Ocean?", "no such office"), X("What is my landlord's name?", "private"),
]
MULTISTEP = [
    N("A train travels 180 km in 2 hours. At the same speed, how far does it travel in 7 hours?", 630, g=M),
    N("A printer prints 60 pages in 4 minutes. How many pages does it print in 22 minutes?", 330, g=M),
    N("A 3 kW oven runs for 20 minutes. How many kWh does it use?", 1, g=M),
    N("A 40 W lamp runs 6 hours a day for 25 days. How many kWh is that?", 6, g=M),
    N("Electricity costs 20 cents per kWh. What does running a 1.5 kW heater for 4 hours cost, in dollars?", 1.2, g=M),
    N("A rectangular field is 250 m by 120 m. How many hectares is it?", 3, g=M),
    N("A 70 kg climber gains 150 metres of height on Mars. How many kilojoules of potential energy is that?", 70 * MARS * 150 / 1000, tol=0.02, g=M),
    N("What does a 75 kg astronaut weigh on the Moon, in newtons?", 75 * MOON, tol=0.02, g=M),
    N("A gold bar has a volume of 50 cubic centimetres. What is its mass in kilograms?", 19.32 * 50 / 1000, tol=0.02, g=M),
    N("A solid iron cube is 5 cm on each side. What does it weigh on Earth, in newtons?", 7.874 * 125 / 1000 * G, tol=0.02, g=M),
    N("How many kilojoules does it take to heat 4 kg of water from 15 °C to 85 °C?", 4 * 4184 * 70 / 1000, tol=0.02, g=M),
    N("A car travels 350 km and uses 8 litres of petrol per 100 km. How many litres does it use?", 28, g=M),
    N("A 2 kg block of copper is heated from 25 °C to 75 °C. How many joules does it absorb?", 2 * 385 * 50, tol=0.02, g=M),
    N("A cyclist covers 45 km in 1.5 hours. What is the average speed in km per hour?", 30, g=M),
    N("A pump fills a 200 litre tank in 5 minutes. How many litres does it deliver in an hour?", 2400, g=M),
    N("A 25 kg sack is lifted 4 metres on Earth. How many joules of potential energy does it gain?", 25 * G * 4, g=M),
    N("A tutor earns 30 dollars an hour and works 5 hours a day for 4 days. How many dollars is that?", 600, g=M),
    N("A 24 V battery stores 50 Ah. How many watt-hours is that?", 1200, g=M),
    N("A walker covers 5 km in 60 minutes. At the same pace, how many minutes does 8 km take?", 96, g=M),
    N("A 2 kg bag is lifted 3 metres on Earth. How many joules of potential energy does it gain?", 2 * G * 3, g=M),
    N("A 2,000 W heater runs for 90 minutes. How many kWh is that?", 3, g=M),
    N("A cylindrical tank 2 metres across and 1 metre tall is full of water. How many kilograms of water does it hold?", math.pi * 1.0 * 1.0 * 1000, tol=0.02, g=M),
    N("What does a 50 kg crate weigh on Mars, in newtons?", 50 * MARS, tol=0.02, g=M),
    N("An athlete runs 400 m in 50 seconds. What is the speed in km per hour?", 28.8, g=M),
    N("A 1,200 W microwave runs for 5 minutes. How many kWh is that?", 0.1, g=M),
]
STARS = [
    N("What is the luminosity of a star with a radius of 0.5 solar radii and a temperature of 3,800 K?", 0.25 * (3800 / TS) ** 4, g=S),
    N("A planet transits a star of 0.4 solar radii with a depth of 2,500 ppm. What is the planet's radius in Earth radii?", 0.4 * math.sqrt(2500e-6) * RE, g=S),
    N("What is the orbital period, in days, of a planet 0.05 AU from a star of 0.3 solar masses?", YR * math.sqrt(0.05 ** 3 / 0.3), g=S),
    N("How much starlight does a planet 0.2 AU from a star of 0.04 solar luminosities receive, compared with Earth?", 0.04 / 0.2 ** 2, g=S),
    N("What is the transit probability, in percent, of a planet 0.1 AU from a star of 0.6 solar radii?", 0.6 / (0.1 * AUR) * 100, g=S),
    N("What is the equilibrium temperature of a planet 0.1 AU from a star of 0.01 solar luminosities, with an albedo of 0.3?", TEQ1 * (0.01 / 0.01) ** 0.25 * 0.7 ** 0.25, g=S),
    N("A sample has 40 g of caesium-137. How much remains after 30.08 years, in milligrams?", 20000, g=S),
    N("What is the effective temperature of a star with a luminosity of 0.09 solar luminosities and a radius of 0.6 solar radii?", TS * (0.09 / 0.36) ** 0.25, g=S),
    T("Is a planet that receives 1.0 times Earth's sunlight from a 5,000 K star in the habitable zone?", ["Yes"], g=S),
    N("How deep is the transit, in ppm, of a planet of 1.2 Earth radii crossing a star of 0.3 solar radii?", (1.2 / (0.3 * RE)) ** 2 * 1e6, g=S),
    X("Where is the habitable zone of a 12,000 K star with 50 solar luminosities?", "outside the fitted 2,600-7,200 K range", g=S),
    X("A planet transits a star with a depth of 900 ppm. What is the planet's radius?", "the star's radius is not given", g=S),
]


def pick(pool, n, prior):
    """the first n questions of the pool that no earlier sealed test asked (deterministic)"""
    out = [i for i in pool if i["q"].strip().lower() not in prior]
    assert len(out) >= n, "not enough unseen questions: %d < %d" % (len(out), n)
    return out[:n]


if __name__ == "__main__":
    prior = set(json.load(open(sys.argv[2])))
    items = pick(KNOWLEDGE, 70, prior) + pick(EXACT, 30, prior) + pick(DECLINE, 30, prior) + pick(MULTISTEP, 20, prior) + pick(STARS, 12, prior)
    qs = [i["q"].strip().lower() for i in items]
    assert len(set(qs)) == 162, "duplicate inside test 23"
    with open(sys.argv[1], "w", encoding="utf-8", newline="\n") as f:
        json.dump(items, f, indent=1, ensure_ascii=False)
    print("sealed 23:", len(items), "items")
