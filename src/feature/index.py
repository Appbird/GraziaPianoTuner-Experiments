from typing import List

from feature.data import ExtendedGlobalFeatures
from feature.features import compute_harmonic_features, compute_interval_features, compute_ioi_features, compute_pitch_features
from feature.preprocess import build_measure_start_positions, collapse_polyphony, collect_note_candidates
from parser.ast.measure_info import MeasureInfo

# ==== Aggregator ====
def compute_extended_global_features(measures: List[MeasureInfo]) -> ExtendedGlobalFeatures:
    harmonic = compute_harmonic_features(measures)
    starts = build_measure_start_positions(measures)
    candidates = collect_note_candidates(measures, starts)
    representative = collapse_polyphony(candidates)
    ordered_notes = [n for _, n in representative]

    pitch = compute_pitch_features(ordered_notes)
    interval = compute_interval_features(ordered_notes)
    ioi = compute_ioi_features(representative)

    return ExtendedGlobalFeatures(
        **harmonic.__dict__,
        **pitch.__dict__,
        **interval.__dict__,
        **ioi.__dict__
    )
