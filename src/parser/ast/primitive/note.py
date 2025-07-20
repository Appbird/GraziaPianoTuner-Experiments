# note.py
from dataclasses import dataclass
from fractions import Fraction
from typing import Optional
from parser.ast.context import Context
from parser.ast.measure_info import MeasureInfo, NoteEvent
from parser.ast.primitive.duration import Duration
from parser.ast.primitive.primitive import MusicalAtom

def default_str(a:Optional[str]):
    return a if a != None else ""

# --- Musical objects ---
@dataclass
class Note(MusicalAtom):
    acc: Optional[str]
    pitch: str
    octave_marks: Optional[str]
    midi: int
    duration: Duration
    def eval(self, context:Context, mlist:list[MeasureInfo]):
        latest = mlist[-1]
        previous_beat= latest.notes[-1].end_beat if len(latest.notes) > 0 else Fraction(0)
        actual_duration = self.duration.f if self.duration != None else Fraction(1)
        actual_duration *= context.L
        note = NoteEvent(
            previous_beat,
            previous_beat + actual_duration,
            self.midi,
            actual_duration,
            len(latest.notes),
            raw_pitch=default_str(self.acc) + self.pitch + default_str(self.octave_marks)
        )
        latest.notes.append(note)
    def stretch(self, a: Fraction):
        self.duration.f *= a
    def dur(self):
        return self.duration.f
    def set_dur(self, a:Fraction):
        self.duration.f = a

@dataclass
class Rest(MusicalAtom):
    duration: Duration
    def eval(self, context:Context, mlist:list[MeasureInfo]):
        latest = mlist[-1]
        previous_beat= latest.notes[-1].end_beat if len(latest.notes) > 0 else Fraction(0)
        actual_duration = self.duration.f if self.duration != None else Fraction(1)
        actual_duration *= context.L
        note = NoteEvent(
            previous_beat,
            previous_beat + actual_duration,
            -1,
            actual_duration,
            len(latest.notes),
            raw_pitch="z"
        )
        latest.notes.append(note)
    def stretch(self, a: Fraction):
        self.duration.f *= a
    def dur(self):
        return self.duration.f
    def set_dur(self, a:Fraction):
        self.duration.f = a
