from fractions import Fraction
from collections import Counter
import math

from parser.ast.measure_info import MeasureInfo

# ==== Dataclasses (上で示したもの) ====
# (ここに dataclass 群を置く)

# ==== Utility ====

def shannon_entropy_counts(counter: Counter) -> float:
    total = sum(counter.values())
    if total <= 1:
        return 0.0
    h = 0.0
    for c in counter.values():
        p = c / total
        h -= p * math.log2(p)
    return h

def measure_length_in_beats(m: MeasureInfo) -> Fraction:
    ts = m.time_sig
    return ts.numerator * Fraction(4, ts.denominator)

