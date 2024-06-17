import sys

from openai import OpenAI
from threading import Thread

# クライアントオブジェクトを作る。これを作らないとAPIへの問い合わせができない。
# ターミナルのカレントディレクトリから見て、`./src/credential/OPEN_AI_KEY.txt`に記述されているAPIキーを読み取って実行します。
def get_client():
    OPEN_AI_KEY = ""
    with open("src/credential/OPEN_AI_KEY.txt") as f:
        OPEN_AI_KEY = f.read()
    return OpenAI(api_key=OPEN_AI_KEY)

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