"""conv_tests_v2 - SEALED CONVERSATION TEST 2: does Oracle7's main model USE and COMBINE its specialists in conversation?
(Ben 2026-10-13: "make sure that oracle7 main can efficiently use and combine the specialists as needed in real
conversation"). Written by Claude on 2026-10-13 before the release head (w533) was measured on any dialogue; same author as
the folds - disclosed. Not chosen by asking the system. Run ONCE, on the release head, with run_conv_v1.py --sealed-sha.
Recipe: 20 dialogues sent turn by turn in ONE session each, built so that answering needs specialists and hand-offs:
  - follow-ups that move between specialists (a moon -> its discoverer -> where that person was born);
  - two-part turns that need two specialists in one reply;
  - chained calculations (a tank's volume -> the mass of the liquid in it -> its weight) and numeric follow-ups ("and after
    48 days?");
  - declines inside a conversation (a negative quantity after a valid one; an unknowable question).
Scoring: conv_tests_v1's rules, unchanged (fact / follow / multi / number / decline / social). Reported, fixed here before
any run: handled turns, precision on answered turns, false yes, follow-up rate, multi-part turns right, and SPECIALIST USE =
share of right answers whose path went through a specialist, a relation organ, the fusion network or a maths agent."""
import json
import math
import sys

F = lambda q, aliases: {"kind": "fact", "q": q, "expect": aliases}
U = lambda q, aliases: {"kind": "follow", "q": q, "expect": aliases}
MU = lambda q, groups: {"kind": "multi", "q": q, "expect": groups}
NU = lambda q, v, tol=0.01: {"kind": "number", "q": q, "expect": v, "tol": tol}
DE = lambda q, why: {"kind": "decline", "q": q, "expect": "decline", "why": why}
SO = lambda q: {"kind": "social", "q": q, "expect": "social"}
G = 9.80665

SEALED2 = [
    [F("Who directed Kagemusha?", ["Kurosawa"]), U("When was he born?", ["1910"]), U("Where?", ["Tokyo", "Shinagawa"]), SO("Thanks.")],
    [F("What is the capital of Bolivia's neighbour Paraguay?", ["Asunción", "Asuncion"]), U("And its currency?", ["guaraní", "guarani"]), U("Which continent is it on?", ["South America"])],
    [F("Who composed the opera The Queen of Spades?", ["Tchaikovsky"]), U("Where was he born?", ["Votkinsk"]), U("In what year did he die?", ["1893"])],
    [F("Which planet does the moon Miranda orbit?", ["Uranus"]), U("Who discovered Miranda?", ["Kuiper"]), U("Where was he born?", ["Tuitjenhorn", "Harenkarspel"])],
    [MU("Who wrote Persuasion, and who wrote Silas Marner?", [["Austen"], ["Eliot"]])],
    [NU("What is the mass of 4 litres of sea water in kg?", 4.1), NU("What does that weigh in newtons?", 4.1 * G)],
    [NU("A cylindrical tank 0.5 m across and 2 m tall is full of sea water. What is the mass of the water in kg?", math.pi * 0.25 ** 2 * 2 * 1025),
     NU("How much does that water weigh in newtons?", math.pi * 0.25 ** 2 * 2 * 1025 * G)],
    [F("Who founded Nintendo?", ["Yamauchi"]), U("When was it founded?", ["1889"]), U("Where is it headquartered?", ["Kyoto"])],
    [F("Who was the architect of the Chrysler Building?", ["Van Alen"]), U("When did it open?", ["1930"]), U("Which country is it in?", ["United States"])],
    [F("Which country did Ole Einar Bjørndalen represent?", ["Norway"]), U("When was he born?", ["1974"])],
    [F("Where was the figure skater Yuzuru Hanyu born?", ["Sendai"]), U("Which country does he represent?", ["Japan"])],
    [F("Who was Ada Lovelace's father?", ["Byron"]), U("And her mother?", ["Milbanke", "Annabella"]), U("When did she die?", ["1852"])],
    [SO("Hello!"), DE("What will I have for lunch tomorrow?", "unknowable"), F("Which constellation is Polaris in?", ["Ursa Minor"]), SO("Cheers, bye.")],
    [NU("A 1.5 kW heater runs 4 hours a day. How many kWh does it use in a week?", 42), NU("At $0.25 per kWh, what does that cost?", 10.5)],
    [MU("What is the capital of Kenya, and what is 20% of 450?", [["Nairobi"], ["90"]])],
    [F("Who wrote The Captain's Daughter?", ["Pushkin"]), U("Where did he die?", ["Saint Petersburg", "St Petersburg", "St. Petersburg"]),
     U("Who was he married to?", ["Goncharova"])],
    [NU("How much of a 40 g sample of iodine-131 remains after 24 days?", 40 * 0.5 ** (24 / 8.0252)),
     NU("And after 48 days?", 40 * 0.5 ** (48 / 8.0252))],
    [NU("What is the mass of 2 litres of water in kg?", 1.996), DE("And of -2 litres?", "negative volume")],
    [F("Which planet is Io a moon of?", ["Jupiter"]), U("Who discovered Io?", ["Galileo"]), U("Where was he born?", ["Pisa"])],
    [F("Who directed Spirited Away?", ["Miyazaki"]), U("When was he born?", ["1941"]), SO("Great, thank you.")],
]


def check():
    turns = [t for d in SEALED2 for t in d]
    assert len(SEALED2) == 20
    kinds = {}
    for t in turns:
        kinds[t["kind"]] = kinds.get(t["kind"], 0) + 1
    return len(turns), kinds


if __name__ == "__main__":
    print(check())
    json.dump(SEALED2, open(sys.argv[1] if len(sys.argv) > 1 else "conv_sealed_v2.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)
