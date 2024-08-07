# summary

## 結果の見方
- `system prompt name` -- `role`を`System`として入力したテキストの種別を表す。
- `user prompt` -- `role`を`User`として入力したテキストの種別を表す。
  - 種別の名前と、実際のプロンプトの対応関係については[Katayose-lab Scrapbox](https://scrapbox.io/katayose-lab/EC2024SI_:_プロンプトの有効性検証;_実験に使用したプロンプト)を参照。
- `model name` -- 実験に使用したモデルの名前を表す。
  - 種別の名前と、実際のプロンプトの対応関係については[Katayose-lab Scrapbox](https://scrapbox.io/katayose-lab/EC2024SI_:_プロンプトの有効性検証;_実験に使用したプロンプト)を参照。
- `generated count` -- 曲を生成した試行回数
  - `perfect` -- abc2midiにおいて警告が出ず曲が生成された回数
    - よく出る警告の一つに「一小節あたりの長さが曲の拍数と合っていない」というものがある。
    - 「この警告が多くのケースにおいて出なかった」ということは、拍節構造を理解した上で正しく曲を生成できていることを意味する。
  - `success` -- abc2midiにおいてエラーが出ず曲が生成された回数
    - `success`でないとしてカウントされた場合、生成された楽曲はABC記譜法として変換できないものであることを意味する。
      - 具体的な原因として
        - `X`ヘッダなど、ABC記譜法において必須なヘッダ情報が抜けている。
        - 音符に対する臨時記号として、ABC記譜法において使用される`^_`ではなく、記号`#b`を利用している。
    - 「このエラーが多くのケースにおいて出なかった」ということは、ABC形式として最低限必要な要素をしっかり押さえて楽譜を記述できていることを意味する。
  
- Temparetureは全て`1.0`として設定している。

## 1. Ablation Study

- Model: `GPT-4o-2024-05-13`
- user prompt: `Please compose a sunny day music.`

| system prompt name     | perfect | success | generated count | 備考 |
|------------------------|---------|---------|-----------------|-|
| super-simple           | 43      | 89      | 100             | コード進行が含まれず生成された曲あり | 
| simple                 | 30      | 73      | 100             | |
| without_piano          | 41      | 87      | 100             | |
| without_examples       | 22      | 63      | 100             | |
| with_guitar            | 38      | 86      | 100             | |
| without_guideline      | 51      | 69      | 100             | |
| without_refine_pattern | 73      | 92      | 100             | |
| complex                | 41      | 87      | 100             | |

- pianoを含めるか、guitarを含めるかどうかはあまり結果に影響しない。
- exampleを抜くと、生成が著しく不安定になる。
- guidelinesにおいても、コンパイルの成功確率が著しく落ちる。
- refine_patternを抜いた時の方が一番安定する。
  - 一般的なタスクにおいてrefine patternは良いと考えられるが、音楽生成においては有効ではないことが推察される。

## 2. Compare with Simple Prompts

- Model: `GPT-4o-2024-05-13`
- Tempareture: `1.0`
- user prompt: `Please compose a sunny day music.`

1 Ablation Studyで最も優秀な成果を出した、`without_refine_pattern`を、他のケースにおいても比較してみる。

| system prompt name | user-prompt | perfect | success | generated count | 備考 |
|----------|-------------|--------|---------|-----------------|---|
| super-simple              | sunny | 43 | 89 | 100 | コード進行が含まれずに生成されている曲あり |
| simple                    | sunny | 30 | 73 | 100 |  | 
| without_refine_pattern    | sunny | 73 | 92 | 100 |  |
| simple                    | rainy | 19 | 62 | 100 |  |
| super-simple              | rainy | 32 | 77 | 100 |  |
| without_refine_pattern    | rainy | 64 | 98 | 100 |  |

- `sunny`よりも、`rainy`の方が全体的に生成が不安定になりやすい。
- その中でも、`without_refine_pattern`はコンパイル成功率を保ったまま、perfect率がトップのままである。

## 3. Compare on other models

1 Ablation Studyで最も優秀な成果を出した、`without_refine_pattern`が他のモデルだとどう出力を見せるかを比較してみる。

## user promptが`sunny`であった場合

| model name             | perfect | success | generated count |
|------------------------|---------|---------|-----------------|
| gpt-3.5-turbo-0125     | 67      | 99      | 100             |
| gpt-4-0613             | 62      | 95      | 100              |
| gpt-4-turbo-2024-04-09 | 83      | 95      | 100              |
| GPT-4o-2024-05-13      | 73      | 92      | 100             |
| Gemini-1.5-Pro-001     | 14      | 34      | 100             |

## user promptが`rainy`であった場合

| model name             | perfect | success | generated count |
|------------------------|---------|---------|-----------------|
| gpt-3.5-turbo-0125     | 50      | 96      | 100             |
| gpt-4-0613             | 60      | 92      | 100             |
| gpt-4-turbo-2024-04-09 | 73      | 88      | 100             |
| GPT-4o-2024-05-13      | 64      | 98      | 100             |
| Gemini-1.5-Pro-001     | 4       | 34      | 100             |

- こちらでも`rainy`の方が不安定になりやすいとわかる。
  - その中でも、`gpt-3.5-turbo-0125`は大きくperfectの率を落としてしまった。
- ほぼ全てのケースにおいて、同じ程度の`success`率を見せた。
  - そのなかでも特に高いのが`GPT-4o-2024-05-13`だった。
- `perfect`率は、`gpt-4-turbo-2024-04-09`の方が高い。
- なお、生成速度が一番早いのは、`gpt-3.5-turbo-0125`と`GPT-4o-2024-05-13`である。