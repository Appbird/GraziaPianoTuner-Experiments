# report-ablation
- Model: `GPT-4o`
- Tempareture: `1.0`
- input user prompt: `Please compose a sunny day music.`

## summary

| testcase name          | perfect | success | generated count |
|------------------------|---------|---------|-----------------|
| without_piano          | 41      | 87      | 100             |
| without_examples       | 22      | 63      | 100             |
| with_guitar            | 38      | 86      | 100             |
| without_guideline      | 51      | 69      | 100             |
| without_refine_pattern | 73      | 92      | 100             |


## first_trial

| testcase name | perfect | success | generated count | 
|---|---|---|---|
| without_piano | 7 | 16 | 20 | 
| without_examples | 3 | 11 | 20 | 
| with_guitar | 7 | 16 | 20 | 
| without_guideline | 10 | 13 | 20 | 
| without_refine_pattern | 16 | 18 | 20 |

## second_trial

| testcase name | perfect | success | generated count | 
|---|---|---|---|
| without_piano | 10 | 17 | 20 | 
| without_examples | 2 | 11 | 20 | 
| with_guitar | 10 | 18 | 20 | 
| without_guideline | 9 | 12 | 20 | 
| without_refine_pattern | 17 | 18 | 20 |

## third_trial

| testcase name | perfect | success | generated count | 
|---|---|---|---|
| without_piano | 8 | 18 | 20 | 
| without_examples | 7 | 14 | 20 | 
| with_guitar | 6 | 18 | 20 | 
| without_guideline | 10 | 15 | 20 | 
| without_refine_pattern | 15 | 19 | 20 |

## forth_trial

| testcase name | perfect | success | generated count | 
|---|---|---|---|
| without_piano | 6 | 17 | 20 | 
| without_examples | 4 | 14 | 20 | 
| with_guitar | 8 | 20 | 20 | 
| without_guideline | 13 | 15 | 20 | 
| without_refine_pattern | 11 | 18 | 20 |

## fifth_trial

| testcase name | perfect | success | generated count | 
|---|---|---|---|
| without_piano | 10 | 19 | 20 | 
| without_examples | 6 | 13 | 20 | 
| with_guitar | 7 | 14 | 20 | 
| without_guideline | 9 | 14 | 20 | 
| without_refine_pattern | 14 | 19 | 20 |

## additional

| testcase name | perfect | success | generated count | 
|---|---|---|---|
| 1-without_refine_pattern_guideline | 9 | 18 | 20 | 
| 2-without_refine_pattern_guideline | 15 | 18 | 20 |
| 3-without_refine_pattern_guideline | 13 | 15 | 20 |