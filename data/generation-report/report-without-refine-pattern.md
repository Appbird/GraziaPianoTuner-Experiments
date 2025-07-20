# report-ablation
- Tempareture: `1.0`
- input system prompt: `without-refine-pattern`

## first_trial (rainy)

- input user prompt: `Please compose a rainy day music.`

| model name          | perfect | success | generated count |
|---------------------|---------|---------|-----------------|
| gpt-4o-2024-05-13   | 64      | 98      | 100             |


| model name | perfect | success | generated count | 
|---|---|---|---|
| gpt-4o-2024-05-13 | 13 | 19 | 20 |
| gpt-4o-2024-05-13 | 12 | 19 | 20 |
| gpt-4o-2024-05-13 | 13 | 20 | 20 |
| gpt-4o-2024-05-13 | 13 | 20 | 20 |
| gpt-4o-2024-05-13 | 13 | 20 | 20 |

- `rainy3/5.wav`がなんかすき

## second_trial

- input user prompt: `Please compose a sunny day music.`

| model name             | perfect | success | generated count |
|------------------------|---------|---------|-----------------|
| gpt-3.5-turbo-0125     | 23      | 39      | 40              |
| gpt-4-0613             | 22      | 39      | 40              |
| gpt-4-turbo-2024-04-09 | 32      | 36      | 40              |
| gpt-3.5-turbo-0125     | 44 | 60 | 60 |
| gpt-4-0613             | 40 | 56 | 60 |
| gpt-4-turbo-2024-04-09 | 51 | 59 | 60 |

- input user prompt: `Please compose a rainy day music.`

| model name | perfect | success | generated count | 
|---|---|---|---|
| gpt-3.5-turbo-0125 | 10 | 20 | 20 |
| gpt-3.5-turbo-0125 | 13 | 19 | 20 |
| gpt-4-0613 | 8 | 19 | 20 |
| gpt-4-0613 | 14 | 20 | 20 |
| gpt-4-turbo-2024-04-09 | 18 | 19 | 20 |
| gpt-4-turbo-2024-04-09 | 14 | 17 | 20 |
| gpt-3.5-turbo-0125 | 27 | 57 | 60 |
| gpt-4-0613 | 38 | 53 | 60 |
| gpt-4-turbo-2024-04-09 | 41 | 52 | 60 |


