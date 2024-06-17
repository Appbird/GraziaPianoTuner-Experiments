import sys
import re
from os import makedirs
from glob import glob
from typing import List, Tuple
from openai import OpenAI
from threading import Thread
from pathlib import Path
from abc2audio import abc2wav

# クライアントオブジェクトを作る。これを作らないとAPIへの問い合わせができない。
# ターミナルのカレントディレクトリから見て、`./src/credential/OPEN_AI_KEY.txt`に記述されているAPIキーを読み取って実行します。
def get_client():
    OPEN_AI_KEY = ""
    with open("src/credential/OPEN_AI_KEY.txt") as f:
        OPEN_AI_KEY = f.read()
    return OpenAI(api_key=OPEN_AI_KEY)


#TODO test this function
def extract_abc_score(response:str) -> Tuple[bool, str]:
    """
    入力`response`から最後にコードブロックに記述されたABC形式の楽譜を抜き出す。
    ただし、抜き出すことに失敗した場合には、全文を返す。
    
    # returns
    ABC記譜法の楽譜`x`が抜き出せたとき: `(True, x)`
    ABC記譜法の楽譜が抜き出せなかったとき: `(False, response)`
    """
    pattern = r'```abc\n([^`]+?)```'
    extracted_scores = re.findall(pattern, response)

    if len(extracted_scores) == 0: return (False, response)
    return (True, extracted_scores[-1])
    


# clientオブジェクトを使って、promptの内容でGPT-4に問い合わせます。
# 問い合わせた結果が返り値になります。
def ask(client:OpenAI, system_prompt:str, user_prompt:str, temperature:float) -> str:
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system",  "content": system_prompt},
            {"role": "user",    "content": user_prompt},
        ],
        temperature=temperature
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
    print(extract_abc_score("""
this is the test message
```abc
    super abc string 
```
And final result.
```abc
    another super abc string
```
    """))
    print(extract_abc_score("""
There is no abc code block.
    """))

def generate_music(client:OpenAI, experiment_name:str, system_prompt:str, user_prompt:str, tempareture:float):
    def filename(ext:str):
        return Path(f"./result/{ext}/{experiment_name}.{ext}")

    # GPT-4に問う
    answer = ask(client, system_prompt, user_prompt, tempareture)
    answer_file = filename("ans")
    makedirs(answer_file.parent, exist_ok=True)
    with open(answer_file, mode='w') as f:
        f.write(answer)
    
    # ABC形式をプロンプトから抽出する
    (succeeded, abc_score) = extract_abc_score(answer)
    abc_file = filename("abc")
    makedirs(abc_file.parent, exist_ok=True)
    
    # 抽出できた時に限り、wav形式へ変換する
    if (succeeded):
        with open(abc_file, mode='w') as f:
            f.write(abc_score)
        abc2wav(str(abc_file))
        


def do_experiment():
    client = get_client()

    assert len(sys.argv) == 2
    temperature = float(sys.argv[1])
    user_prompt = "8小節の楽曲を作って"
    num_threads = 20

    for (exp_name, prompt) in load_prompts():
        threads:list[Thread] = []
        # いくつものスレッドを立ち上げて、各スレッドごとにGPT-4に問い合わせる。
        for th in range(num_threads):
            thread = Thread(
                target=generate_music,
                args=(client, exp_name, prompt, user_prompt, temperature)
            )
            thread.start()
            threads.append(thread)
        
        # 各スレッドが終了するまで待つ    
        for thread in threads:
            thread.join()
    

if __name__ == "__main__":
    test()