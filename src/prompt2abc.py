import re
from typing import Tuple
from fractions import Fraction
from Result import Result, ProcessState, ResultOK

#TODO test this function
def extract_abc_score(response:str) -> tuple[Result, str]:
    """
    入力`response`から最後にコードブロックに記述されたABC形式の楽譜を抜き出す。
    ただし、抜き出すことに失敗した場合には、全文を返す。
    また、ABC記譜法に2行以上の連続した改行があった際には、1行の改行に置換する。

    # returns
    ABC記譜法の楽譜`x`が抜き出せたとき: `(ResultOK(), x)`
    ABC記譜法の楽譜が抜き出せなかったとき: `(Result(ProcessState.FAILED_EXTRACT_AUDIO, "There is no abc score in output."), response)`
    """
    pattern = r'```[^\n]*\n([^`]+?)```'
    extracted_scores = re.findall(pattern, response)
    if len(extracted_scores) == 0: return (Result(ProcessState.FAILED_EXTRACT_AUDIO, "There is no abc score in output."), response)
    
    abc_score = postprocess(extracted_scores[-1])
    return (ResultOK(), abc_score)

def postprocess(extracted_score:str):
    result_score = shrink_empty_lines(extracted_score)
    lines = []
    for (line, is_header) in add_header_info(result_score):
        # ABC記譜法の対応していない、メジャーコード、マイナーコードの記法を出力してしまうことがあるため
        if is_header:
            line = re.sub("maj", "", line)
            line = re.sub("min", "m", line)
            lines.append(line)
        else:
            lines.append(line)
    return "\n".join(lines)

def shrink_empty_lines(abc_score:str):
    """
    ある空行でない2行の間に空行があった場合、それを縮小し一つの改行文字に置換する。
    """
    return re.sub(r"\n\s*\n", "\n", abc_score)

def add_header_info(abc_score:str):
    """
    abc記譜法の各行に対して、その行が音列が書かれた行かを記録する
    戻り値: i行目について、(i行目の中身, `is_header`)
        ただし、`is_header`は、i行目がヘッダ行であるときに限りTrueであるような値である。
    """
    header_start_pattern = re.compile(r"^[A-Za-z]\s*:")
    return [(line, header_start_pattern.match(line) == None) for line in abc_score.splitlines()]

def read_rythm_info(abc_score:str):
    """
    ヘッダ行にあるリズム情報を読み取る
    """
    meter = Fraction(4, 4)
    unit_note_length = Fraction(1, 8)
    meter_pattern = re.compile(r"M:")
    unit_note_length_pattern = re.compile(r"L:")
    for (line, is_header) in add_header_info(abc_score):
        if is_header:
            if meter_pattern.match(line):               meter = Fraction(line.split(":")[1])
            if unit_note_length_pattern.match(line):    unit_note_length = Fraction(line.split(":")[1])
    return (meter, unit_note_length)



def test():
    assert extract_abc_score("""
this is the test message
```abc
super string 
```
And final result.
```abc
another super abc string
```
    """) == (True, 'another super _ac string')
    assert extract_abc_score("\nThere is no abc code block.\n") == (False, '\nThere is no abc code block.\n')

    score_example = """
X:1
T:Sunny, Shiny, Fore#st
M:4/4
Q:1/4 = 180
L:1/8
K:D
|: "Dmaj7" D^FAF "A7" A#C#EA | "Gmaj7" GBbd#B "F#m7" AFCE | "Em7" EGBE "Bm7" DFAD | "E7" ^GBDG "A7" AECA :|
    """
    score_expected = """
X:1
T:Sunny, Shiny, Fore#st
M:4/4
Q:1/4 = 180
L:1/8
K:D
|: "D7" D^FAF "A7" ^A^CEA | "G7" G_B^dB "F#m7" AFCE | "Em7" EGBE "Bm7" DFAD | "E7" ^GBDG "A7" AECA :|
    """
    print(read_rythm_info(score_expected))
    assert postprocess(score_example).strip() == score_expected.strip()

if __name__ == "__main__":
    test()