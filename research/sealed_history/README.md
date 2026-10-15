# Sealed history: tests 12-17 and the conversation tests

Every sealed test was written and hashed before the build it measured, and run once. Failures stay published. All tests were written by the same author as the system; that is disclosed.

## Single-question tests

Each has 150 questions: 70 knowledge, 30 exact, 20 multi-step, 30 that must be declined. Bars: precision on answered at least 90%, at most 2 false yeses, 0 format defects.

| Test | Head | Full | Slim | Verdict |
|---|---|---|---|---|
| 12 | w406 | 111 right, 12 wrong, 5 false yes | 109 right, 10 wrong, 5 false yes | failed (false yes) |
| 13 | w532 | 114 right, 10 wrong, 1 false yes, 1 format defect | precision 89.2% | failed (format; slim precision) |
| 14 | w533 | 115 right, 9 wrong, 3 false yes | 111 right, 6 wrong, 3 false yes | failed by one (false yes) |
| 15 | w534 | 114 right, 2 wrong, 0 false yes | 109 right, 3 wrong, 0 false yes | passed every bar |
| 16 | w536 | 113 right, 3 wrong, 0 false yes | 109 right, 1 wrong, 0 false yes | passed every bar (carried to w537 with 0 differences) |
| 17 | w538 | 111 right, 5 wrong, 1 false yes | 108 right, 3 wrong, 1 false yes | passed every bar: the release gate |

Test 16 was run once on RC13e, then replayed on head w537 with zero reply differences on all 150 questions in both variants. Fold w538 then changed reply text, so test 17 was written fresh and run once on the release itself: precision 95.3% full, 97.5% slim.

What each failure was, and what fixed it:

- **Test 12:**
  - Two specialists dropped a minus sign.
  - Private questions were answered with encyclopedia sentences.
  - A false date premise was answered.
  - Fixed by fold w532.
- **Test 13:**
  - A thousands separator was misread ("2,025" as 2).
  - A fraction was handed back unconverted.
  - Unit letters were treated as algebra.
  - Mercury the metal was read as the planet.
  - Fixed by fold w533.
- **Test 14:** the answer guards ran before a specialist family. Fixed by fold w534.

## Conversation tests

| Test | Turns | Run on | Handled | Precision | False yes | Follow-ups right |
|---|---:|---|---:|---:|---:|---:|
| 1, run 2 | 88 | w526 (before the conversation fold) | 46.6% | 63.6% | 0 | 5.7% |
| 1, run 3 | 88 | w533 (after it) | 71.6% | 90.9% | 0 | 51.4% |
| 2 | 51 | w533 | 62.7% | 83.9% | 0 | 52.4% |
| 3, arm A | 49 | w534 | 63.3% | 89.7% | 0 | 60.0% |
| 4 | 49 | w536 | 67.3% | 77.8% | 0 | 70.0% |
| 5 | 49 | w538 (the release) | 77.6% | 94.4% | 0 | 90.0% |

Conversation test 4 found a regression in w536 (a two-part turn lost its second answer; fixed by w537) and three conversation defects (fixed by w538). Test 5, written afterwards, measures the release.

## Files

- `sealed1[2-7].json`: the questions.
- `sealed1[3-7]_questions.py`: the generators, with the scoring rules in their docstrings.
- `sealed1[2-7]_result_*.json`: every single run.
- `conv_sealed_v[1-5].json`: the dialogue tests.
- `conv*_run*.json`: the runs.
