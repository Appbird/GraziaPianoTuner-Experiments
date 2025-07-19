from abc import ABC, abstractmethod

from parser.ast.context import Context
from parser.ast.measure_info import MeasureInfo



class MeasurePrimitive(ABC):
    @abstractmethod
    def eval(self, context:Context, mlist:list[MeasureInfo]):
        raise NotImplementedError()

