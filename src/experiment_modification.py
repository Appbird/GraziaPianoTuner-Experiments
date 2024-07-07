
import itertools
from os import makedirs
from openai import OpenAI
from threading import Thread
from pathlib import Path
from time import sleep
from datetime import datetime

from conversion.answer2audio import answer2audio
from llm_api import gpt4
from utility.Result import Result, ResultOK
from utility.error_logs import write_error_log
from utility.load_prompts import load_best_prompt

# パラメータ群
## APIへのリクエストについて
MODEL_NAME = "gpt-4o-2024-05-13"
TEMPARATURE = 1.0
NUM_TRIALS = 10
SLEEP_SEC = 60

## 概念パラメータの入力について
from conceptual_parameters.set_modification_test import *


def generate_music(
        client:OpenAI, result_dst_file:Path,
        thread_results:list[Result], exp_no:int,
        system_prompt:str, user_prompt:str
    ):
    response = gpt4.ask(client, MODEL_NAME, TEMPARATURE, system_prompt, user_prompt)
    with open(result_dst_file, mode="w") as f:
        f.write(response)
    result = answer2audio(result_dst_file)
    thread_results[exp_no].write_result(result)

def do_experiment():
    client = gpt4.get_client()
    sys_prompt = load_best_prompt()

    dt_now_title = datetime.now().strftime("%Y%m%d_%H%M%S")
    dst_timestamp_folder = Path.cwd()/"result-mod"/(dt_now_title)
    # いくつかのwaveに分けて問い合わせを分散する。
    for (case_name, modifying_prompt) in MODIFICATION_LIST:
        threads:list[Thread] = []
        print(f"[INFO] starts wave {case_name}.")
        thread_results:list[Result] = [ResultOK() for _ in range(NUM_TRIALS)]

        for trial in range(NUM_TRIALS):
            
            dst = dst_timestamp_folder/case_name/f"trial{trial}.ans"
            thread_results[trial].give_casename(f"{case_name} at - {trial}")
            makedirs(dst.parent, exist_ok=True)
            # いくつものスレッドを立ち上げて、各スレッドごとにGPT-4に問い合わせる。
            thread = Thread(
                target=generate_music,
                args=(
                    client, dst, thread_results, trial,
                    sys_prompt, gen_user_prompt(modifying_prompt)
                )
            )
            thread.start()
            threads.append(thread)    

        # 各スレッドが終了するまで待つ    
        for thread in threads:
            thread.join()
        
        print(f"[INFO] finish wave {case_name}.")

        # エラーのログを出力させる。
        perfect_cases_count, success_cases_count = write_error_log(dst_timestamp_folder/case_name, thread_results)
        print(f"perfect {perfect_cases_count}, success {success_cases_count} / {NUM_TRIALS}")
        
        # APIを叩きすぎるとレート制限に引っかかるため、適宜休憩を入れる。
        sleep(SLEEP_SEC)


if __name__ == "__main__":
    do_experiment()