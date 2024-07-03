
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
NUM_TRIALS = 5
SLEEP_SEC = 10

## 概念パラメータの入力について
from conceptual_parameters.set_additional_test import *

## 制約
assert all([len(adj) == len(param) for adj, param in zip(ADJ_LIST, PARAM_LIST)])
all_pattern_count = len(ADJ_LIST) * len(PARAM_LIST) * NUM_TRIALS

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

    thread_results:list[Result] = [ResultOK() for _ in range(all_pattern_count)]
    
    trial_no = 0
    dt_now_title = datetime.now().strftime("%Y%m%d_%H%M%S")
    dst_timestamp_folder = Path.cwd()/"result-adj"/(dt_now_title)
    # いくつかのwaveに分けて問い合わせを分散する。
    for adj in ADJ_LIST:
        threads:list[Thread] = []
        dst_adj_name = "-".join(adj)
        print(f"[INFO] starts wave {adj}.")
        
        for (param, trial) in itertools.product(PARAM_LIST, range(NUM_TRIALS)):
            
            dst = dst_timestamp_folder/dst_adj_name/f"trial{trial}-{str(param)}.ans"
            thread_results[trial_no].give_casename(f"{adj} at {str(param)} - {trial}")

            makedirs(dst.parent, exist_ok=True)
            # いくつものスレッドを立ち上げて、各スレッドごとにGPT-4に問い合わせる。
            thread = Thread(
                target=generate_music,
                args=(
                    client, dst,
                    thread_results, trial_no,
                    sys_prompt, gen_user_prompt(adj, param)
                )
            )
            thread.start()
            threads.append(thread)
            trial_no += 1

        # 各スレッドが終了するまで待つ    
        for thread in threads:
            thread.join()
        
        print(f"[INFO] finish wave {adj}.")

        # APIを叩きすぎるとレート制限に引っかかるため、適宜休憩を入れる。
        sleep(SLEEP_SEC)

    # エラーのログを出力させる。
    perfect_cases_count, success_cases_count = write_error_log(dst_timestamp_folder, thread_results)
    print(f"perfect {perfect_cases_count}, success {success_cases_count} / {all_pattern_count}")

if __name__ == "__main__":
    do_experiment()