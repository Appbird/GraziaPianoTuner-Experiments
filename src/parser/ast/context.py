from dataclasses import dataclass
from fractions import Fraction
from parser.key import ParsedKey, parse_k_field


def bpm_from_Q(q_field: str) -> int:
    """
    Q フィールド例: '1/4=120' または '1/4=120 1/8=...' などの最初部分だけ使う。
    """
    first = q_field.split()[0]
    frac, bpm = first.split('=')
    return int(bpm)

def parse_time_sig(m_field: str):
    # '4/4' 等
    num, den = m_field.split('/')
    return Fraction(int(num), int(den))

def parse_L(l_field: str) -> Fraction:
    """
    L: 基本長を四分音符=1 beat 系に換算。
    L = a/b → 長さ(beat) = 4 * (a/b)
    例: 1/8 → 0.5 beat, 1/4 → 1.0 beat
    """
    a, b = l_field.split('/')
    return 4 * Fraction(int(a), int(b))


@dataclass
class Context:
    BPM:int
    L:Fraction
    M:Fraction
    Key:ParsedKey
    def set(self, field_name:str, value:str):
        if field_name == "Q":
            self.BPM = bpm_from_Q(value)
        elif field_name == "L":
            self.L = parse_L(value)
        elif field_name == "M":
            self.M = parse_time_sig(value)
        elif field_name == "Key":
            self.Key = parse_k_field(value)
            
