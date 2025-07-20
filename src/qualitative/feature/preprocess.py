from typing import List, Dict, Tuple
from fractions import Fraction

from feature.utility import measure_length_in_beats
from parser.ast.measure_info import MeasureInfo, NoteEvent

def build_measure_start_positions(measures: List[MeasureInfo]) -> Dict[int, float]:
    acc = Fraction(0, 1)
    starts: Dict[int, float] = {}
    for m in sorted(measures, key=lambda x: x.index):
        starts[m.index] = float(acc)
        acc += measure_length_in_beats(m)
    return starts

def collect_note_candidates(
    measures: List[MeasureInfo],
    starts: Dict[int, float]
) -> Dict[float, List[NoteEvent]]:
    """
    global_pos -> list[NoteEvent]
    """
    by_pos: Dict[float, List[NoteEvent]] = {}
    for m in measures:
        base = starts[m.index]
        for n in m.notes:
            if n.midi is None or n.midi < 0:   # 休符排除
                continue
            gpos = base + float(n.start_beat)
            by_pos.setdefault(gpos, []).append(n)
    return by_pos

def collapse_polyphony(
    candidates_by_pos: Dict[float, List[NoteEvent]]
) -> List[Tuple[float, NoteEvent]]:
    """
    同時発音 → 最小 pitch, 次に order のノートのみ採用
    """
    reps: List[Tuple[float, NoteEvent]] = []
    for gpos, lst in candidates_by_pos.items():
        if len(lst) == 1:
            reps.append((gpos, lst[0]))
        else:
            chosen = min(lst, key=lambda nn: (nn.midi, nn.order))
            reps.append((gpos, chosen))
    reps.sort(key=lambda t: t[0])
    return reps
