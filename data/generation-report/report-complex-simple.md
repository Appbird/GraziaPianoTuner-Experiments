# report

| model name | testcase | user-prompt | perfect | success | generated count | 備考 |
|------------|----------|-------------|--------|---------|-----------------|---|
| GPT-4o-2024-05-13 | complex       | sunny | 41 | 87 | 100 | | 
| GPT-4o-2024-05-13 | simple        | sunny | 30 | 73 | 100 | | 
| GPT-4o-2024-05-13 | super-simple  | sunny | 43 | 89 | 100 | コード進行が含まれずに生成されている曲あり |
| GPT-4o-2024-05-13 | complex       | rainy | 33 | 94 | 100 |  |
| GPT-4o-2024-05-13 | simple        | rainy | 19 | 62 | 100 |  |
| GPT-4o-2024-05-13 | super-simple  | rainy | 32 | 77 | 100 |  |
| GPT-4o-2024-05-13 | complex       | storm | 5 | 16 | 20 | |
| GPT-4o-2024-05-13 | simple        | storm | 2 | 14 | 20 | |
| GPT-4o-2024-05-13 | super-simple  | storm | 3 | 11 | 20 | |
| gpt-4-turbo-2024-04-09 | complex      | sunny | 12 | 16 | 20 | | 
| gpt-4-turbo-2024-04-09 | simple       | sunny | 9  | 14 | 20 | | 
| gpt-4-turbo-2024-04-09 | super-simple | sunny | 15 | 17 | 20 | | 
| gpt-4-0613 | complex      | sunny | 13 | 28 | 30 | | 
| gpt-4-0613 | simple       | sunny | 11 | 20 | 30 | | 
| gpt-4-0613 | super-simple | sunny | 16 | 23 | 30 | | 
| gpt-3.5-turbo-0125 | complex      | sunny | 10 | 19 | 20 | | 
| gpt-3.5-turbo-0125 | simple       | sunny |6 | 20 | 20 | | 
| gpt-3.5-turbo-0125 | super-simple | sunny | 7 | 19 | 20 | | 
| gpt-3.5-turbo-0125 | complex         | rainy | 5 | 10 | 10 | | 
| gpt-3.5-turbo-0125 | simple          | rainy | 1 | 10 | 10 | | 
| gpt-3.5-turbo-0125 | super-simple    | rainy | 4 | 9 | 10 | | 

## GPT-4o
### sunny case
- input user prompt
  - `Please compose a sunny day music.`



| testcase name | perfect | success | generated count | 
|---|---|---|---|
| 1-complex         | 11 | 18 | 20 | 
| 2-complex         | 8 | 16 | 20 |
| 3-complex         | 6 | 18 | 20 |
| 4-complex         | 10 | 17 | 20 |
| 5-complex         | 6 | 18 | 20 |
| total | 41 | 87 | 100 |

| testcase name | perfect | success | generated count | 
|---|---|---|---|
| 1-simple          | 6 | 13 | 20 |
| 2-simple          | 4 | 15 | 20 |
| 3-simple          | 4 | 14 | 20 |
| 4-simple          | 8 | 16 | 20 |
| 5-simple          | 8 | 15 | 20 |
| total | 30 | 73 | 100 |

| testcase name | perfect | success | generated count | 
|---|---|---|---|
| 1-super-simple    | 9 | 19 | 20 | 
| 2-super-simple    | 6 | 18 | 20 | 
| 3-super-simple    | 10 | 19 | 20 |
| 4-super-simple    | 11 | 19 | 20 |
| 5-super-simple    | 7 | 14 | 20 |
| total | 43 | 89 | 100 |

- `super-simple`について注意
  - 作られた曲の一部にはコード進行が含まれていない。
  - 今回作りたい曲はコード進行とメロディを含めた曲であるため、一部不適当な曲もカウントアップされている点に留意する。

### rainy case
- input user prompt
  - `Please compose a rainy day music.`

| testcase name | perfect | success | generated count | 
|---|---|---|---|
| 1-complex         | 6 | 20 | 20 | 
| 2-complex         | 7 | 19 | 20 | 
| 3-complex         | 8 | 19 | 20 |
| 4-complex         | 5 | 18 | 20 |
| 5-complex         | 7 | 18 | 20 |
| total | 33 | 94 | 100 |

| testcase name | perfect | success | generated count | 
|---|---|---|---|
| 1-simple          | 6 | 13 | 20 |
| 2-simple          | 3 | 12 | 20 |
| 3-simple          | 2 | 12 | 20 |
| 4-simple          | 6 | 13 | 20 |
| 5-simple          | 2 | 12 | 20 |
| total | 19 | 62 | 100 |

| testcase name | perfect | success | generated count | 
|---|---|---|---|
| 1-super-simple    | 8 | 18 | 20 |
| 2-super-simple    | 5 | 15 | 20 |
| 3-super-simple    | 7 | 15 | 20 |
| 4-super-simple    | 4 | 13 | 20 |
| 5-super-simple    | 8 | 16 | 20 |
| total | 32 | 77 | 100 |

### storm case

- input user prompt
  - `Please compose a storm day music.`

| testcase name | perfect | success | generated count | 
|---|---|---|---|
| complex         | 5 | 16 | 20 | 
| simple          | 2 | 14 | 20 |
| super-simple    | 3 | 11 | 20 |

## `gpt-4-turbo-2024-04-09`

- input user prompt
  - `Please compose a sunny day music.`

| testcase name | perfect | success | generated count | 
|---|---|---|---|
| complex         | 12 | 16 | 20 | 
| simple          | 9 | 14 | 20 |
| super-simple    | 15 | 17 | 20 |

## `gpt-4-0613`

- input user prompt
  - `Please compose a sunny day music.`

| testcase name | perfect | success | generated count | 
|---|---|---|---|
| 1-complex         | 7 | 18 | 20 | 
| 2-complex         | 6 | 10 | 10 | 
| total | 13 | 28 | 30 |

| testcase name | perfect | success | generated count | 
|---|---|---|---|
| 1-simple          | 8 | 14 | 20 |
| 2-simple          | 3 | 6 | 10 |
| total | 11 | 20 | 30 | 

| testcase name | perfect | success | generated count | 
|---|---|---|---|
| 1-super-simple    | 10 | 17 | 20 |
| 2-super-simple    | 6 | 9 | 10 |
| total | 16 | 23 | 30 |

## `gpt-3.5-turbo-0125`

- input user prompt
  - `Please compose a sunny day music.`

| testcase name | perfect | success | generated count | 
|---|---|---|---|
| 1-complex         | 8 | 10 | 10 | 
| 2-complex         | 2 | 9 | 10 | 
| total | 10 | 19 | 20 |

| testcase name | perfect | success | generated count | 
|---|---|---|---|
| 1-simple          | 5 | 10 | 10 |
| 2-simple          | 1 | 10 | 10 |
| total | 6 | 20 | 20 |

| testcase name | perfect | success | generated count | 
|---|---|---|---|
| 1-super-simple    | 1 | 9 | 10 |
| 2-super-simple    | 6 | 10 | 10 |
| total | 7 | 19 | 20 |

- input user prompt
  - `Please compose a rainy day music.`

| testcase name | perfect | success | generated count | 
|---|---|---|---|
| 1-complex         | 5 | 10 | 10 | 
| 1-simple          | 1 | 10 | 10 |
| 1-super-simple    | 4 | 9 | 10 |


