# Oracle7 Nutrition (label & public-health arithmetic) (#62, tier C)

**id** `nutrition-label-v2` - organ `organ_nutrition_label_v2.NutritionLabelOrganV2` composed in front of the frozen head `oracle_release_runtime_w503`.

## Verdict

- decision: **ADMIT** (gate v2)
- held-out domain: specialist 16/16 (false yes 0) vs head 2/16 (false yes 0)
- core capability panel: head 160 -> composed 160 (0 items swept in by the full sweep)
- reasons: none

## Sources and licences

- FDA Nutrition Facts label Daily Values (2020 rule) and Atwater factors 4/4/9/7 (public domain (US government)) https://www.fda.gov/food/nutrition-facts-label/daily-value-nutrition-and-supplement-facts-labels
- CDC adult BMI calculation and categories (public domain (US government)) https://www.cdc.gov/bmi/adult-calculator/bmi-categories.html

## What it takes

- answers: bmi, bmi_category, kcal_macros, pct_dv, pct_fat_cal
- declines (in-domain): underspecified
- everything else falls through to the head unchanged

## Notes and known gaps

v2 of nutrition-label (v1 NEGATIVE 2026-09-29: '150-calorie snack ... percent of its calories are from fat' unread -> head computed 3/150). Reads N-calorie and the 'of its calories' forms; recognise-then-decline on numeric label turns; personal advice still falls through. Fresh panel v2.
