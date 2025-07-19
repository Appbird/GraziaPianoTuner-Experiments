from dataclasses import dataclass
from typing import List, Optional
from parser.ast.context import Context
from parser.ast.header import HeaderLine
from parser.ast.measure import Measure
from parser.ast.measure_info import MeasureInfo



@dataclass
class Line:
    header: Optional[HeaderLine] = None
    measures: Optional[List[Measure]] = None
    def eval(self, context:Context, mlist:list[MeasureInfo]):
        if self.header:
            self.header.eval(context, mlist)
        if self.measures:
            for measure in self.measures:
                measure.eval(context, mlist)

@dataclass
class Score:
    lines: List[Line]
    def eval(self, context:Context, mlist:list[MeasureInfo]):
        for line in self.lines:
            line.eval(context, mlist)