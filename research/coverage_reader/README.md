# The general relation reader: how it was measured

Fold w539 adds `general_reader_v1` (in `root/wander-train/`). It runs only when the core declined for lack of a reading.
It answers a question one Wikidata fact away from a thing the question names, and every answer carries the record it read.

The reader answers only when every one of these conditions holds:

- The question's own words name the relation, through the property's label or one of its aliases.
- The answer is the kind of thing that was asked for:
  - a person for "who";
  - a city or a country for "which city" or "which country", checked against the answer's own classes;
  - the named relation itself for "what is the capital of".
- Exactly one candidate answer remains.
- The relation is one that the admitted relation specialists also read.
- Every name in the question is one the reader linked.
- When the question names two or more things, at least two of them agree on the answer.

It declines on:

- a turn that names a year;
- a private question;
- a question with several parts;
- a question carrying a qualifier such as "when", "during", "before" or "nickname".

## Held-out runs (each run once; data never used to build it)

All three runs used TriviaQA (`mandarjoshi/trivia_qa`, `rc.nocontext`, train split) at offsets the reader was never developed on.

| Run | Data | Answered | Right (scorer) | Right (judged) | Precision | Bar 95% |
|---|---|---:|---:|---:|---:|---|
| v6 | offset 100000, 2,000 questions | 17 | 14 | 16 | 94.1% | failed |
| v7 | offset 120000, 6,000 questions | 68 | 62 | 63 | 92.6% | failed |
| **v10** | **offset 130000, 6,000 questions** | **82** | **80** | **81** | **98.8%** | **passed** |

The two failed runs showed one cause. When the question named something the reader could not link (Jennings Brewery,
Dismaland), the reader answered about the nearest thing it could link (Cumbria, Banksy). Its "which country" check also
let a city through (Peter Hain → Nairobi). Three changes fixed this:

- a name the reader cannot link stops it;
- two named things must agree on the answer;
- place types are checked on the answer's own classes.

The development data was the offsets 40000, 60000 and 80000, plus the two spent held-out sets: 14,000 questions in all.
On these the reader answered 99 and got 96 right by the scorer.

**The judging rule** (`adjudicate_v1.py`, SHA-256 `37c8329f…`) was written and hashed before the v10 run. It counts an
answer the scorer marked wrong as right only if the answer is a place that the relation store records inside the
expected place. In v10 that applied once: Rupelmonde is in Belgium, which is the answer key's "Belgium". Every other
disagreement stays wrong, including this one:

- What is the currency of Bulgaria? The reader answered Euro, from Wikidata; the key says Lev. Bulgaria adopted the
  euro on 1 January 2026, so the key is out of date. The rule does not cover this, so it counts as wrong.

**Hashes recorded before the v10 run** (`coverage_heldout_v10.hashes`):

| File | SHA-256 |
|---|---|
| reader | `429e1e4b…` |
| allowlist | `dfe5d802…` |
| judging rule | `37c8329f…` |
| question set | `7ae9fc9a…` |
| time | 2026-10-14T13:14:52Z |

## Coverage

The reader is precise but narrow. It answered 82 of 6,000 trivia questions, about 1.4%, on top of what the core already
answers. That is the trade the release makes everywhere: an answer with its record, or a decline.

## Files

- `general_reader_v1.py`: the reader as shipped.
- `adjudicate_v1.py`: the judging rule.
- `coverage_heldout_v10.hashes`, `coverage_heldout_v10.log`, `coverage_heldout_v10_result.json`: the passing run.
- `coverage_heldout_v6.log`, `coverage_heldout_v7.log`: the failed runs.
- `coverage_eval_v9.log`: development.
