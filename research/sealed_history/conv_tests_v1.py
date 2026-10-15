"""conv_tests_v1 - the CHAT instruments for RC13 (Ben 2026-10-09: "we have what we need for a proper chat model ... 10x chat").

Two sets, written by Claude on 2026-10-09 BEFORE any chat code (same author - disclosed):
  SEALED  conversation test 1 (multi-turn dialogues). Hashed before any chat work. Run exactly THREE times, each once:
          (1) w496 - the head the old 543-turn instrument measured (where chat stood), (2) the head just before the chat fold,
          (3) the head after the chat fold. Runs 1 and 2 report COUNTS ONLY - their items are never read, so nothing in the
          test can shape the build; only run 3's items may be read. The 10x claim is measured here and nowhere else.
  DEV     open dialogues of the same recipe for building the chat fold; tune on these only.
Turn kinds (scored by run_conv_v1.py, fixed here before any run):
  fact     the reply must contain one alias (case-insensitive substring); declining = missed, wrong text = wrong
  follow   a FACT turn that only makes sense through the conversation (pronoun, ellipsis, "and its ...") - same scoring
  multi    a turn with two or more questions: every listed alias group must be present (partial = wrong)
  number   the first number in the reply (not one of the turn's own givens) within tol of expect
  decline  must not be answered (status answered = false yes)
  social   greeting / thanks / goodbye: any reply that is not a refusal or a request to rephrase counts as handled
A dialogue is sent turn by turn in ONE session. Metrics: handled turns (right + social handled + declines kept), precision on
answered fact/follow/multi/number turns, false yes, and the follow-up rate (follow turns right / follow turns)."""

F = lambda q, aliases: {"kind": "fact", "q": q, "expect": aliases}
U = lambda q, aliases: {"kind": "follow", "q": q, "expect": aliases}
MU = lambda q, groups: {"kind": "multi", "q": q, "expect": groups}
NU = lambda q, v, tol=0.01: {"kind": "number", "q": q, "expect": v, "tol": tol}
DE = lambda q, why: {"kind": "decline", "q": q, "expect": "decline", "why": why}
SO = lambda q: {"kind": "social", "q": q, "expect": "social"}

SEALED = [
    [F("Who wrote The Old Man and the Sea?", ["Hemingway"]), U("Where was he born?", ["Oak Park"]), U("When did he die?", ["1961"]), SO("Thanks!")],
    [F("What is the capital of Ghana?", ["Accra"]), U("And its currency?", ["cedi"]), U("Which continent is it on?", ["Africa"]),
     U("What is its official language?", ["English"])],
    [F("Who painted The Starry Night?", ["Gogh"]), U("Where was he born?", ["Zundert"]), U("In what year did he die?", ["1890"])],
    [F("Which planet does Titan orbit?", ["Saturn"]), U("Who discovered it?", ["Huygens"]), U("In what year?", ["1655"])],
    [F("Who composed The Magic Flute?", ["Mozart"]), U("Where was he born?", ["Salzburg"]), U("Who was his father?", ["Leopold"])],
    [SO("Hi there!"), F("Who founded Microsoft?", ["Gates", "Allen"]), NU("What's 15% of 80?", 12), SO("Thanks, that's all.")],
    [DE("Who is the current King of the United States?", "no such office"), F("Who was the first President of the United States?", ["Washington"]),
     U("Where was he born?", ["Westmoreland", "Popes Creek", "Virginia"])],
    [NU("A 2 kW heater runs 5 hours a day. How many kWh does it use in 30 days?", 300), NU("At $0.20 per kWh, what does that cost?", 60)],
    [F("Who wrote Frankenstein?", ["Mary Shelley", "Shelley"]), U("Who was her mother?", ["Wollstonecraft"]), U("Who was she married to?", ["Percy"])],
    [F("Who directed Jaws?", ["Spielberg"]), U("When was he born?", ["1946"]), U("Where?", ["Cincinnati"])],
    [F("Which country is Machu Picchu in?", ["Peru"]), U("What's the capital of that country?", ["Lima"]), U("And the currency?", ["sol"])],
    [NU("Solve for x: 3x + 4 = 19.", 5), NU("What is x squared?", 25)],
    [NU("How long does a stone take to fall 20 m?", 2.0196), NU("And on the Moon?", 4.969, 0.02)],
    [DE("What did I have for dinner last night?", "private"), F("What is the currency of Sweden?", ["krona"]), U("And of Denmark?", ["krone"])],
    [F("Who wrote Crime and Punishment?", ["Dostoevsky", "Dostoyevsky"]), U("Where did he die?", ["Saint Petersburg", "St. Petersburg", "St Petersburg"]),
     U("What nationality was he?", ["Russia"])],
    [MU("What is the capital of Austria and what is its currency?", [["Vienna"], ["euro"]]), SO("Great, thanks.")],
    [F("Who directed Lawrence of Arabia?", ["Lean"]), U("And Doctor Zhivago?", ["Lean"]), DE("What was his favourite colour?", "unknowable / not recorded")],
    [F("Which planet does Io orbit?", ["Jupiter"]), U("And Phobos?", ["Mars"]), U("And Triton?", ["Neptune"])],
    [F("Who painted The Last Supper?", ["Leonardo"]), U("Where was he born?", ["Vinci", "Anchiano"]), U("When did he die?", ["1519"])],
    [SO("Good morning!"), F("What is the capital of Kenya?", ["Nairobi"]), U("Which continent is Kenya on?", ["Africa"]), SO("Bye!")],
    [F("Who composed Swan Lake?", ["Tchaikovsky"]), U("And The Nutcracker?", ["Tchaikovsky"]), U("Where was he born?", ["Votkinsk"])],
    [NU("What is the area of a circle with radius 5 m?", 78.54), NU("And with radius 10 m?", 314.16)],
    [DE("Which team will win the next World Cup?", "unknowable future"), F("Who won the 2014 FIFA World Cup?", ["Germany"]),
     F("Which city hosted the 2016 Summer Olympics?", ["Rio"])],
    [F("Who wrote Jane Eyre?", ["Charlotte Brontë", "Charlotte Bronte"]), U("Where was she born?", ["Thornton"]), U("When did she die?", ["1855"])],
    [NU("How much energy in MJ does burning 5 kg of coal release?", 129), NU("And how much CO2 does that emit, in kg?", 12.2, 0.02)],
    [F("What is the official language of Brazil?", ["Portuguese"]), U("And of Mexico?", ["Spanish"]), DE("What language will people speak there in 3000?", "unknowable")],
    [F("Who discovered penicillin?", ["Fleming"]), U("Where was he born?", ["Darvel", "Lochfield"]), SO("Interesting, thank you.")],
    [MU("Who wrote Hamlet and who wrote Faust?", [["Shakespeare"], ["Goethe"]]), F("Where was Goethe born?", ["Frankfurt"])],
    [F("Which river flows through Cairo?", ["Nile"]), DE("How many fish are in it right now?", "unknowable"), F("What is the capital of Egypt?", ["Cairo"])],
    [F("Who is the author of The Hobbit?", ["Tolkien"]), U("Where was he born?", ["Bloemfontein"]), U("When did he die?", ["1973"]), SO("Cheers!")],
]

DEV = [
    [F("Who wrote Moby-Dick?", ["Melville"]), U("Where was he born?", ["New York"]), U("When did he die?", ["1891"])],
    [F("What is the capital of Peru?", ["Lima"]), U("And its currency?", ["sol"]), U("Which continent is it on?", ["South America"])],
    [F("Who painted Guernica?", ["Picasso"]), U("Where was he born?", ["Málaga", "Malaga"]), U("In what year did he die?", ["1973"])],
    [F("Which planet does Europa orbit?", ["Jupiter"]), U("Who discovered it?", ["Galileo"])],
    [F("Who composed The Four Seasons?", ["Vivaldi"]), U("Where was he born?", ["Venice"]), U("When did he die?", ["1741"])],
    [SO("Hello!"), F("Who founded Apple?", ["Jobs", "Wozniak", "Wayne"]), SO("Thank you.")],
    [NU("A 1.5 kW kettle runs 2 hours a day. How many kWh does it use in 10 days?", 30), NU("At $0.30 per kWh, what does that cost?", 9)],
    [F("Who wrote Pride and Prejudice?", ["Austen"]), U("Where was she born?", ["Steventon"]), U("When did she die?", ["1817"])],
    [F("Who directed Psycho?", ["Hitchcock"]), U("When was he born?", ["1899"]), U("Where?", ["London", "Leytonstone"])],
    [F("Which country is the Taj Mahal in?", ["India"]), U("What's the capital of that country?", ["Delhi"]), U("And the currency?", ["rupee"])],
    [NU("Solve for x: 2x - 6 = 10.", 8), NU("What is x squared?", 64)],
    [NU("How long does a stone take to fall 45 m?", 3.029), NU("And on Mars?", 4.926, 0.02)],
    [F("What is the currency of Norway?", ["krone"]), U("And of Iceland?", ["króna", "krona"])],
    [MU("What is the capital of Hungary and what is its currency?", [["Budapest"], ["forint"]])],
    [F("Which planet does Charon orbit?", ["Pluto"]), U("And Deimos?", ["Mars"])],
    [F("Who composed Carmen?", ["Bizet"]), U("Where was he born?", ["Paris"])],
    [NU("What is the area of a circle with radius 2 m?", 12.566), NU("And with radius 4 m?", 50.265)],
    [F("Who wrote Wuthering Heights?", ["Emily Brontë", "Emily Bronte"]), U("When did she die?", ["1848"])],
    [NU("How much energy in MJ does burning 10 kg of wood release?", 156), NU("And how much CO2 does that emit, in kg?", 17.47, 0.02)],
    [F("What is the official language of Argentina?", ["Spanish"]), U("And of Angola?", ["Portuguese"])],
    [MU("Who wrote Macbeth and who wrote Don Quixote?", [["Shakespeare"], ["Cervantes"]])],
    [F("Who is the author of The Lord of the Rings?", ["Tolkien"]), U("When was he born?", ["1892"])],
    [DE("What is my neighbour's phone number?", "private"), F("What is the capital of Japan?", ["Tokyo"]), U("And of South Korea?", ["Seoul"])],
]
