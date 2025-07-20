from dataclasses import dataclass


@dataclass
class HarmonicFeatures:
    major_ratio: float
    minor_ratio: float
    bpm_mean: float
    chord_ratio_triad_diatonic: float
    chord_ratio_tetrad_diatonic: float
    chord_ratio_nondiatonic: float
    n_measures: int
    n_chords: int

@dataclass
class PitchFeatures:
    pitch_range: float
    pitch_average: float
    pitch_entropy: float
    n_notes: int

@dataclass
class IntervalFeatures:
    interval_entropy: float
    n_intervals: int

@dataclass
class IOIFeatures:
    ioi_average: float
    ioi_entropy: float
    n_ioi: int

@dataclass
class ExtendedGlobalFeatures(HarmonicFeatures, PitchFeatures, IntervalFeatures, IOIFeatures):
    pass
