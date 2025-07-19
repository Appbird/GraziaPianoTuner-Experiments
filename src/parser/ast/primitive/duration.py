# duration.py
from dataclasses import dataclass
from fractions import Fraction

from parser.ast.context import Context
from parser.ast.measure_info import MeasureInfo

@dataclass
class Duration:
    f: Fraction
    def eval(self, context:Context, mlist:list[MeasureInfo]):
        raise NotImplementedError()
