# GPT-4のプロンプトエンジニアリングによる対話的音楽生成の実現: 実験リポジトリ

このリポジトリでは、情報処理学会 2024年度12月号エンタテインメントコンピューティング特集号に向けて
投稿された論文「GPT-4のプロンプトエンジニアリングによる対話的音楽生成の実現」にて、
実験の際に使用したコード・データ・プロンプトについて掲載しています。

# ディレクトリの説明
- `prompts`: `role`が`system`であるような入力において、使用したプロンプトを掲載しています。
- `report`: 結果についてまとめた書類を掲載しています。
- `src`: 実験において使用したコードを掲載しています。
  - `experiment.py`: エントリポイント。GPT-4 APIにリクエストを送信するコードを主に示しています。（ここでは、論文中「第3章 プロンプトインタプリタの構築と検証」にて使用されたコードが載せられています。）
  - `experiment_parameters.py`, `experiment_modification.py`
    - 論文中「第5.1節 フリーフォーマットの指示による楽曲編集の評価」・「第5.2節 概念パラメタによる楽曲制御の性能評価」において利用されたコードが掲載されています。
  - `conversion/answer2abc.py`: GPT4-APIから返却された回答からABC形式に変換するためのコードを示しています。
  - `conversion/abc2audio.py`: ABC形式をMIDI, wavの音声ファイルに変換するコードを示しています。

# プログラムの機能
- プログラム`./src/experiment.py`を実行すると、次のことが行われます。
  - `MODEL_NAME`に指定したGPT-4モデルに対して、
  - 温度を`TEMPARATURE`に指定した上で
  - `NUM_TRIALS`回、音楽生成のためにChat Completionタスクを行うようリクエストします。[*1]
  - Chat Completionタスクが終わり、レスポンスが帰ってきたら
    - システムはそのレスポンスからABC形式の楽譜を抽出し、前処理[*2]を行った上で
    - ABC形式の楽譜をMIDI形式に変換し
    - MIDI形式をwav形式に変換します。
    - 実行結果は、`./result/{MODEL_NAME}/{実行に使ったシステムプロンプトのファイル名}/`に全て格納されます。
      - ファイル名は、そのファイルが何回目の試行において生成されたものかを表します。
      - `*.ans`: GPT-4の出力
      - `*.abc`: システムが生成した楽曲（ABC記譜法）
      - `*.mid`: システムが生成した楽曲（MIDIデータ）
      - `*.wav`: システムが生成した楽曲（wavデータ）
      - `error.log`: それぞれの生成において発生したエラーのログ



[*1]
- 入力はメッセージの系列（長さ2）からなります。
  1. `role`を`system`とし、`content`をフォルダ`prompts`に含まれているテキストファイルの中身とする。（このプロンプトをシステムプロンプトとする）
  2. `role`を`user`とし、`content`を`USER_PROMPT`に含まれている文字列とする。
- 以上二つのメッセージの系列に対して、Chat Completionタスクを行わせます。
- ただし
  - `NUM_THREAD`回分が並列に問い合わせられます。
    - レート制限に応じて適宜調節してください。（Usage Tierが1であれば、`NUM_THREAD = 10`に設定することをお勧めします。）
  - `prompts`に入っているテキストファイルそれぞれを、システムプロンプトの中身だとみなし、それぞれ別々に実行します。
    - 実験に使用されたくないシステムプロンプトについては、そのファイルの名前を`_`から始まるようにしておくと無視されます。

[*2]
- abc2midiに入力する際には、以下の処理を行う。
  - 簡単に言えば、GPT-4からの出力に誤りがあったとしても、修正を簡単に行えるものについては自動的に修正する。
1. ヘッダ行に存在しない`maj, min`の記述は全て空文字列``, `m`に置き替える。
   - これは、abc2midiが`maj, min`のコード記述に対応していない一方で、GPT-4はこの記述法に則って楽譜を生成することがあるため。
   - (なお、同じ機能を持つライブラリである[abcjs]はこの記法に対応している。)
2.  出力に連続した改行`\n`があった場合にはすべて一回の改行に置き換える。
    - GPT-4は、楽譜ヘッダ部と音列を記述する部の間に1行以上空行を入れて記述することがある。
    - 仮にGPT-4が楽曲を生成していたとしても、この場所に1行以上空行が入っていると曲が一切記述されていないものとしてabc2midiに解釈されてしまうため。

# 実行情報

## 実行環境
- MacBook Pro (16-inch, 2023) Apple M2 Pro
  - OS: Sonoma 14.5
- Python 3.12.4

## 実行要件
1. 実行には、次のツールがローカルマシンに導入されている必要があります。
- [fluidsynth ver 2.3.4](https://www.fluidsynth.org)
- [abc2midi ver 4.93](https://abcmidi.sourceforge.io)

```zsh
❯ fluidsynth --version
FluidSynth runtime version 2.3.4
Copyright (C) 2000-2023 Peter Hanappe and others.
Distributed under the LGPL license.
SoundFont(R) is a registered trademark of Creative Technology Ltd.

FluidSynth executable version 2.3.4
Sample type=double

❯ abc2midi --Version
abc2midi version 4.93 June 06 2024 abc2midi
```

2. 次のpipパッケージの導入が必要です。
- [openai 1.34.0](https://pypi.org/project/openai/)
  - c.f. [Python library -- OpenAI](https://platform.openai.com/docs/libraries/python-library)

3. 次の場所に何かしらのサウンドフォント`.sf2`を導入しておく必要があります。
- `sf2/GeneralUser_GS_1.471/GeneralUser_GS_v1.471.sf2`
  - 今回の実験の際に、MIDIデータのレンダリングに用いたのは[GeneralUser GS 1.471](https://schristiancollins.com/generaluser.php)です。

4. 次の場所にOpen AI keyを記述したファイルを保存する必要があります。
- `OPEN_AI_KEY.txt`
  - このファイルにAPI Keyを格納して保存してください。（改行なしで）
  - なお、`./src/experiment`のget_client()関数を下のように改造すれば、環境引数`OPEN_AI_KEY`を受け取ってシステムが動作するように変更することもできます。
    - c.f. https://github.com/openai/openai-python
```py
def get_client():
    return OpenAI()
```