import sys
import re
from typing import Tuple

from openai import OpenAI
from threading import Thread

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
    pattern = r'```abc\n([^`]+?)\n```"'
    extracted_scores = re.findall(pattern, response)

    if len(extracted_scores) == 0: return (False, response)
    return (True, extracted_scores[-1])
    


# clientオブジェクトを使って、promptの内容でGPT-4に問い合わせます。
# 問い合わせた結果が返り値になります。
def ask(client:OpenAI, prompt:str, temperature:float) -> str:
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content": prompt},
        ],
        temperature=temperature
    )
    result = response.choices[0].message.content
    return result if result != None else ""


prompt = "Say a random number between 0 and 100."
client = get_client()

assert len(sys.argv) == 2
temperature = float(sys.argv[1])
num_threads = 5
num_rounds = 2

for i in range(num_rounds):
    threads:list[Thread] = []
    results = [""] * (num_threads)
	# いくつものスレッドを立ち上げて、各スレッドごとにGPT-4に問い合わせる。
    for j in range(num_threads):
    	# スレッドを作り、終了した時に問い合わせた結果をresult[j]に記述する。
        thread = Thread(target = lambda j=j: results.__setitem__(j, ask(client, prompt, temperature)))
        thread.start()
        threads.append(thread)
    
    # 各スレッドが終了するまで待つ    
    for thread in threads:
        thread.join()
    
    print(results)