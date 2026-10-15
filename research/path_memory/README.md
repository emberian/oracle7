# Path memory: built, measured, not switched on

Path memory is Oracle7's mechanism for learning which routes to trust. A route is a chain of specialists, organs or a reader. The memory learns which routes give answers that check out, for which kind of question, using verified outcomes only. It is built in the core's own algebra:
- each path is one HRR vector, made by binding the question's shape (its lead word, the relation reader that recognises it, whether it carries numbers) to the route that answered;
- the codebook is `osub_seed`, D = 1024;
- a path never seen before borrows the credit of the most similar stored path on the same route.

## What it was trained on

The training data is 4,804 graded questions from development pools only:
- TriviaQA train;
- Mintaka train;
- the development split of every admitted specialist's exam.

No sealed-test question and no reported benchmark window was used. For each question we recorded the main model's answer, its route and its grade, plus the relation-specialist family's answer to the same question and that answer's grade.

## How it was judged

1. **Choosing the policy.** It was chosen on 80% of the data, using sealed test 15's own pass rule: more right answers, no more wrong ones, precision not lower.
2. **Checking on the held-back 20% (965 questions):**

   | | Right | Wrong | Precision |
   |---|---:|---:|---:|
   | Fixed routing | 470 | 56 | 89.4% |
   | Path memory (swap only) | 475 | 51 | 90.3% |
   | Path memory (swap or withhold) | 468 | 30 | 94.0% |

   The swap-or-withhold variant was not chosen because it loses right answers, which the sealed rule forbids. The held-back fifth was looked at for three policy families. That is disclosed.

3. **Sealed test 15, run once on each arm.** Arm A was the fixed-routing head (w534); arm B was the same head plus path memory (w535). On both parts, 150 single questions and 20 dialogues, the results were identical: 114 right, 2 wrong, 0 false yeses. On questions it had never seen, the memory found no route to swap. The pre-registered rule required more right answers, so path memory is **not switched on** in the released model.

## What did ship from it

The credit data showed one large, plain pattern. On questions a relation reader recognises, when another route answered and the relation family answered too, the outcomes were:

| Other route | Relation family | Count |
|---|---|---:|
| right | right | 140 |
| wrong | right | 34 |
| wrong | wrong | 5 |
| right | wrong | 0 |

That pattern became a fixed rule in fold w536: on such questions the family's answer takes precedence. When the family cannot answer and path memory rates the answering route below 0.5 for that kind of question, the answer is withheld. w536 went through the gate like every other change. Sealed test 16 measured it and it passed every bar. The release adds folds w537 and w538 and is measured by sealed test 17.

## Files

| File | What it is |
|---|---|
| `path_memory_v1.py` | the memory: shapes, routes, HRR path vectors, credit, recall |
| `path_memory_v1.json` | the memory built from all 4,804 graded outcomes |
| `path_credit_gen_v1.py` | how the graded outcomes were produced |
| `path_memory_tune_v1.py`, `path_memory_tuning_v1.json` | policy choice and the held-back report |
| `oracle_release_runtime_w535.py` | the fold that would switch it on |
| `sealed15_result_armA_w534.json`, `sealed15_result_armB_w535.json` | the two single runs of sealed test 15 |
| `conv15_armA_w534.json`, `conv15_armB_w535.json` | the two dialogue runs |
