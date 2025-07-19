from dataclasses import dataclass
from typing import Optional

from parser.ast.context import Context
from parser.ast.measure_info import MeasureInfo


@dataclass
class HeaderLine:
    field: str
    value: Optional[str]
    def eval(self, context:Context, mlist:list[MeasureInfo]):
        if self.value:
            context.set(self.field, self.value)