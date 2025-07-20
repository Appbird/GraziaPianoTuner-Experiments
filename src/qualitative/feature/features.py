from typing import List, Tuple
from collections import Counter

from qualitative.feature.data import HarmonicFeatures, IOIFeatures, IntervalFeatures, PitchFeatures
from qualitative.feature.utility import shannon_entropy_counts
from parser.ast.measure_info import MeasureInfo, NoteEvent

def compute_harmonic_features(measures: List[MeasureInfo]) -> HarmonicFeatures:
    if not measures:
        return HarmonicFeatures(0,0,0,0,0,0,0,0)

    major = minor = 0
    bpms = []
    triad_diat = tetrad_diat = nondiat = 0
    chord_total = 0

    for m in measures:
        mode = m.key.get("mode")
        if mode == "major": major += 1
        elif mode == "minor": minor += 1
        bpms.append(m.bpm)
        for ch in m.chords:
            chord_total += 1
            if ch.is_diatonic:
                if ch.is_triad: triad_diat += 1
                else:           tetrad_diat += 1
            else:
                nondiat += 1

    n_measures = len(measures)
    major_ratio = major / n_measures
    minor_ratio = minor / n_measures
    bpm_mean = sum(bpms)/len(bpms) if bpms else 0.0

    if chord_total == 0:
        r_triad = r_tetrad = r_non = 0.0
    else:
        r_triad  = triad_diat  / chord_total
        r_tetrad = tetrad_diat / chord_total
        r_non    = nondiat     / chord_total

    return HarmonicFeatures(
        major_ratio=major_ratio,
        minor_ratio=minor_ratio,
        bpm_mean=bpm_mean,
        chord_ratio_triad_diatonic=r_triad,
        chord_ratio_tetrad_diatonic=r_tetrad,
        chord_ratio_nondiatonic=r_non,
        n_measures=n_measures,
        n_chords=chord_total
    )

def compute_pitch_features(ordered_notes: List[NoteEvent]) -> PitchFeatures:
    if not ordered_notes:
        return PitchFeatures(0,0,0,0)
    pitches = [n.midi for n in ordered_notes]
    pitch_range = max(pitches) - min(pitches)
    pitch_average = sum(pitches)/len(pitches)
    pitch_entropy = shannon_entropy_counts(Counter(pitches))
    return PitchFeatures(
        pitch_range=pitch_range,
        pitch_average=pitch_average,
        pitch_entropy=pitch_entropy,
        n_notes=len(pitches)
    )

def compute_interval_features(ordered_notes: List[NoteEvent]) -> IntervalFeatures:
    if len(ordered_notes) < 2:
        return IntervalFeatures(interval_entropy=0.0, n_intervals=0)
    pitches = [n.midi for n in ordered_notes]
    intervals = [b - a for a, b in zip(pitches, pitches[1:])]
    interval_entropy = shannon_entropy_counts(Counter(intervals))
    return IntervalFeatures(interval_entropy=interval_entropy, n_intervals=len(intervals))

def compute_ioi_features(representative: List[Tuple[float, NoteEvent]]) -> IOIFeatures:
    if len(representative) < 2:
        return IOIFeatures(0.0, 0.0, 0)
    onsets = [gp for gp, _ in representative]
    iois = []
    for a, b in zip(onsets, onsets[1:]):
        delta = b - a
        if delta > 0:
            iois.append(delta)
    if not iois:
        return IOIFeatures(0.0, 0.0, 0)
    ioi_avg = sum(iois)/len(iois)
    ioi_entropy = shannon_entropy_counts(Counter(iois))
    return IOIFeatures(ioi_average=ioi_avg, ioi_entropy=ioi_entropy, n_ioi=len(iois))
