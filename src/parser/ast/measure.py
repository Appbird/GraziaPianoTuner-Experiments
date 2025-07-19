
from parser.ast.context import Context
from parser.ast.measure_info import MeasureInfo
from parser.ast.primitive.primitive import MeasurePrimitive


class Measure:
    elems:list[MeasurePrimitive]
    def eval(self, context:Context, mlist:list[MeasureInfo]):
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