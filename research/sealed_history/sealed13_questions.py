"""sealed13_questions - SEALED TEST 13: the release gate for RC13b (head after w532). Sealed test 12 was run once on RC13
(2026-10-13, head w406) and FAILED its false-yes bar (5 > 2 in both variants); it is spent. Written by Claude on 2026-10-13
AFTER those five failures were known and by the author of the w532 fix - disclosed. The recipe and the group sizes are
test 12's (knowledge, exact computation, multi-step everyday problems, questions that must be declined); the decline group
keeps test 12's classes (no such thing, private, unknowable future, impossible quantities, negative quantities, false
premise, anachronism) with NEW questions, so a fix that only memorised test 12's wording gains nothing. Questions were NOT
chosen by asking the system; no question repeats sealed tests 3-12, the probes, any harvested benchmark question or any
specialist panel item (checked by sealed12_dedupe.py logic before hashing). Run ONCE per variant on the clean harness.
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
    T("Who wrote The Mill on the Floss?", ["George Eliot", "Eliot"]),
    T("Who wrote A Month in the Country?", ["Turgenev", "Carr"]),
    T("Who wrote Sentimental Education?", ["Flaubert"]),
    T("Who wrote Buddenbrooks?", ["Thomas Mann"]),
    T("Who wrote La Celestina?", ["Fernando de Rojas", "Rojas"]),
    T("Who wrote Agnes Grey?", ["Anne Brontë", "Anne Bronte", "Brontë", "Bronte"]),
    T("Who wrote Berlin Alexanderplatz?", ["Döblin", "Doblin"]),
    T("Who is the author of Frankenstein?", ["Mary Shelley", "Shelley"]),
    T("Who is the author of Things Fall Apart?", ["Achebe"]),
    T("Who is the author of The Name of the Rose?", ["Umberto Eco"]),
    T("Who painted The Anatomy Lesson of Dr. Nicolaes Tulp?", ["Rembrandt"]),
    T("Who painted The Haywain Triptych?", ["Bosch"]),
    T("Who painted The Death of Sardanapalus?", ["Delacroix"]),
    T("Who painted Swans Reflecting Elephants?", ["Dalí", "Dali"]),
    T("Who painted The Art of Painting?", ["Vermeer"]),
    T("Who composed The Firebird?", ["Stravinsky"]),
    T("Who composed the opera The Pearl Fishers?", ["Bizet"]),
    T("Who composed the opera Aida?", ["Verdi"]),
    T("Who composed the opera The Magic Flute?", ["Mozart"]),
    T("Who composed the ballet The Nutcracker?", ["Tchaikovsky"]),
    T("What is the capital of Bhutan?", ["Thimphu"]),
    T("What is the capital of Togo?", ["Lomé", "Lome"]),
    T("What is the capital of Eritrea?", ["Asmara"]),
    T("What is the capital of North Macedonia?", ["Skopje"]),
    T("What is the capital of Tajikistan?", ["Dushanbe"]),
    T("Which city is the capital of Canada?", ["Ottawa"]),
    T("Which city is the capital of Kenya?", ["Nairobi"]),
    T("What is the currency of the Czech Republic?", ["koruna"]),
    T("What is the currency of Malaysia?", ["ringgit"]),
    T("What is the currency of Ghana?", ["cedi"]),
    T("What is the official language of Cape Verde?", ["Portuguese"]),
    T("What is the official language of Gabon?", ["French"]),
    T("On which continent is Mali?", ["Africa"]),
    T("Which country is the city of Ghent in?", ["Belgium"]),
    T("Which country is the city of Gdańsk in?", ["Poland"]),
    T("Who directed Ikiru?", ["Kurosawa"]),
    T("Who directed Rope?", ["Hitchcock"]),
    T("Who directed Apocalypse Now?", ["Coppola"]),
    T("Who directed the film Metropolis?", ["Fritz Lang"]),
    T("Who invented the spinning jenny?", ["Hargreaves"]),
    T("Who discovered the moon Io?", ["Galileo"]),
    T("Who discovered the moon Miranda?", ["Kuiper"]),
    T("Which planet does Titan orbit?", ["Saturn"]),
    T("Which planet does Triton orbit?", ["Neptune"]),
    T("Who founded Apple Inc.?", ["Jobs", "Wozniak", "Ronald Wayne"]),
    T("Who was the architect of the Guggenheim Museum Bilbao?", ["Gehry"]),
    T("Where was Franz Schubert born?", ["Vienna", "Himmelpfortgrund"]),
    T("Where was Diego Rivera born?", ["Guanajuato"]),
    T("In what year was Johannes Kepler born?", ["1571"]),
    T("Who was Robert Browning married to?", ["Elizabeth Barrett"]),
    T("Who was the mother of Queen Elizabeth I?", ["Anne Boleyn", "Boleyn"]),
    T("Which instrument did Miles Davis play?", ["trumpet"]),
    T("Which band was John Lennon a member of?", ["Beatles"]),
    T("Who won the 1998 FIFA World Cup?", ["France"]),
    T("Which city hosted the 2008 Summer Olympics?", ["Beijing"]),
    T("In which constellation is the star Aldebaran?", ["Taurus"]),
    T("Who created the character Hercule Poirot?", ["Agatha Christie", "Christie"]),
    T("Which company developed the video game The Legend of Zelda?", ["Nintendo"]),
    T("Name the author of Moby-Dick", ["Melville"]),
    T("Tell me the capital of Argentina", ["Buenos Aires"]),
    T("The currency of the United Kingdom", ["pound", "sterling"]),
    T("Name the composer of The Four Seasons", ["Vivaldi"]),
    T("The first woman to win a Nobel Prize", ["Marie Curie", "Curie"]),
    T("Name the planet that the moon Callisto orbits", ["Jupiter"]),
    T("The director of the film Vertigo", ["Hitchcock"]),
    T("Name the painter of The Starry Night", ["van Gogh", "Gogh"]),
    T("Name the capital of Turkey", ["Ankara"]),
    T("The inventor of dynamite", ["Nobel"]),
    T("Name the author of Crime and Punishment", ["Dostoevsky", "Dostoyevsky"]),
    T("The country in which the city of Lyon lies", ["France"]),
    # ---- exact (30)
    N("What is 23% of 1,500?", 345),
    N("What is 7/16 as a decimal?", 0.4375),
    N("Solve for x: 3x + 11 = 50.", 13),
    N("What is the square root of 2,025?", 45),
    N("What is 3 to the power 7?", 2187),
    N("How many seconds are there in 2.25 hours?", 8100),
    N("Convert 90 kilometres per hour to metres per second.", 25),
    N("Convert 86 degrees Fahrenheit to Celsius.", 30),
    N("How many millilitres are in 3.2 litres?", 3200),
    N("What is 22 pounds in kilograms?", 22 * 0.45359237),
    N("What is the derivative of 5x^2 at x = 3?", 30),
    N("What is the area of a circle with radius 5 m?", math.pi * 25),
    N("What is the volume of a cube with side 6 cm?", 216),
    N("What is the mass of 0.5 litres of mercury in kg?", 6.767),
    N("What is the density of ethanol in kg/m3?", 789),
    N("What is the pressure 15 m deep in fresh water?", 1000 * G * 15),
    N("How much energy in MJ does burning 5 kg of natural gas release?", 240),
    N("A spring with spring constant 250 N/m is stretched 0.12 m. What force does it exert?", 30),
    N("How much of a 120 g sample of cobalt-60 remains after 10.54 years?", 120 * 0.5 ** (10.54 / 5.2714)),
    N("What is the kinetic energy of a 4 kg ball moving at 3 m/s?", 18),
    N("How long does a stone take to fall 20 m?", math.sqrt(2 * 20 / G)),
    N("What is 9 factorial divided by 7 factorial?", 72),
    N("What is the greatest common divisor of 132 and 198?", 66),
    N("How many hours are in 6 weeks?", 1008),
    N("What is 35% of 640?", 224),
    N("What is the sum of the interior angles of an octagon in degrees?", 1080),
    N("Convert 12 miles to kilometres.", 12 * 1.609344),
    N("What is the perimeter of a rectangle 9 m by 5 m?", 28),
    N("What is 12 cubed?", 1728),
    N("How many grams are in 2.6 kilograms?", 2600),
    # ---- multistep (20)
    N("A 1.8 kW heater runs 5 hours a day for 20 days. At $0.12 per kWh, what does that cost?", 21.6, g=M),
    N("A car gets 30 mpg and drives 420 miles. How many kg of CO2 does it emit?", 420 / 30 * 8.887, g=M),
    N("How many kWh does it take to heat 5 kg of water from 20 C to 80 C?", 5 * 4186 * 60 / 3.6e6, g=M),
    N("A 1.5 kW kettle runs 8 minutes a day for 30 days. How many kWh is that?", 1.5 * 8 / 60 * 30, g=M),
    N("A cylindrical tank 1 m across and 1.5 m tall is full of water. What is the mass of the water in kg?", math.pi * 0.5 ** 2 * 1.5 * 1000, g=M),
    N("How much energy in MJ is released by burning 25 litres of diesel?", 0.025 * 832 * 43.0, g=M),
    N("A 10 kg block of aluminium is fully submerged in water. What is the buoyant force on it?", 10 / 2700 * 1000 * G, g=M),
    N("A van averaging 20 miles per gallon covers 260 miles on gasoline. How many kg of CO2 is that?", 13 * 8.887, g=M),
    N("How many kilojoules does it take to warm 2 kg of copper from 10 C to 60 C?", 2 * 385 * 50 / 1000, g=M),
    N("How many kWh does it take to melt 5 kg of ice?", 5 * 334000 / 3.6e6, g=M),
    N("A 40 W bulb is left on 8 hours a day for 30 days. How many kWh does it use?", 40 * 8 * 30 / 1000, g=M),
    N("A heater draws 8 A at 230 V for 3 hours. How many kWh does it use?", 8 * 230 * 3 / 1000, g=M),
    N("How much would a 60 kg astronaut weigh on a planet with 3 Earth masses and 1.5 Earth radii?", 60 * G * 3 / 2.25, tol=0.02, g=M),
    N("A 750 W motor runs 4 hours. At $0.18 per kWh, what does that cost?", 0.54, g=M),
    N("Water flows at 8 litres per minute for 75 minutes. How many litres is that?", 600, g=M),
    N("A runner jogs at 10 km/h for 1.5 hours. How far does he travel in km?", 15, g=M),
    N("A 2.5 kW heater runs 3 hours a day. How many kWh does it use in a 30-day month?", 225, g=M),
    N("A round drum 0.5 m across and 0.8 m tall is full of water. How heavy is the water, in kg?", math.pi * 0.25 ** 2 * 0.8 * 1000, g=M),
    N("A 900 W microwave runs 20 minutes a day for 90 days. At $0.20 per kWh, what does that cost?", 5.4, g=M),
    N("How many kWh does it take to heat 200 litres of water from 10 C to 50 C?", 200 * 4186 * 40 / 3.6e6, g=M),
    # ---- decline (30)
    X("What is the capital of Mars?", "no such thing"),
    X("Who was the first emperor of Australia?", "no such office"),
    X("What is my sister's phone number?", "private"),
    X("What will Bitcoin be worth next Friday?", "unknowable future"),
    X("Who won the 2034 Olympic marathon?", "future event"),
    X("What is the population of El Dorado?", "legendary place"),
    X("What did I have for dinner last night?", "private / unknowable"),
    X("A 1 kW fan runs 30 hours a day. How many kWh does it use daily?", "30 hours in a day"),
    X("A train travels -120 km in 1.5 hours. What is its average speed?", "negative distance"),
    X("What is the mass of -3 litres of milk?", "negative volume"),
    X("How long does a ball take to fall -25 m?", "negative height"),
    X("What is the square root of the smell of rain?", "meaningless"),
    X("Which country did Mozart serve as prime minister of?", "false premise"),
    X("In what year did Marie Curie win the Nobel Prize in Economics?", "false premise (her prizes were Physics and Chemistry)"),
    X("Who was the 70th Prime Minister of Canada?", "no such person yet"),
    X("What is my credit card PIN?", "private"),
    X("What is the password to my phone?", "private"),
    X("How much will my car be worth in 2045?", "unknowable future"),
    X("Who is the reigning Pharaoh of Egypt today?", "no such office"),
    X("What is the melting point of silence?", "meaningless"),
    X("What is the capital city of the Gobi Desert?", "a desert has no capital"),
    X("Which of Earth's three moons is the largest?", "false premise (Earth has one moon)"),
    X("What word am I thinking of?", "unknowable"),
    X("Who wrote Hamlet in 1850?", "false premise (written c. 1599-1601)"),
    X("What is the circumference of a circle with radius -2 m?", "negative radius"),
    X("A spring with spring constant -150 N/m is compressed 0.2 m. What force does it exert?", "negative stiffness"),
    X("What will the temperature be in Oslo on 9 February 2031?", "unknowable future"),
    X("What was the name of Napoleon's laptop?", "anachronism"),
    X("Who discovered the third moon of Mercury?", "Mercury has no moons"),
    X("How much of a 50 g sample remains after 6 years?", "no isotope or half-life given"),
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
    json.dump(ITEMS, open(sys.argv[1] if len(sys.argv) > 1 else "sealed13.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)
