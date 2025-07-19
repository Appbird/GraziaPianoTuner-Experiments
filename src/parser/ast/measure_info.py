
from dataclasses import dataclass
from fractions import Fraction
from typing import List, Optional

from parser.key import ParsedKey


@dataclass
class NoteEvent:
    start_beat: Fraction
    end_beat: Fraction
    midi: int
    length_beats: Fraction
    order: int
    raw_pitch: str

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

@dataclass
class MeasureInfo:
    index: int
    time_sig: Fraction
    key: ParsedKey
    bpm: int
    notes: List[NoteEvent] = []
    chords: List[ChordEvent] = []