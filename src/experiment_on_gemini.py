from os import makedirs
from glob import glob
from typing import List, Tuple
from threading import Thread
from pathlib import Path

from time import sleep

from abc2audio import abc2wav
from answer2abc import extract_abc_score
from Result import Result, ResultOK

from gemini import set_gemini_API_Key, ask_gemini_pro

# パラメータ群
MODEL_NAME = 'gemini-1.5-pro-001'
NUM_TRIALS = 100
NUM_THREAD = 10
USER_PROMPT = "Please compose a rainy day music."

# test done
def load_prompts() -> List[Tuple[str, str]]:
    """
    ./promptsフォルダにあるプロンプトをリストにして返す。
    # returns
    `load_prompts()[i] = (x, y)`
    `i`番目にあったファイルの名前が`x`であり、その中身が`y`であった。
    ただし、`_`から始まるファイルは無視する。
    """
    result:List[Tuple[str, str]] = []
    # リストとしてpromptsフォルダの中にあるテキストファイルを全て列挙したい
    for filepath in glob("prompts/*"):
        if Path(filepath).stem.startswith("_"): continue
        with open(filepath) as f:
            result.append((Path(filepath).stem, f.read()))
    return result


def test():
    print(load_prompts())


def generate_music(exp_name:str, thread_results:list[Result], exp_no:int, system_prompt:str, user_prompt:str):
    def filename(ext:str):
        return Path.cwd()/Path(f"result/{MODEL_NAME}/{exp_name}/{exp_no+1}.{ext}")
    answer_file = filename("ans")
    abc_file    = filename("abc")
    midi_file   = filename("midi")
    wav_file    = filename("wav")

    # Gemini-1.5-proに問う
    answer = ask_gemini_pro(MODEL_NAME, system_prompt, user_prompt)
    makedirs(answer_file.parent, exist_ok=True)
    with open(answer_file, mode='w') as f:
        f.write(answer)
    
    # ABC形式をプロンプトから抽出する
    (result1, abc_score) = extract_abc_score(answer)
    # 抽出できた時に限り、wav形式へ変換する
    if not result1.is_ok():
        thread_results[exp_no] = result1
        return
    makedirs(abc_file.parent, exist_ok=True)
    makedirs(midi_file.parent, exist_ok=True)
    makedirs(wav_file.parent, exist_ok=True)
    with open(abc_file, mode='w') as f:
        f.write(abc_score)
    #FIXED fがclosedされる前に新しく書き込みを加えてたせいでアクセスできていなかった
    thread_results[exp_no] = abc2wav(str(abc_file), str(midi_file), str(wav_file))


def write_error_log(exp_name:str, thread_results:list[Result]):
    makedirs(Path.cwd()/f"result/{MODEL_NAME}/{exp_name}/", exist_ok=True)
    success_cases_count = 0
    perfect_cases_count = 0
    with open(Path.cwd()/Path(f"result/{MODEL_NAME}/{exp_name}/error.log"), mode='w') as f:
        for (trial_no, result) in enumerate(thread_results):
            if (result.is_ok()):
                success_cases_count += 1
            if (len(result.reason) == 0):
                perfect_cases_count += 1
                continue
            f.write(f"[{trial_no + 1}: {result.state.name}] {result.reason}\n")
            f.write(f"\n")
        f.write("\n")
        f.write(f"[INFO] perfect {perfect_cases_count}, success {success_cases_count} / {NUM_TRIALS}")
    return perfect_cases_count, success_cases_count

def do_experiment():
    client = set_gemini_API_Key()

    phase_count = 0
    for (exp_name, prompt) in load_prompts():
        print(f"[INFO] starts {exp_name}.")
        thread_results:list[Result] = [ResultOK()] * NUM_TRIALS

        assert NUM_TRIALS % NUM_THREAD == 0
        wave_count = NUM_TRIALS // NUM_THREAD
        # いくつかのwaveに分けて問い合わせを分散する。
        for wave in range(wave_count):
            print(f"[INFO] starts wave {wave + 1} / { wave_count } in {exp_name}.")
            threads:list[Thread] = []
            # いくつものスレッドを立ち上げて、各スレッドごとにGPT-4に問い合わせる。
            for thread_no in range(NUM_THREAD):
                trial_no = wave * NUM_THREAD + thread_no
                thread = Thread(
                    target=generate_music,
                    args=(exp_name, thread_results, trial_no, prompt, USER_PROMPT)
                )
                thread.start()
                threads.append(thread)

            # 各スレッドが終了するまで待つ    
            for thread in threads:
                thread.join()
            print(f"[INFO] finish wave {wave + 1} / {wave_count} in {exp_name}.")

            # APIを叩きすぎるとレート制限に引っかかるため、適宜休憩を入れる。
            sleep(35)
        # エラーのログを出力させる。
        perfect_cases_count, success_cases_count = write_error_log(exp_name, thread_results)
        phase_count += 1
        print(f"[INFO] end phase {phase_count}.")
        print(f"perfect {perfect_cases_count}, success {success_cases_count} / {NUM_TRIALS}")

if __name__ == "__main__":
    do_experiment()