
import re
from typing import Tuple


ReplacedRange = Tuple[str, int, int]
class ReplacedRanges:
    def __init__(self):
        self.ranges:list[Tuple[str, int, int]] = []

    def append(self, replaced_range:ReplacedRange):
        self.ranges.append(replaced_range)

    def execute(self, target:str):
        result = ""
        completed_before = 0
        for (after, begin, end) in self.ranges:
            result += target[completed_before:begin]
            result += after
            completed_before = end
        


def replace_range(target:str, repl:str, begin:int, end:int):
    return target[:begin] + repl + target[end:]

def modify_score_in_accent(abc_score_soundseq:str):
    replaced_ranges = ReplacedRanges()
    current_pos = 0
    while current_pos < len(abc_score_soundseq):
        current_char = abc_score_soundseq[current_pos]
        if current_char == '|':
            (is_illegal, next_point) = measure_meters(abc_score_soundseq, current_pos)
            if (is_illegal): replaced_ranges.append(create_ranges(abc_score_soundseq, current_pos, next_point))
            current_pos = next_point
    return replaced_ranges.execute(abc_score_soundseq)

def create_ranges(abc_score_soundseq:str, current_pos:int, next_pos:int) -> ReplacedRange:
    return (modify_accents(abc_score_soundseq[current_pos:next_pos]), current_pos, next_pos)

#TODO ここを実装する。
#正しい音価を含んでいるか、`current_pos`から今の小節が終わるまで調べる。
def measure_meters(soundseq:str, current_pos:int) -> Tuple[bool, int]:
    for i in range(current_pos + 1, len(soundseq)):
        if soundseq[i]: 
            pass


def is_accent_sign(char:str):
    return char in {'_', '^'}


def replace_on_sound_seq(piece:str):
    """
    ある臨時記号を持たない単音`X`に対して、`X#`, `Xb`を`^X`, `_X`に置換する。
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
