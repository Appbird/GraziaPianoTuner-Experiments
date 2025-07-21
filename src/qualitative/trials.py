from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
from pathlib import Path
import random
from dataclasses import asdict
from typing import TypedDict
import pandas as pd
from scipy.stats import pearsonr
from scipy.stats._stats_py import PearsonRResult

from qualitative.cache import compose_music_cached
from qualitative.feature.index import compute_extended_global_features
from qualitative.gen_music import to_measures

from returns.result import Success, Result, Failure
from utility.result import SimplifiedResult

FEATURE_COLUMNS = [
    "major_ratio", "minor_ratio", "bpm_mean",
    "chord_ratio_triad_diatonic", "chord_ratio_tetrad_diatonic", "chord_ratio_nondiatonic",
    "pitch_range", "pitch_average", "pitch_entropy",
    "interval_entropy", "ioi_average", "ioi_entropy"
]


def _safe_pearson(x_vals, y_vals) -> SimplifiedResult[PearsonRResult, Exception]:
    """
    分散ゼロや要素不足のとき NaN を返すヘルパ。
    """
    if len(x_vals) < 2:
        return Failure(Exception("safe_pearson: lack of samples."))
    if _variance_zero(x_vals) or _variance_zero(y_vals):
        return Failure(Exception("safe_pearson: variance is zero."))
    try:
        result: PearsonRResult = pearsonr(x_vals, y_vals)
        return Success(result)
    except Exception:
        return Failure(Exception("safe_pearson: variance is zero."))

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
    a, b = 0., 0.
    for _ in range(max_retry):
        a = rng.uniform(low_a, high_a)
        b = rng.uniform(low_b, high_b)
        if (not require_diff) or (abs(a - b) > 1e-3):
            return a, b
    # どうしても差が出ないなら最後を返す
    return a, b

class FeaturesDiff(TypedDict):
    a:float
    b:float
    dx:float
    diff_features:dict[str, int|float]

def compute_features_for_pair(
    X: str,
    a: float,
    b: float,
    cache_dir: str | Path = "data/cache_music",
    precision: int = 6,
    hashing: bool = False
) -> Result[FeaturesDiff, Exception]:
    match compose_music_cached(X, a, b, cache_dir=cache_dir, precision=precision, hashing=hashing):
        case Failure(_) as f: return f
        case Success(succ): abc_a, abc_b = succ
    return Result.do(
        { "a": a, "b": b, "dx": b - a, "diff_features": diff_features }
        for ma in to_measures(abc_a).bind(compute_extended_global_features).map(asdict)
        for mb in to_measures(abc_b).bind(compute_extended_global_features).map(asdict)
        for diff_features in Success({k: mb[k] - ma[k] for k in FEATURE_COLUMNS})
    )


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
) -> SimplifiedResult[pd.DataFrame, Exception]:
    rng = random.Random(seed)
    rows = []
    for X in adjs:
        logging.info(f"対象軸: {X}")
        # まず各 trial の a,b をシード固定で生成しておく
        ab_list = [sample_ab(rng, *range_a, *range_b) for _ in range(N)]
        # トライアル１つ分を実行する関数
        def run_trial(a_b_pair) -> SimplifiedResult[FeaturesDiff, Exception]:
            a, b = a_b_pair
            logging.info(f"[{X}] trial {a:.3f} -> {b:.3f} -- start to compose")
            # TODO:
            #   1. cache_dirをcache_fileにする(つまり、パラメータ基準での命名としない)
            #   2. その状態で、cache_fileに何か入っていればそれを読み込み、何も入っていなければ読み込まない、とする。
            #   3. 読み込み可能かどうかは事前に判別しておく。読み込み不可であった場合、もう一度再生成を試みる。
            #      ABC記譜法はパースにそれほど時間はかからないため、boolフラグなどを持つ必要はないと思われる。（それをする時間はない）
            match compute_features_for_pair(X, a, b,
                cache_dir=cache_dir,
                precision=precision,
                hashing=hashing
            ):
                case Success(_) as s:
                    logging.info(f"[{X}] trial {a:.3f} -> {b:.3f} -- finish composing")
                    return s
                case Failure(e):
                    logging.exception(f"[{X}] compute_features_for_pair エラー: {e}")
            return Failure(Exception(f"Failed to compose: {e}"))
        # 10スレッドで並列に実行
        deltas_x = []
        missing_count = 0
        deltas_by_feature = {feat: [] for feat in FEATURE_COLUMNS}
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(run_trial, ab) for ab in ab_list]
            for fut in as_completed(futures):
                match fut.result():
                    case Failure(err):
                        logging.error(err)
                        missing_count += 1
                    case Success(succ):
                        diff_feats = succ
                        deltas_x.append(diff_feats["dx"])
                        for feat, val in diff_feats["diff_features"].items():
                            deltas_by_feature[feat].append(val)

        if missing_count > 0:
            logging.error(f"{missing_count}曲で生成に失敗しました。生成に失敗した分について、もう一度再生成してください。")
            logging.info(f"コマンドラインプロンプトでもう一度同じコマンドを打てば、生成に失敗した分を同じパラメータで再生成できます。")

        # 相関計算
        def r(feat: str) -> float:
            match _safe_pearson(deltas_x, deltas_by_feature[feat]):
                case Failure(err):
                    logging.info(f"replaced to NaN @ {feat} / {ab_list} / {X}: {err}")
                    return float("nan")
                case Success(succ):
                    return succ.correlation
        row = {feat: f"{r(feat):.3f}" for feat in FEATURE_COLUMNS}
        row["__trials__"] = str(N)
        rows.append((X, row))
    df = pd.DataFrame({name: data for name, data in rows}).T
    df = df[FEATURE_COLUMNS + ["__trials__"]]
    df.to_csv(csv_path, encoding="utf-8")
    return Success(df)

# 使い方例:
# adjs = ["明るさ", "ジャズ感", "静けさ"]
# df_corr = run_experiments(adjs, N=30)
# print(df_corr)