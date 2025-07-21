#!python3.12
from os import makedirs
import sys
from .answer2abc import extract_abc_score
from .abc2audio import abc2wav
from pathlib import Path
from utility.ABC2AudioResult import ABC2AudioResult
from utility.paths import filename

def answer2audio(answer_file:Path) -> ABC2AudioResult:
    """
    `ans_path`に格納されている、GPT-4から返ってきたプロンプトの返答に
    含まれているabc記譜法の楽譜を抽出し、
    abc形式, midi形式, wav形式のファイルとしてexportする。
    # returns
    処理の結果を表す`Result`インスタンス。
    """
    abc_file    = filename(answer_file, "abc")
    midi_file   = filename(answer_file, "midi")
    wav_file    = filename(answer_file, "wav")
    
    makedirs(answer_file.parent, exist_ok=True)
    answer = ""
    with open(answer_file, mode='r') as f:
        answer = f.read()
    
    # ABC形式をプロンプトから抽出する
    (result1, abc_score) = extract_abc_score(answer)

    # 抽出できた時に限り、wav形式へ変換する
    if not result1.is_ok():
        return result1

    makedirs(abc_file.parent, exist_ok=True)
    makedirs(midi_file.parent, exist_ok=True)
    makedirs(wav_file.parent, exist_ok=True)
    with open(abc_file, mode='w') as f:
        f.write(abc_score)
    
    #FIXED fがclosedされる前に新しく書き込みを加えてたせいでアクセスできていなかった
    return abc2wav(str(abc_file), str(midi_file), str(wav_file))


if __name__ == "__main__":
    path = Path(sys.argv[1])
    print(answer2audio(path).encode())