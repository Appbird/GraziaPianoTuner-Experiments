import re
from typing import Tuple
from fractions import Fraction

#TODO test this function
def extract_abc_score(response:str) -> Tuple[bool, str]:
    """
    入力`response`から最後にコードブロックに記述されたABC形式の楽譜を抜き出す。
    ただし、抜き出すことに失敗した場合には、全文を返す。
    また、ABC記譜法に2行以上の連続した改行があった際には、1行の改行に置換する。

    # returns
    ABC記譜法の楽譜`x`が抜き出せたとき: `(True, x)`
    ABC記譜法の楽譜が抜き出せなかったとき: `(False, response)`
    """
    pattern = r'```abc\n([^`]+?)```'
    extracted_scores = re.findall(pattern, response)
    if len(extracted_scores) == 0: return (False, response)
    abc_score = postprocess(extracted_scores[-1])
    return (True, abc_score)

class SoundEvent:
    def __init__(self, pitch:str, length:Fraction):
        self.pitch = pitch
        self.length = length
class Measure:
    def __init__(self, sound_events:list[SoundEvent]):


def postprocess(extracted_score:str):
    result_score = shrink_empty_lines(extracted_score)
    lines = []
    for (line, is_header) in add_header_info(result_score):
        # ABC記譜法の対応していない、メジャーコード、マイナーコードの記法を出力してしまうことがあるため
        if is_header:
            line = re.sub("maj", "", line)
            line = re.sub("min", "m", line)
            line = modify_accents(line)
            lines.append(line)
        else:
            lines.append(line)
    return "\n".join(lines)

def measure_meters(abc_score_line:str):
    sound_pattern = (r"[a-gA-G][,']?([0-9]+/?[0-9]*)?")
    for (line, is_header) in add_header_info(abc_score_line):
        if (is_header): continue


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

def replace_on_sound_seq(piece:str):
    """
    ある臨時記号を持たない単音`X`に対して、`X#`, `Xb`を`^X`, `_X`に置換する。
    ただし、ABC記譜法において、1小節を含んだ
    """
    sound_pattern = r"([a-gA-G][,']?)"
    wrong_pattern_sharp = sound_pattern + r"#"
    wrong_pattern_flat = sound_pattern + r"b"
    
    piece = re.sub(wrong_pattern_sharp, "^\\1", piece)
    piece = re.sub(wrong_pattern_flat, "_\\1", piece)
    return piece

#TODO 音bが実際に楽曲として含まれていた含まれていた場合、置換するのは不適当である。
def modify_accents(abc_score:str):
    """
    渡されたABC記譜法の楽譜に対して、"で囲まれた部分（コード表記）を除き、`X#`, `Xb`を`^X`, `_X`に置換する。
    GPT-4の出力したABC記譜法において、臨時記号の誤りを訂正するため。
    """
    proceeded_pieces = [
        replace_on_sound_seq(piece) if ind % 2 == 0 else piece
        for (ind, piece) in enumerate(abc_score.split('\"'))
    ]
    return "\"".join(proceeded_pieces)


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

    assert replace_on_sound_seq("A#CbEA") == "^A_CEA"

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