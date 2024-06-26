# test done
from glob import glob
from pathlib import Path


def load_prompts() -> list[tuple[str, str]]:
    """
    ./promptsフォルダにあるプロンプトをリストにして返す。
    # returns
    `load_prompts()[i] = (x, y)`
    `i`番目にあったファイルの名前が`x`であり、その中身が`y`であった。
    ただし、`_`から始まるファイルは無視する。
    """
    result:list[tuple[str, str]] = []
    # リストとしてpromptsフォルダの中にあるテキストファイルを全て列挙したい
    for filepath in glob("prompts/*"):
        if Path(filepath).stem.startswith("_"): continue
        with open(filepath) as f:
            result.append((Path(filepath).stem, f.read()))
    return result

def load_best_prompt() -> str:
    """
    "without_refine_pattern"のプロンプトを読み込む。
    """
    filename = "prompts/without_refine_pattern.txt"
    # リストとしてpromptsフォルダの中にあるテキストファイルを全て列挙したい
    with open(filename) as f:
        return f.read()

if __name__ == "__main__":
    print(load_prompts())