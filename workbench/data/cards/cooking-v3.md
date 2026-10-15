# Oracle7 Cooking & Nutrition v3 (#61, tier A)

**id** `cooking-v3` - organ `organ_nutrition_v3.NutritionOrganV3` composed in front of the frozen head `oracle_release_runtime_w363`.

## Verdict

- decision: **ADMIT** (gate v2)
- held-out domain: specialist 224/228 (false yes 0) vs head 10/228 (false yes 0)
- core capability panel: head 160 -> composed 160 (0 items swept in by the full sweep)
- reasons: none

## Sources and licences

- USDA FoodData Central SR Legacy 2018-04 (public domain (US government work)) https://fdc.nal.usda.gov/
- Project Gutenberg cookbooks (2,533 recipes, already in the core via the conversation organ) (public domain) https://www.gutenberg.org/

## What it takes

- answers: nutrient
- declines (in-domain): unknown_food, no_value, no_portion, clarify
- everything else falls through to the head unchanged

Supersedes: cooking-v2 (ADMIT gate v2, 155/210; misses = 'Can you give me the X content of ...' lost its question word)

## Notes and known gaps

v3 = v2 + 'What is' restored when frame stripping leaves no question word. Judged under spec_gate_v2 on a FRESH panel (new seeds, new phrasings both splits including the class). Same author - disclosed. Earlier notes: v2 = v1 + one defect-class fix found by v1's held-out verdict: the question frame (contractions, content/amount/level/value, polite frames) leaked into the food name and v1 declined (59 held-out misses, all safe declines). Judged on a FRESH panel v2: seed 6161, a different food partition, new frame-heavy phrasings for both splits, new invented foods. v1's held-out stays sealed. Same author wrote the organ and the fresh phrasings - disclosed.
