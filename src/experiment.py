from os import makedirs
from glob import glob
from typing import List, Tuple
from openai import OpenAI
from threading import Thread
from pathlib import Path
from abc2audio import abc2wav
from prompt2abc import extract_abc_score

# パラメータ群
MODEL_NAME = "gpt-4o"
TEMPARATURE = 1.0
NUM_TRIALS = 3
USER_PROMPT = "compose something in 8 bars."

# クライアントオブジェクトを作る。これを作らないとAPIへの問い合わせができない。
# ターミナルのカレントディレクトリから見て、`./src/credential/OPEN_AI_KEY.txt`に記述されているAPIキーを読み取って実行します。
def get_client():
    OPEN_AI_KEY = ""
    with open("credential/OPEN_AI_KEY.txt") as f:
        OPEN_AI_KEY = f.read()
    return OpenAI(api_key=OPEN_AI_KEY)



# clientオブジェクトを使って、promptの内容でGPT-4に問い合わせます。
# 問い合わせた結果が返り値になります。
def ask(client:OpenAI, system_prompt:str, user_prompt:str) -> str:
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system",  "content": system_prompt},
            {"role": "user",    "content": user_prompt},
        ],
        temperature=TEMPARATURE
    )
    result = response.choices[0].message.content
    return result if result != None else ""

# test done
def load_prompts() -> List[Tuple[str, str]]:
    """
    ./promptsフォルダにあるプロンプトをリストにして返す。
    # returns
    `load_prompts()[i] = (x, y)`
    `i`番目にあったファイルの名前が`x`であり、その中身が`y`であった。
    """
    result:List[Tuple[str, str]] = []
    # リストとしてpromptsフォルダの中にあるテキストファイルを全て列挙したい
    for filepath in glob("prompts/*"):
        with open(filepath) as f:
            result.append((Path(filepath).stem, f.read()))
    return result


def test():
    print(load_prompts())

def generate_music(client:OpenAI, exp_name:str, exp_no:int, system_prompt:str, user_prompt:str):
    def filename(ext:str):
        return Path(f"./result/{MODEL_NAME}/{exp_name}/{exp_no+1}.{ext}")
    answer_file = filename("ans")
    abc_file    = filename("abc")
    midi_file   = filename("midi")
    wav_file    = filename("wav")

    # GPT-4に問う
    answer = ask(client, system_prompt, user_prompt)
    makedirs(answer_file.parent, exist_ok=True)
    with open(answer_file, mode='w') as f:
        f.write(answer)
    
    # ABC形式をプロンプトから抽出する
    (succeeded, abc_score) = extract_abc_score(answer)
    
    # 抽出できた時に限り、wav形式へ変換する
    if (succeeded):
        makedirs(abc_file.parent, exist_ok=True)
        makedirs(midi_file.parent, exist_ok=True)
        makedirs(wav_file.parent, exist_ok=True)
        with open(abc_file, mode='w') as f:
            f.write(abc_score)
        abc2wav(str(abc_file), str(midi_file), str(wav_file))
        

def do_experiment():
    client = get_client()

    phase_count = 0
    for (exp_name, prompt) in load_prompts():
        print(f"[INFO] starts {exp_name}.")
        print(prompt)
        threads:list[Thread] = []
        # いくつものスレッドを立ち上げて、各スレッドごとにGPT-4に問い合わせる。
        for trial_no in range(NUM_TRIALS):
            thread = Thread(
                target=generate_music,
                args=(client, exp_name, trial_no, prompt, USER_PROMPT)
            )
            thread.start()
            threads.append(thread)
        
        # 各スレッドが終了するまで待つ    
        for thread in threads:
            thread.join()
        phase_count += 1
        print(f"[INFO] end phase {phase_count}.")

if __name__ == "__main__":
    do_experiment()