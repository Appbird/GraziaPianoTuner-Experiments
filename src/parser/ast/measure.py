
from dataclasses import dataclass
from fractions import Fraction
from parser.ast.context import Context
from parser.ast.measure_info import MeasureInfo
from parser.ast.primitive.primitive import MeasurePrimitive, MusicalAtom

@dataclass
class Measure:
    elems:list[MeasurePrimitive]
    def eval(self, context:Context, mlist:list[MeasureInfo]):
        assert context.Key
        mlist.append(
            MeasureInfo(
                len(mlist),
                context.M,
                context.Key,
                context.BPM
            )
        )
        for elem in self.elems:
            elem.eval(context, mlist)

# TODO: brokenrhythm
    # eval時にlengthに補正をかけることができればOK
    # フィールドにパラメータを持たせて、あとで反映させよう
@dataclass
class BrokenPair(MeasurePrimitive):
    left:MusicalAtom
    right:MusicalAtom
    level:int
    forward:bool
    def eval(self, context:Context, mlist:list[MeasureInfo]):
        level = self.level
        while level > 0:
            self.left.stretch(Fraction(3, 2))
            self.right.stretch(Fraction(1, 2))
            level -= 1
        self.left.eval(context, mlist)
        self.right.eval(context, mlist)


@dataclass
class AtomList(MeasurePrimitive):
    seq:list[MusicalAtom]
    def eval(self, context:Context, mlist:list[MeasureInfo]):
        for elem in self.seq:
            elem.eval(context, mlist)

@dataclass
class Triplet(MeasurePrimitive):
    seq:list[MusicalAtom]
    def eval(self, context:Context, mlist:list[MeasureInfo]):
        total_duration = Fraction(0)
        for elem in self.seq: total_duration += elem.dur()
        for elem in self.seq: elem.set_dur(total_duration/3)
        for elem in self.seq: elem.eval(context, mlist)

@dataclass
class MeasureLine:
    seq:list[Measure]
    def eval(self, context:Context, mlist:list[MeasureInfo]):
        for elem in self.seq:
            elem.eval(context, mlist)