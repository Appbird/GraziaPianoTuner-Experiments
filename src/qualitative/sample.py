#!/usr/bin/env python3
import json
import random
from pathlib import Path
from dataclasses import asdict
from typing import List, Dict
import pandas as pd

from conversion.abc2audio import abc2wav
from qualitative.feature.index import compute_extended_global_features
from qualitative.gen_music import to_measures

# ==== ここで既存の関数 / クラスを import する想定 ====
# from your_module import to_measures, compute_extended_global_features, ExtendedGlobalFeatures, abc2audio

FEATURE_COLUMNS = [
    "major_ratio","minor_ratio","bpm_mean",
    "chord_ratio_triad_diatonic","chord_ratio_tetrad_diatonic","chord_ratio_nondiatonic",
    "pitch_range","pitch_average","pitch_entropy",
    "interval_entropy","ioi_average","ioi_entropy"
]

def load_cache_records(cache_root: Path) -> Dict[str, List[Path]]:
    """
    cache_root/X/*.json を走査し、X -> JSONファイル一覧。
    """
    axis_map: Dict[str, List[Path]] = {}
    if not cache_root.exists():
        return axis_map
    for axis_dir in cache_root.iterdir():
        if not axis_dir.is_dir():
            continue
        files = [p for p in axis_dir.glob("*.json") if p.is_file()]
        if files:
            axis_map[axis_dir.name] = files
    return axis_map

def pick_samples(files: List[Path], k: int, rng: random.Random) -> List[Path]:
    if len(files) <= k:
        return files
    return rng.sample(files, k)

def read_cache_file(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)

def compute_features_from_abc(abc_text: str):
    measures = to_measures(abc_text)
    feat = compute_extended_global_features(measures)
    return asdict(feat)

def write_abc(text: str, path: Path):
    path.write_text(text, encoding="utf-8")

def format_markdown_summary(X: str, sample_id: int, a: float, b: float,
                            feat_a: dict, feat_b: dict, deltas: dict) -> str:
    lines = []
    lines.append(f"# {X} / Sample {sample_id:02d}")
    lines.append("")
    lines.append(f"- a = {a}")
    lines.append(f"- b = {b}")
    lines.append(f"- Δx = {b - a}")
    lines.append("")
    lines.append("| Feature | A | B | Δ (B - A) |")
    lines.append("|---------|---|---|-----------|")
    for k in FEATURE_COLUMNS:
        va = feat_a[k]
        vb = feat_b[k]
        vd = deltas[k]
        lines.append(f"| {k} | {va:.6g} | {vb:.6g} | {vd:.6g} |")
    lines.append("")
    return "\n".join(lines)

def process_axis(
    X: str,
    files: List[Path],
    out_root: Path,
    rng: random.Random,
    k: int = 3,
    audio: bool = True
):
    samples = pick_samples(files, k, rng)
    records_for_csv = []
    axis_out = out_root / X
    axis_out.mkdir(parents=True, exist_ok=True)

    for idx, file_path in enumerate(samples, start=1):
        try:
            data = read_cache_file(file_path)
        except Exception as e:
            print(f"[WARN] Failed to read {file_path}: {e}")
            continue

        a = data.get("a")
        b = data.get("b")
        abc_a = data.get("abc_a")
        abc_b = data.get("abc_b")
        if abc_a is None or abc_b is None:
            print(f"[WARN] Missing abc in {file_path}")
            continue

        # 出力ディレクトリ
        sample_dir = axis_out / f"{idx:02d}"
        sample_dir.mkdir(parents=True, exist_ok=True)

        # ABC 書き出し
        a_abc_path = sample_dir / "a.abc"
        b_abc_path = sample_dir / "b.abc"
        write_abc(abc_a, a_abc_path)
        write_abc(abc_b, b_abc_path)

        # 特徴量計算
        feat_a = compute_features_from_abc(abc_a)
        feat_b = compute_features_from_abc(abc_b)
        deltas = {k: feat_b[k] - feat_a[k] for k in FEATURE_COLUMNS}

        # JSON 保存
        feat_out = {
            "X": X,
            "a": a,
            "b": b,
            "delta_x": b - a,
            "features_a": {k: feat_a[k] for k in FEATURE_COLUMNS},
            "features_b": {k: feat_b[k] for k in FEATURE_COLUMNS},
            "deltas": deltas
        }
        (sample_dir / "features.json").write_text(
            json.dumps(feat_out, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )

        # Markdown summary
        (sample_dir / "summary.md").write_text(
            format_markdown_summary(X, idx, a, b, feat_a, feat_b, deltas),
            encoding="utf-8"
        )

        # Audio (任意)
        if audio:
            try:
                abc2wav(abc_a, str(sample_dir / "a.midi"), str(sample_dir / "a.wav"))
                abc2wav(abc_b, str(sample_dir / "b.midi"), str(sample_dir / "b.wav"))
            except Exception as e:
                print(f"[WARN] audio generation failed for {file_path}: {e}")

        # CSV 用フラットレコード (A, B, Δ)
        flat_row = {
            "X": X,
            "sample_id": idx,
            "a": a,
            "b": b,
            "delta_x": b - a
        }
        for key in FEATURE_COLUMNS:
            flat_row[f"A_{key}"] = feat_a[key]
            flat_row[f"B_{key}"] = feat_b[key]
            flat_row[f"D_{key}"] = deltas[key]
        records_for_csv.append(flat_row)

    return records_for_csv

def export_representatives(
    cache_root: str | Path = "cache_music",
    out_root: str | Path = "representatives",
    k: int = 3,
    seed: int = 123,
    audio: bool = True,
    csv_name: str = "summary_all.csv"
):
    cache_root = Path(cache_root)
    out_root = Path(out_root)
    out_root.mkdir(parents=True, exist_ok=True)

    rng = random.Random(seed)
    axis_map = load_cache_records(cache_root)

    all_rows = []
    for X, files in axis_map.items():
        rows = process_axis(X, files, out_root, rng, k=k, audio=audio)
        all_rows.extend(rows)

    if all_rows:
        df = pd.DataFrame(all_rows)
        csv_path = out_root / csv_name
        df.to_csv(csv_path, index=False, encoding="utf-8")
        print(f"[INFO] Wrote CSV: {csv_path}")
    else:
        print("[INFO] No records produced.")

# === 実行例 ===
if __name__ == "__main__":
    export_representatives(
        cache_root="cache_music",
        out_root="representatives",
        k=3,
        seed=42,
        audio=True
    )
