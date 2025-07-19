from pathlib import Path
from music21 import converter, tempo, key, chord, note, stream

# ---------- Utils ----------
import math
from collections import Counter

def shannon_entropy(counts, base=2):
    total = sum(counts.values())
    if total == 0 or len(counts) <= 1:
        return 0.0, 0.0
    probs = [c/total for c in counts.values()]
    H = -sum(p*math.log(p, base) for p in probs if p > 0)
    H_norm = H / math.log(len(counts), base)
    return H, H_norm

def quantize_value(x, vocab):
    return min(vocab, key=lambda v: abs(v - x))

# ---------- 0. Load ----------
def load_abc(abc_source:str):
    """
    abc_source: path or raw ABC string
    """
    return converter.parse(abc_source)  # parse decides format automatically

# ---------- 1. BPM ----------
def extract_bpm(score):
    mm_list = []
    for mm in score.recurse().getElementsByClass(tempo.MetronomeMark):
        # quarterLength referent default is quarter note
        if mm.number:
            mm_list.append((mm.offset, mm.number))
    if not mm_list:
        return None
    # 時間加重平均 (区間長 = 次マーク offset - 現 offset)
    mm_list.sort()
    weights = []
    values = []
    for i,(off,num) in enumerate(mm_list):
        if i < len(mm_list)-1:
            dur = mm_list[i+1][0] - off
        else:
            dur = score.highestTime - off
        if dur <= 0: dur = 1e-6
        weights.append(dur)
        values.append(num)
    wsum = sum(weights)
    bpm_weighted = sum(v*w for v,w in zip(values,weights)) / wsum
    return bpm_weighted

# ---------- 2. Key / Mode ratio ----------
def measure_mode_ratio(score, use_declared=True):
    major = 0
    minor = 0
    measures = list(score.parts[0].getElementsByClass(stream.Measure)) if score.parts else list(score.getElementsByClass(stream.Measure))
    for m in measures:
        if use_declared and m.keySignature:
            k = m.analyze('key')  # or derive from keySignature directly
        else:
            k = m.analyze('key')
        if k.mode == 'major':
            major += 1
        elif k.mode == 'minor':
            minor += 1
    total = major + minor
    return {'major_ratio': major/total if total else None}

# ---------- 3. Harmony traits ----------
def harmony_profile(score, key_map=None):
    # chordify
    cscore = score.chordify()
    triad = tetrad = nondiat = 0
    total = 0
    for ch in cscore.recurse().getElementsByClass(chord.Chord):
        pcs = set(ch.pitchClasses)
        if len(pcs) < 2:  # skip single notes
            continue
        total += 1
        if len(pcs) == 3:
            triad += 1
        elif len(pcs) == 4:
            tetrad += 1
        # key context
        local_key = None
        if key_map:
            local_key = key_map(ch.offset)
        else:
            # fallback: global analyze
            local_key = score.analyze('key')
        scale_pcs = set(local_key.pitchClasses) if local_key else set()
        if not pcs.issubset(scale_pcs):
            nondiat += 1
    if total == 0:
        return {}
    return {
        'triad_ratio': triad/total,
        'tetrad_ratio': tetrad/total,
        'nondiat_ratio': nondiat/total
    }

# ---------- 4. Pitch stats ----------
def pitch_profile(score):
    pitches = [n.pitch.midi for n in score.recurse().notes if isinstance(n, note.Note)]
    if not pitches:
        return {}
    pmin, pmax = min(pitches), max(pitches)
    avg = sum(pitches)/len(pitches)
    # pitch-class entropy
    pc_counts = Counter([p % 12 for p in pitches])
    _, pc_H_norm = shannon_entropy(pc_counts)
    return {
        'pitch_range': pmax - pmin,
        'pitch_average': avg,
        'pitch_entropy_norm': pc_H_norm
    }

# ---------- 5. Interval entropy ----------
def interval_entropy(score, monophonic_part=None):
    # pick part
    part = monophonic_part if monophonic_part else (score.parts[0] if score.parts else score)
    notes = [n for n in part.recurse().notes if isinstance(n, note.Note)]
    if len(notes) < 2:
        return {'interval_entropy_norm': 0.0}
    steps = []
    prev_offset_group = None
    group_notes = []
    for n in notes:
        # group simultaneous notes (same offset) -> pick top pitch
        if prev_offset_group is None or n.offset == prev_offset_group:
            group_notes.append(n)
            prev_offset_group = n.offset
            continue
        # finalize previous group
        top_prev = max(group_notes, key=lambda x: x.pitch.midi)
        # start new group with current note
        group_notes = [n]
        prev_offset_group = n.offset
        # We will fill steps after we have next group top note
    # second pass simpler:
    events = []
    current_offset = None
    bucket = []
    for n in notes:
        if current_offset is None or n.offset == current_offset:
            bucket.append(n)
            current_offset = n.offset
        else:
            events.append(max(bucket, key=lambda x: x.pitch.midi))
            bucket = [n]
            current_offset = n.offset
    if bucket:
        events.append(max(bucket, key=lambda x: x.pitch.midi))
    for a,b in zip(events, events[1:]):
        diff = b.pitch.midi - a.pitch.midi
        diff = max(-12, min(12, diff))
        steps.append(diff)
    cnt = Counter(steps)
    _, Hnorm = shannon_entropy(cnt)
    return {'interval_entropy_norm': Hnorm}

# ---------- 6. IOI features ----------
def rhythm_profile(score, ioi_vocab=None):
    c = score.chordify()
    chords = [ch for ch in c.recurse().getElementsByClass(chord.Chord)]
    onsets = sorted({ch.offset for ch in chords})
    if len(onsets) < 2:
        return {'ioi_average': None, 'ioi_entropy_norm': 0.0}
    iois = [b - a for a,b in zip(onsets, onsets[1:])]
    avg = sum(iois)/len(iois)
    if ioi_vocab is None:
        ioi_vocab = [0.25, 1/3, 0.5, 0.75, 1.0, 1.5, 2.0, 4.0]
    quantized = [quantize_value(x, ioi_vocab) for x in iois]
    cnt = Counter(quantized)
    _, Hnorm = shannon_entropy(cnt)
    return {'ioi_average': avg, 'ioi_entropy_norm': Hnorm}

# ---------- 7. Master ----------
def extract_all(abc_source:str):
    s = load_abc(abc_source)
    feats = {}
    feats.update({'bpm': extract_bpm(s)})
    feats.update(measure_mode_ratio(s))
    feats.update(harmony_profile(s))
    feats.update(pitch_profile(s))
    feats.update(interval_entropy(s))
    feats.update(rhythm_profile(s))
    return feats
