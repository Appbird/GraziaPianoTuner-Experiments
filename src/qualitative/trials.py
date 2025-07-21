import logging
from pathlib import Path
import random
import math
from dataclasses import asdict
from typing import Callable, Sequence
import pandas as pd
from scipy.stats import pearsonr

from qualitative.cache import compose_music_cached
from qualitative.feature.index import compute_extended_global_features
from qualitative.gen_music import compose_music, to_measures


FEATURE_COLUMNS = [
    "major_ratio", "minor_ratio", "bpm_mean",
    "chord_ratio_triad_diatonic", "chord_ratio_tetrad_diatonic", "chord_ratio_nondiatonic",
    "pitch_range", "pitch_average", "pitch_entropy",
    "interval_entropy", "ioi_average", "ioi_entropy"
]

def _safe_pearson(x_vals, y_vals):
    """
    分散ゼロや要素不足のとき NaN を返すヘルパ。
    """
    if len(x_vals) < 2:
        return float("nan")
    if _variance_zero(x_vals) or _variance_zero(y_vals):
        return float("nan")
    try:
        r, _ = pearsonr(x_vals, y_vals)
        return r
    except Exception:
        return float("nan")

def _variance_zero(xs):
    first = xs[0]
    for v in xs[1:]:
        if v != first:
            return False
    return True

def sample_ab(rng: random.Random, low_a: float, high_a: float,
              low_b: float, high_b: float,
              require_diff: bool = True,
              max_retry: int = 20):
    """
    a,b を独立一様サンプリング。a==b を避けたいなら再試行。
    """
    for _ in range(max_retry):
        a = rng.uniform(low_a, high_a)
        b = rng.uniform(low_b, high_b)
        if (not require_diff) or (abs(a - b) > 1e-3):
            return a, b
    # どうしても差が出ないなら最後を返す
    return a, b
def compute_features_for_pair(
    X: str,
    a: float,
    b: float,
    cache_dir: str | Path = "data/cache_music",
    precision: int = 6,
    hashing: bool = False
) -> dict:
    abc_a, abc_b = compose_music_cached(
        X, a, b,
        cache_dir=cache_dir,
        precision=precision,
        hashing=hashing
    )
    measures_a = to_measures(abc_a)
    measures_b = to_measures(abc_b)
    feat_a = compute_extended_global_features(measures_a)
    feat_b = compute_extended_global_features(measures_b)
    dict_a = asdict(feat_a)
    dict_b = asdict(feat_b)
    diff = {k: dict_b[k] - dict_a[k] for k in FEATURE_COLUMNS}
    return {
        "a": a,
        "b": b,
        "dx": b - a,
        "diff_features": diff
    }

def run_experiments(
    adjs,
    N=30,
    range_a=(0.0,1.0),
    range_b=(0.0,1.0),
    seed=42,
    csv_path="param_feature_correlations.csv",
    cache_dir="cache_music",
    precision=6,
    hashing=False
):
    rng = random.Random(seed)
    rows = []
    for X in adjs:
        logging.info(f"対象軸: {X}")
        deltas_x = []
        deltas_by_feature = {feat: [] for feat in FEATURE_COLUMNS}
        for _ in range(N):
            a, b = sample_ab(rng, *range_a, *range_b)
            logging.info(f"対象値: {a} -> {b}")
            persistance = 3
            while persistance > 0:
                try:
                    result = compute_features_for_pair(
                        X, a, b,
                        cache_dir=cache_dir,
                        precision=precision,
                        hashing=hashing
                    )
                    break
                except Exception as e:
                    logging.exception(f"compute_feature_for _ pair: {e}")
                    persistance -= 1
                    if persistance > 0:
                        logging.info(f"もう一度生成しなおします。(persistance = {persistance})") 
                    else:
                        print("Failed to generate music three times: ")
                        exit(1)
            dx = result["dx"]
            deltas_x.append(dx)
            for feat, val in result["diff_features"].items():
                deltas_by_feature[feat].append(val)
        r = lambda feat: _safe_pearson(deltas_x, deltas_by_feature[feat])
        row = {feat: f"{r(feat):.3f}" for feat in FEATURE_COLUMNS}
        row["__trials__"] = str(N)
        rows.append((X, row))
    df = pd.DataFrame({name: data for name, data in rows}).T
    df = df[FEATURE_COLUMNS + ["__trials__"]]
    df.to_csv(csv_path, encoding="utf-8")
    return df

# 使い方例:
# adjs = ["明るさ", "ジャズ感", "静けさ"]
# df_corr = run_experiments(adjs, N=30)
# print(df_corr)