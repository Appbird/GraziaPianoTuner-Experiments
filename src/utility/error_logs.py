from os import makedirs
from pathlib import Path

from utility.Result import Result


def write_error_log(result_dir:Path, thread_results:list[Result]) -> tuple[int, int]:
    """
    指定したパス`path`に、`thread_results`に記述されている結果の系列をもとにエラーログを書き起こす。
    # returns
    (一切警告が出なかった曲の数`perfect`, コンパイルに成功した曲の数`success`)
    """
    makedirs(result_dir, exist_ok=True)
    success_cases_count = 0
    perfect_cases_count = 0
    with open(result_dir/"error.log", mode='w') as f:
        for (trial_no, result) in enumerate(thread_results):
            if (result.is_ok()):
                success_cases_count += 1
            if (len(result.reason) == 0):
                perfect_cases_count += 1
                continue
            f.write(f"[{trial_no + 1}: {result.state.name}] {result.reason}\n")
            f.write(f"\n")
        f.write("\n")
        f.write(f"[INFO] perfect {perfect_cases_count}, success {success_cases_count} / {len(thread_results)}")
    return perfect_cases_count, success_cases_count