from LLM.OpenAI import GPT, Model
from utility.feature_extractors import load_abc, extract_all
from utility.paths import prompt_path


def main():
    system_prompts = (prompt_path()/"without_refine_pattern.txt").read_text(encoding="utf-8")
    gpt = GPT(Model.gpt_4o_2024_08_06, system_prompts)
    print(extract_all("result/gpt-4o-mini-2024-07-18/without_refine_pattern/41.abc"))

    exit(0)
    axes = [
        '明るさ', '気まぐれな', '厳かな',
        '勇敢な', '堂々とした',
        '静かな', '沈んだ',
        "クラシック感", "ジャズ感", "スイング感",
    ]


    for axis in axes:
        for i in range(30):
            pass
            # gptに可変概念パラメータを入力し、作曲するように要請する。
            # gptにメッセージMを伝えたいときは
                # gpt.tell(M)
                # msg = gpt.ask(true) ---> リクエストを送信する
            # 一度作られた曲に対してさらに可変概念パラメータを変更させ、さらにその曲に基づいて楽曲を変更する。

            # それぞれの2曲の特徴量を求める。
                # 1. 長調なら+1、短調なら0（小節数で割合を取る）
                # 2. 三和音ダイアトニックコード / 四和音ダイアトニックコード / ノンダイアトニックコードの割合を調べる。
                # 3. BPM
                # 4. メロディの平均と分散(MIDIノーツ番号を基準に)
                # 5. リズムパターンについて、IOIの平均と分散を取る
                
                # その特徴量の変化度合いを調べ、それぞれの特徴量の変化前後を記録する。

        # パラメータの変化に対して、特徴量の変化の統計をとる。

if __name__ == "__main__":
    main()