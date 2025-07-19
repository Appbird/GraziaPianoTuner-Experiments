import re

ACC_PATTERN = re.compile(r'(\^{1,2}|_{1,2}|=)')
PC = {'C':0,'D':2,'E':4,'F':5,'G':7,'A':9,'B':11}

def _accidental_offset(acc_text: str | None) -> int:
    if not acc_text:
        return 0
    off = 0
    for sym in ACC_PATTERN.findall(acc_text):
        if sym == '^': off += 1
        elif sym == '^^': off += 2
        elif sym == '_': off -= 1
        elif sym == '__': off -= 2
        elif sym == '=':  off += 0
    return off

def _octave_marks_offset(mark_text: str | None) -> int:
    if not mark_text:
        return 0
    return 12 * (mark_text.count("'") - mark_text.count(","))

def compute_midi(acc:str|None, pitch_letter:str, octave_marks:str|None):
    base = 60  # C4
    # pitch letter base
    pc = PC[pitch_letter.upper()]
    # difference inside its “letter octave”
    # For uppercase letters: stay in 4th octave; for lowercase add +12
    base_shift = 12 if pitch_letter.islower() else 0
    acc_off = _accidental_offset(acc)
    oct_off = _octave_marks_offset(octave_marks)
    return base + pc + base_shift + acc_off + oct_off
