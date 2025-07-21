#!/usr/bin/env python3
"""
grid_feature_sampling.py

11x11 グリッド (x,y) で特徴量 f(x,y) を計測。
各点 T 回再生成して平均 (＋必要なら標準偏差) を CSV 出力。

Usage:
    python grid_feature_sampling.py --axes 明るさ ジャズ感 --trials 5 --out-csv grid_features.csv
"""

from __future__ import annotations
import argparse, math, json
from pathlib import Path
from dataclasses import asdict
from statistics import mean, pstdev
from typing import List, Dict

from qualitative.feature.index import compute_extended_global_features
from qualitative.gen_music import compose_with_two_axes, to_measures
from returns.pipeline import flow
from returns.pointfree import bind
from returns.result import Success, Failure

from utility.result import SimplifiedResult

# ====== 既存モジュールからインポートする前提 ======
# from yourpkg.generation import compose_with_two_axes
# from yourpkg.features import to_measures, compute_extended_global_features

FEATURE_COLUMNS = [
    "major_ratio","minor_ratio","bpm_mean",
    "chord_ratio_triad_diatonic","chord_ratio_tetrad_diatonic","chord_ratio_nondiatonic",
    "pitch_range","pitch_average","pitch_entropy",
    "interval_entropy","ioi_average","ioi_entropy"
]

N = 10
GRID_VALUES = [i/N for i in range(N+1)]

def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument("--axes", nargs=2, required=True, metavar=("X","Y"),
                    help="2軸の名前")
    ap.add_argument("--trials", type=int, default=5, help="各格子点の試行数 (デフォルト5)")
    ap.add_argument("--out-csv", type=str, default="./data/qualitative_grid/grid_features.csv")
    ap.add_argument("--cache-dir", type=str, default="./data/qualitative_grid/cache_two_axes")
    ap.add_argument("--no-cache", action="store_true", help="キャッシュを使わず毎回生成")
    ap.add_argument("--with-std", action="store_true", help="標準偏差も出力")
    ap.add_argument("--features", nargs="*", help="出力する特徴量を限定（未指定なら全て）")
    ap.add_argument("--precision", type=int, default=3, help="キャッシュファイル名の丸め桁数")
    return ap.parse_args()

def cache_path(cache_root: Path, i:int, X: str, Y: str, x: float, y: float, precision: int) -> Path:
    return cache_root / f"{X}__{Y}" / f"{i}__{x:.{precision}f}_{y:.{precision}f}.abc"

def load_or_generate_abc(i:int, X: str, Y: str, x: float, y: float,
                         cache_root: Path, use_cache: bool, precision: int) -> SimplifiedResult[str, Exception]:
    if use_cache:
        path = cache_path(cache_root, i, X, Y, x, y, precision)
        if path.exists():
            return Success(path.read_text(encoding="utf-8"))
    match compose_with_two_axes(X, Y, x, y):
        case Failure(_) as f: return f
        case Success(succ): abc = succ
    if use_cache:
        path = cache_path(cache_root, i, X, Y, x, y, precision)
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(".tmp")
        tmp.write_text(abc, encoding="utf-8")
        tmp.replace(path)
    return Success(abc)

def compute_single_features(abc: str) -> dict:
    return flow(
        abc,
        to_measures,
        compute_extended_global_features,
        asdict
    )

def main():
    args = parse_args()
    X, Y = args.axes
    use_cache = not args.no_cache
    cache_root = Path(args.cache_dir)
    chosen_feats = args.features if args.features else FEATURE_COLUMNS

    rows = []
    total_points = len(GRID_VALUES)**2
    point_index = 0

    for x in GRID_VALUES:
        for y in GRID_VALUES:
            point_index += 1
            feat_samples: Dict[str, List[float]] = {k: [] for k in chosen_feats}

            for t in range(args.trials):
                print(f"trial = {t}")
                match load_or_generate_abc(t, X, Y, x, y, cache_root, use_cache, args.precision):
                    case Failure(_) as f: return f
                    case Success(succ): abc = succ
                feats = compute_single_features(abc)
                for k in chosen_feats:
                    feat_samples[k].append(feats[k])

            row = {"X_axis": X, "Y_axis": Y, "x": x, "y": y}
            for k, vals in feat_samples.items():
                row[f"{k}_mean"] = mean(vals)
                if args.with_std:
                    # 全母集団とは言えないが簡便に母標準偏差(pstdev)利用
                    row[f"{k}_std"] = pstdev(vals) if len(vals) > 1 else 0.0
            rows.append(row)
            print(f"[INFO] ({point_index}/{total_points}) done x={x:.1f}, y={y:.1f}")

    # CSV 出力
    import csv
    out_path = Path(args.out_csv)
    # ヘッダ順
    header = ["X_axis","Y_axis","x","y"]
    for k in chosen_feats:
        header.append(f"{k}_mean")
        if args.with_std:
            header.append(f"{k}_std")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writeheader()
        writer.writerows(rows)

    # メタ情報も保存しとく
    meta = {
        "X": X, "Y": Y,
        "grid_values": GRID_VALUES,
        "trials": args.trials,
        "features": chosen_feats,
        "with_std": args.with_std,
        "cache_used": use_cache,
        "points": total_points,
        "csv": str(out_path)
    }
    out_meta = out_path.with_suffix(".meta.json")
    out_meta.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[INFO] CSV written: {out_path}")
    print(f"[INFO] Meta written: {out_meta}")

if __name__ == "__main__":
    raise SystemExit(main())
