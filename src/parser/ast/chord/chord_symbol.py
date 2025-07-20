from dataclasses import dataclass, field
from fractions import Fraction
from typing import List, Optional

from parser.ast.context import Context
from parser.ast.measure_info import ChordEvent, MeasureInfo
from parser.ast.primitive.primitive import MeasurePrimitive
from pychord import Chord

from parser.diatonic import is_diatonic_chord

# --- Chord Symbol ---
@dataclass
class ChordSymbol(MeasurePrimitive):
    root: str                 # e.g. 'C', 'F#', 'Bb'
    raw_types: List[str]      # ['maj7', '#11b13'] など (現段階そのまま)
    bass: Optional[str] = None  # 'E', 'G#', etc.
    alternates: List['ChordSymbol'] = field(default_factory=list)
    text: str = ""            # 原文再現
    def eval(self, context:Context, mlist:list[MeasureInfo]):
        latest = mlist[-1]
        end_beat = latest.notes[-1].end_beat if len(latest.notes) > 0 else Fraction(0)
        if len(latest.notes) > 0:
            latest.chords[-1].end_beat = end_beat
        
        chordname = self.root + "".join(self.raw_types)
        if self.bass: chordname += "/" + self.bass
        tones = Chord(chordname).components(False)

        assert context.Key and context.Key["tonic"]
        is_diatonic = is_diatonic_chord(chordname, context.Key["tonic"], context.Key["mode"], use_harmonic_in_minor=True)
        is_triad = len(tones) == 3

        chord = ChordEvent(
            end_beat,
            strict_ceil(end_beat),
            self.root,
            self.raw_types,
            self.bass,
            is_diatonic,
            is_triad,
            tones, #type: ignore
            len(latest.chords)
        )
        latest.chords.append(chord)

def strict_ceil(x: Fraction) -> Fraction:
    """
    値 x より厳密に大きい最小の整数を返す。
    （整数ちょうどなら +1, 端数があれば通常のceilと同じ。）
    """
    return Fraction(x.numerator // x.denominator) + 1