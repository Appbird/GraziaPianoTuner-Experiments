from abc import ABC, abstractmethod
from fractions import Fraction

from parser.ast.context import Context
from parser.ast.measure_info import MeasureInfo



class MeasurePrimitive(ABC):
    @abstractmethod
    def eval(self, context:Context, mlist:list[MeasureInfo]):
        raise NotImplementedError()

class Adjustable(ABC):
    @abstractmethod
    def stretch(self, a:Fraction):
        raise NotImplementedError()
    def dur(self) -> Fraction:
        raise NotImplementedError()
    def set_dur(self, a:Fraction):
        raise NotImplementedError()

class MusicalAtom(MeasurePrimitive, Adjustable):
    pass