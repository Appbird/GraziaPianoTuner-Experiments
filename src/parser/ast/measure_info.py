
from dataclasses import dataclass, field
from fractions import Fraction
from typing import List, Optional

from parser.key import ParsedKey, dump_parsed_key


@dataclass
class NoteEvent:
    start_beat: Fraction
    end_beat: Fraction
    midi: int
    length_beats: Fraction
    order: int
    raw_pitch: str
    def dump(self, indent:int=0):
        print("\t"*indent, end=""); print(f"note={self.midi}, start-end=[{self.start_beat}, {self.end_beat})")

@dataclass
class ChordEvent:
    start_beat: Fraction
    end_beat: Fraction
    root:str
    raw_types:List[str]
    bass:Optional[str]
    is_diatonic:bool
    is_triad:bool
    tones: List[int]
    order: int
    def dump(self, indent:int=0):
        print("\t"*indent, end=""); print(f"Chord={self.root+("".join(self.raw_types))+"/"+str(self.bass)}, start-end={self.start_beat}-{self.end_beat}")
        print("\t"*(indent+1), end=""); print(f"is_diatonic={self.is_diatonic}, is_triad={self.is_triad}")

@dataclass
class MeasureInfo:
    index: int
    time_sig: Fraction
    key: ParsedKey
    bpm: int
    notes: List[NoteEvent] = field(default_factory=list)
    chords: List[ChordEvent] = field(default_factory=list)
    def dump(self):
        print(f"index={self.index} / time_sig={self.time_sig}")
        dump_parsed_key(self.key, 1)
        for note in self.notes: note.dump(1)
        for chord in self.chords: chord.dump(1)