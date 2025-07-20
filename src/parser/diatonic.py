from pychord import Chord

NOTE_TO_PC = {
    'C':0,'C#':1,'Db':1,'D':2,'D#':3,'Eb':3,'E':4,'Fb':4,'E#':5,'F':5,'F#':6,'Gb':6,
    'G':7,'G#':8,'Ab':8,'A':9,'A#':10,'Bb':10,'B':11,'Cb':11,'B#':0
}

def major_diatonic_sets():
    triads = [
        {0,4,7},      # I
        {2,5,9},  # ii
        {4,7,11},     # iii
        {0,5,9},      # IV
        {2,7,11},     # V
        {0,4,9},      # vi
        {2,5,11},     # vii°
    ]
    sevenths = [
        {0,4,7,11},   # IΔ7
        {0,2,5,9},    # ii7
        {2,4,7,11},   # iii7
        {0,4,5,9},    # IVΔ7
        {2,5,7,11},   # V7
        {0,4,7,9},    # vi7
        {2,5,9,11},   # viiø7
    ]
    return triads + sevenths

def minor_diatonic_sets(include_harmonic=True):
    # natural minor core triads
    triads = [
        {0,3,7},    # i
        {2,5,8},    # ii°
        {3,7,10},   # ♭III
        {0,5,8},    # iv
        {2,7,10},   # v
        {0,3,8},    # ♭VI
        {2,5,10},   # ♭VII
    ]
    sevenths = [
        {0,3,7,10},   # i7
        {0,2,5,8},    # iiø7
        {2,3,7,10},   # ♭IIIΔ7
        {0,3,5,8},    # iv7
        {2,5,7,10},   # v7
        {0,3,7,8},    # ♭VIΔ7
        {2,5,8,10},   # ♭VII7
    ]
    if include_harmonic:
        # Add harmonic minor alterations
        triads += [
            {2,7,11},   # V
            {2,5,11},   # vii°
        ]
        sevenths += [
            {2,5,7,11},   # V7
            {2,5,8,11},   # vii°7 (fully dim)
        ]
    # remove duplicates
    seen = set()
    out = []
    for s in triads + sevenths:
        key = tuple(sorted(s))
        if key not in seen:
            seen.add(key)
            out.append(s)
    return out

def key_tonic_pc(key_name: str) -> int:
    """
    key_name 例: 'C', 'G', 'F#', 'Bb', 'A'
    (モードは別引数で受ける想定)
    """
    return NOTE_TO_PC[key_name]

def chord_pcs_relative_to_key(chord: str, tonic_pc: int) -> set[int]:
    abs_pcs = Chord(chord).components(False)  # e.g. [0,4,7] for C
    return { (int(pc) - tonic_pc) % 12 for pc in abs_pcs }

def is_diatonic_chord(chord: str, key_root: str, mode: str, use_harmonic_in_minor=True) -> bool:
    """
    mode: 'major' | 'minor'
    """
    tonic_pc = key_tonic_pc(key_root)
    rel = chord_pcs_relative_to_key(chord, tonic_pc)

    # 3〜4和音のみ対象
    if len(rel) not in {3, 4}:
        return False

    if mode == 'major':
        allowed = major_diatonic_sets()
    elif mode == 'minor':
        allowed = minor_diatonic_sets(include_harmonic=use_harmonic_in_minor)
    else:
        raise ValueError("mode must be 'major' or 'minor'.")
    return rel in allowed

# --- 使用例 ---
if __name__ == "__main__":
    print(is_diatonic_chord("Dm", "C", "major"))   # True (ii)
    print(is_diatonic_chord("G7", "C", "major"))   # True (V7)
    print(is_diatonic_chord("E7", "A", "minor"))   # True (V7 in A minor, harmonic)
    print(is_diatonic_chord("E7", "A", "minor", use_harmonic_in_minor=False))  # False (natural minorのみ)
    print(is_diatonic_chord("F#m7b5", "G", "major"))  # True? G major の viiø7 → F#ø7 = {2,5,8,11} 相対 {2,5,8,11}
