import itertools
from openai import OpenAI
from threading import Thread
from pathlib import Path
from time import sleep

from conversion.answer2audio import answer2audio
from llm_api import gpt4
from utility.Result import Result, ResultOK
from utility.error_logs import write_error_log
from utility.load_prompts import load_best_prompt, load_prompts
from utility.paths import result_dir

# パラメータ群
MODEL_NAME = "gpt-4o-2024-05-13"
TEMPARATURE = 1.0
NUM_TRIALS = 3
def prompt(adj:str, value:float):
    assert 0 <= value <= 1
    return f"""
# parameters
{adj}: {value}
"""
adj_list    = {"明るさ", "躍動感"}
param_list  = {0, 0.5, 1.0}
all_pattern_count = len(adj_list) * len(param_list) * NUM_TRIALS

def generate_music(
        client:OpenAI, result_dst_file:Path,
        thread_results:list[Result], exp_no:int,
        system_prompt:str, user_prompt:str
    ):
    response = gpt4.ask(client, MODEL_NAME, TEMPARATURE, system_prompt, user_prompt)
    with open(result_dst_file) as f:
        f.write(response)
    thread_results[exp_no] = answer2audio(result_dst_file)

def do_experiment():
    client = gpt4.get_client()
    dst = Path.cwd()/"result-adj"

    phase_count = 0
    sys_prompt = load_best_prompt()
    print(f"[INFO] starts.")

    thread_results:list[Result] = [ResultOK()] * all_pattern_count
    
    # いくつかのwaveに分けて問い合わせを分散する。
    for adj in adj_list:
        
        trial_no = 0
        threads:list[Thread] = []

        for param in param_list:
            for trial in range(NUM_TRIALS):
                print(f"[INFO] starts wave {adj}.")
                
                dst = Path.cwd()/"result-adj"/adj/f"{str(param)}-{trial}.ans"
                
                # いくつものスレッドを立ち上げて、各スレッドごとにGPT-4に問い合わせる。
                thread = Thread(
                    target=generate_music,
                    args=(
                        client, dst,
                        thread_results, trial_no,
                        sys_prompt, prompt(adj, param)
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
    sleep(35)

    # エラーのログを出力させる。
    perfect_cases_count, success_cases_count = write_error_log(dst, thread_results)
    phase_count += 1
    print(f"[INFO] end phase {phase_count}.")
    print(f"perfect {perfect_cases_count}, success {success_cases_count} / {NUM_TRIALS}")

if __name__ == "__main__":
    do_experiment()