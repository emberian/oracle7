"""sealed14_questions - SEALED TEST 14: the release gate for RC13c (head after w533). Sealed test 13 was run once on RC13b
(2026-10-13, head w532): full missed the format bar (1 expression reply), slim missed precision (89.2%); it is spent.
Written by Claude on 2026-10-13 AFTER those failures were known and by the author of the w533 fix - disclosed. Two
answer-key errors in test 13 (a birth year that differs between the Julian and Gregorian calendars; an item whose answer
sentence states an implied count before the answer) are avoided here by construction. The recipe and the group sizes are
tests 12-13's; the decline group keeps their classes with NEW questions. Questions were NOT chosen by asking the system; no
question repeats sealed tests 3-13, the probes, any harvested benchmark question or any specialist panel item (checked by
sealed14_dedupe.py before hashing). Run ONCE per variant on the clean harness.
Bars (unchanged): precision on answered >= 0.90, false yes <= 2, zero FORMAT defects (format audit v2).
Groups: knowledge 70 (12 without a question mark) · exact 30 · multistep 20 · decline 30 = 150."""
import json
import math
import re
import sys

E, M, K, D = "exact", "multistep", "knowledge", "decline"
N = lambda q, v, tol=0.01, g=E: {"q": q, "expect": v, "kind": "number", "tol": tol, "group": g, "valid": True}
T = lambda q, aliases, g=K: {"q": q, "expect": aliases, "kind": "text", "group": g, "valid": True}
X = lambda q, why: {"q": q, "expect": "decline", "kind": "decline", "group": D, "valid": False, "why": why}
G = 9.80665

ITEMS = [
    # ---- knowledge (70: 58 questions + 12 without a question mark)
    T("Who wrote The Charterhouse of Parma?", ["Stendhal"]),
    T("Who wrote The White Guard?", ["Bulgakov"]),
    T("Who wrote Pedro Páramo?", ["Rulfo"]),
    T("Who wrote R.U.R.?", ["Čapek", "Capek"]),
    T("Who wrote Kristin Lavransdatter?", ["Undset"]),
    T("Who wrote The Man Without Qualities?", ["Musil"]),
    T("Who wrote Eugénie Grandet?", ["Balzac"]),
    T("Who is the author of The Radetzky March?", ["Joseph Roth"]),
    T("Who is the author of Siddhartha?", ["Hesse"]),
    T("Who is the author of Kokoro?", ["Sōseki", "Soseki", "Natsume"]),
    T("Who painted The Charging Chasseur?", ["Géricault", "Gericault"]),
    T("Who painted Saturn Devouring His Son?", ["Goya"]),
    T("Who painted Wanderer above the Sea of Fog?", ["Friedrich"]),
    T("Who painted The Ambassadors?", ["Holbein"]),
    T("Who painted The Surrender of Breda?", ["Velázquez", "Velazquez"]),
    T("Who composed the opera Rusalka?", ["Dvořák", "Dvorak"]),
    T("Who composed the opera Khovanshchina?", ["Mussorgsky", "Musorgsky"]),
    T("Who composed the opera Lakmé?", ["Delibes"]),
    T("Who composed the ballet Coppélia?", ["Delibes"]),
    T("Who composed the opera Les Troyens?", ["Berlioz"]),
    T("What is the capital of Malawi?", ["Lilongwe"]),
    T("What is the capital of Moldova?", ["Chișinău", "Chisinau", "Chişinău"]),
    T("What is the capital of Turkmenistan?", ["Ashgabat"]),
    T("What is the capital of Namibia?", ["Windhoek"]),
    T("What is the capital of Honduras?", ["Tegucigalpa"]),
    T("Which city is the capital of Jamaica?", ["Kingston"]),
    T("Which city is the capital of Iceland?", ["Reykjavík", "Reykjavik"]),
    T("What is the currency of Serbia?", ["dinar"]),
    T("What is the currency of Bangladesh?", ["taka"]),
    T("What is the currency of Armenia?", ["dram"]),
    T("What is the official language of Mauritania?", ["Arabic"]),
    T("What is the official language of Liechtenstein?", ["German"]),
    T("On which continent is Bhutan?", ["Asia"]),
    T("Which country is the city of Tartu in?", ["Estonia"]),
    T("Which country is the city of Trondheim in?", ["Norway"]),
    T("Who directed Wild Strawberries?", ["Bergman"]),
    T("Who directed Bicycle Thieves?", ["De Sica"]),
    T("Who directed The Seventh Seal?", ["Bergman"]),
    T("Who directed Andrei Rublev?", ["Tarkovsky"]),
    T("Who invented the stethoscope?", ["Laennec", "Laënnec"]),
    T("Who discovered the moon Phoebe?", ["Pickering"]),
    T("Who discovered the moon Hyperion?", ["Bond", "Lassell"]),
    T("Which planet does Enceladus orbit?", ["Saturn"]),
    T("Which planet does Oberon orbit?", ["Uranus"]),
    T("Who founded IKEA?", ["Kamprad"]),
    T("Who was the architect of the Sydney Opera House?", ["Utzon"]),
    T("Where was Frédéric Chopin born?", ["Żelazowa Wola", "Zelazowa Wola"]),
    T("Where was Gustav Mahler born?", ["Kaliště", "Kaliste"]),
    T("In what year was Marie Curie born?", ["1867"]),
    T("Who was Frida Kahlo married to?", ["Diego Rivera", "Rivera"]),
    T("Who was the father of Queen Victoria?", ["Edward"]),
    T("Which instrument did Louis Armstrong play?", ["trumpet", "cornet"]),
    T("Which band was Mick Jagger a member of?", ["Rolling Stones"]),
    T("Who won the 2010 FIFA World Cup?", ["Spain"]),
    T("Which city hosted the 2000 Summer Olympics?", ["Sydney"]),
    T("In which constellation is the star Vega?", ["Lyra"]),
    T("Who created the character Jay Gatsby?", ["Fitzgerald"]),
    T("Which company developed the video game Half-Life?", ["Valve"]),
    T("Name the author of The Trial", ["Kafka"]),
    T("Tell me the capital of Chile", ["Santiago"]),
    T("The currency of Sweden", ["krona"]),
    T("Name the composer of the opera William Tell", ["Rossini"]),
    T("The first person to reach the South Pole", ["Amundsen"]),
    T("Name the planet that the moon Deimos orbits", ["Mars"]),
    T("The director of the film Rear Window", ["Hitchcock"]),
    T("Name the painter of Primavera", ["Botticelli"]),
    T("Name the capital of Portugal", ["Lisbon"]),
    T("The inventor of the Braille alphabet", ["Louis Braille", "Braille"]),
    T("Name the author of Anna Karenina", ["Tolstoy"]),
    T("The country in which the city of Kyoto lies", ["Japan"]),
    # ---- exact (30)
    N("What is 18% of 2,250?", 405),
    N("What is 5/8 as a decimal?", 0.625),
    N("Solve for x: 6x - 12 = 30.", 7),
    N("What is the square root of 3,136?", 56),
    N("What is 5 to the power 5?", 3125),
    N("How many seconds are there in 1.75 hours?", 6300),
    N("Convert 54 kilometres per hour to metres per second.", 15),
    N("Convert 104 degrees Fahrenheit to Celsius.", 40),
    N("How many millilitres are in 4.5 litres?", 4500),
    N("What is 30 pounds in kilograms?", 30 * 0.45359237),
    N("What is the derivative of 3x^3 at x = 2?", 36),
    N("What is the area of a circle with radius 6 m?", math.pi * 36),
    N("What is the volume of a cube with side 7 cm?", 343),
    N("What is the mass of 3 litres of sea water in kg?", 3.075),
    N("What is the density of gold in kg/m3?", 19300),
    N("What is the pressure 25 m deep in fresh water?", 1000 * G * 25),
    N("How much energy in MJ does burning 2 kg of petrol release?", 88.6),
    N("A spring with spring constant 600 N/m is stretched 0.03 m. What force does it exert?", 18),
    N("How much of a 64 g sample of phosphorus-32 remains after 28.6 days?", 64 * 0.5 ** (28.6 / 14.268)),
    N("What is the kinetic energy of a 6 kg ball moving at 4 m/s?", 48),
    N("How long does a stone take to fall 80 m?", math.sqrt(2 * 80 / G)),
    N("What is 10 factorial divided by 8 factorial?", 90),
    N("What is the greatest common divisor of 144 and 180?", 36),
    N("How many minutes are in 2.5 days?", 3600),
    N("What is 15% of 860?", 129),
    N("What is the area of a triangle with base 10 m and height 6 m?", 30),
    N("Convert 20 kilometres to miles.", 20 / 1.609344),
    N("What is the perimeter of a square with side 11 m?", 44),
    N("What is 15 squared?", 225),
    N("How many milligrams are in 3.5 grams?", 3500),
    # ---- multistep (20)
    N("A 2.2 kW heater runs 4 hours a day for 25 days. At $0.16 per kWh, what does that cost?", 35.2, g=M),
    N("A car gets 35 mpg and drives 280 miles. How many kg of CO2 does it emit?", 280 / 35 * 8.887, g=M),
    N("How many kWh does it take to heat 6 kg of water from 10 C to 70 C?", 6 * 4186 * 60 / 3.6e6, g=M),
    N("A 1.2 kW toaster runs 5 minutes a day for 60 days. How many kWh is that?", 1.2 * 5 / 60 * 60, g=M),
    N("A cylindrical tank 2 m across and 1 m tall is full of water. What is the mass of the water in kg?", math.pi * 1000, g=M),
    N("How much energy in MJ is released by burning 15 litres of diesel?", 0.015 * 832 * 43.0, g=M),
    N("A 5 kg block of iron is fully submerged in water. What is the buoyant force on it?", 5 / 7874 * 1000 * G, g=M),
    N("A truck averaging 12 miles per gallon covers 240 miles on gasoline. How many kg of CO2 is that?", 20 * 8.887, g=M),
    N("How many kilojoules does it take to warm 4 kg of iron from 20 C to 120 C?", 4 * 449 * 100 / 1000, g=M),
    N("How many kWh does it take to melt 12 kg of ice?", 12 * 334000 / 3.6e6, g=M),
    N("A 100 W lamp is left on 6 hours a day for 30 days. How many kWh does it use?", 100 * 6 * 30 / 1000, g=M),
    N("A fridge draws 1.5 A at 230 V for 24 hours. How many kWh does it use?", 1.5 * 230 * 24 / 1000, g=M),
    N("How much would a 90 kg astronaut weigh on a planet with 0.5 Earth masses and 0.8 Earth radii?", 90 * G * 0.5 / 0.64, tol=0.02, g=M),
    N("A 1.5 kW pump runs 6 hours. At $0.22 per kWh, what does that cost?", 1.98, g=M),
    N("Water flows at 15 litres per minute for 25 minutes. How many litres is that?", 375, g=M),
    N("A walker goes at 5 km/h for 3.5 hours. How far does she travel in km?", 17.5, g=M),
    N("A 3.5 kW oven runs 2 hours a day. How many kWh does it use in a 30-day month?", 210, g=M),
    N("A round drum 0.4 m across and 1.2 m tall is full of diesel. How heavy is the diesel, in kg?", math.pi * 0.2 ** 2 * 1.2 * 832, g=M),
    N("A 1.1 kW microwave runs 15 minutes a day for 120 days. At $0.18 per kWh, what does that cost?", 5.94, g=M),
    N("How many kWh does it take to heat 150 litres of water from 15 C to 60 C?", 150 * 4186 * 45 / 3.6e6, g=M),
    # ---- decline (30)
    X("What is the capital of Jupiter?", "no such thing"),
    X("Who was the first king of the United States?", "no such office"),
    X("What is my boss's home address?", "private"),
    X("What will the euro be worth in dollars next Tuesday?", "unknowable future"),
    X("Who won the 2038 Wimbledon men's final?", "future event"),
    X("What is the population of Shangri-La?", "fictional place"),
    X("What did I dream about last night?", "private / unknowable"),
    X("A 500 W fridge runs 28 hours a day. How many kWh does it use daily?", "28 hours in a day"),
    X("A cyclist rides -45 km in 3 hours. What is her average speed?", "negative distance"),
    X("What is the mass of -2 litres of oil?", "negative volume"),
    X("How long does a coin take to fall -15 m?", "negative height"),
    X("What is the cube root of jealousy?", "meaningless"),
    X("Which country did Beethoven rule as king?", "false premise"),
    X("In what year did Charles Darwin win the Nobel Prize in Physics?", "false premise (no Nobel Prize)"),
    X("Who was the 90th President of France?", "no such person yet"),
    X("What is my social security number?", "private"),
    X("What is the code to my front door?", "private"),
    X("How much will my house be worth in 2050?", "unknowable future"),
    X("Who is the current Emperor of Germany?", "no such office"),
    X("What is the freezing point of a dream?", "meaningless"),
    X("What is the capital city of the Arctic Ocean?", "an ocean has no capital"),
    X("Which of the Sun's two moons is larger?", "false premise (the Sun has no moons)"),
    X("What colour am I thinking of?", "unknowable"),
    X("Who painted The Starry Night in 1990?", "false premise (painted 1889)"),
    X("What is the area of a square with side -3 m?", "negative side"),
    X("A spring with spring constant -80 N/m is stretched 0.25 m. What force does it exert?", "negative stiffness"),
    X("What will the rainfall be in Madrid on 4 August 2032?", "unknowable future"),
    X("What brand of phone did Cleopatra use?", "anachronism"),
    X("Who discovered the second moon of Venus?", "Venus has no moons"),
    X("How much of a 200 g sample remains after 3 days?", "no isotope or half-life given"),
]


def check():
    groups = {}
    for it in ITEMS:
        groups[it["group"]] = groups.get(it["group"], 0) + 1
        if it["kind"] == "number":
            givens = [float(t.replace(",", "")) for t in re.findall(r"(?<![\w.])\d[\d,]*(?:\.\d+)?", it["q"])]
            assert not any(abs(g - it["expect"]) <= 1e-9 * max(abs(g), 1) for g in givens), ("answer is a given", it["q"])
        if it["kind"] == "text":
            assert all(len(a) >= 3 for a in it["expect"]), ("alias under 3 characters", it["q"])
    nq = sum(1 for it in ITEMS if it["group"] == K and not it["q"].rstrip().endswith("?"))
    assert groups == {K: 70, E: 30, M: 20, D: 30}, groups
    assert nq == 12, nq
    assert len({it["q"] for it in ITEMS}) == len(ITEMS), "duplicate question"
    return groups


if __name__ == "__main__":
    print(check())
    json.dump(ITEMS, open(sys.argv[1] if len(sys.argv) > 1 else "sealed14.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)
