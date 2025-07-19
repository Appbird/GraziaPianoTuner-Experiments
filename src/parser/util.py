import re
from typing import Optional
from pychord import Chord


ACC_CHUNK_RE = re.compile(r'(\^{1,2}|_{1,2}|=)')   # For note accidentals
PC_MAP = {'C':0,'D':2,'E':4,'F':5,'G':7,'A':9,'B':11}

def accidental_offset(acc_text: Optional[str]) -> int:
    if not acc_text:
        return 0
    off = 0
    for sym in ACC_CHUNK_RE.findall(acc_text):
        if sym == '^':   off += 1
        elif sym == '^^': off += 2
        elif sym == '_':  off -= 1
        elif sym == '__': off -= 2
        elif sym == '=':  off += 0
    return off

def octave_marks_offset(mark_text: Optional[str]) -> int:
    if not mark_text:
        return 0
    return 12 * (mark_text.count("'") - mark_text.count(","))

def compute_midi(acc: Optional[str], pitch_letter: str, octave_marks: Optional[str]) -> int:
    base = 60  # C4
    pc = PC_MAP[pitch_letter.upper()]
    upper_shift = 12 if pitch_letter.islower() else 0
    acc_off = accidental_offset(acc)
    oct_off = octave_marks_offset(octave_marks)
    return base + pc + upper_shift + acc_off + oct_off

# Unicode accidental normalize for chords
ACC_NORMALIZE = {
    '♭': 'b',
    '♯': '#',
    '♮': '',  # natural -> remove
    "b": "b",
    "#": "#"
}

def normalize_accidental_symbol(sym: Optional[str]) -> str:
    if not sym:
        return ""
    return ACC_NORMALIZE.get(sym, sym)

# c.components() -> ['D', 'F#', 'A', 'C']# 必要なら MIDI へ:
def pitch_class_to_midi(pc: str, base_octave=4):
    # pc例 'F#'
    semis = {'C':0,'C#':1,'Db':1,'D':2,'D#':3,'Eb':3,'E':4,'F':5,'F#':6,'Gb':6,
             'G':7,'G#':8,'Ab':8,'A':9,'A#':10,'Bb':10,'B':11}
    return 12*(base_octave+1) + semis[pc]  # C4=60 ⇒ base_octave=4 なら 12*5=60

def chord_tones(c:Chord, base_octave=4):
    base_c = 12*(base_octave+1)
    return [base_c + int(p) for p in c.components(False)]
