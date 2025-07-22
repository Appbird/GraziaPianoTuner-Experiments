from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
from os import makedirs
from pathlib import Path
import random
from dataclasses import asdict
from typing import TypedDict
from matplotlib import pyplot as plt
import pandas as pd
from scipy.stats import pearsonr, spearmanr
from scipy.stats._stats_py import PearsonRResult

from qualitative.cache import compose_music_with_caching, pick_cached_music, pick_previous_params
from qualitative.feature.index import compute_extended_global_features
from qualitative.gen_music import to_measures

from returns.result import Success, Result, Failure
from utility.result import SimplifiedResult, aperture

FEATURE_COLUMNS = [
    "major_ratio", "minor_ratio", "bpm_mean",
    "chord_ratio_triad_diatonic", "chord_ratio_tetrad_diatonic", "chord_ratio_nondiatonic",
    "pitch_range", "pitch_average", "pitch_entropy",
    "interval_entropy", "ioi_average", "ioi_entropy"
]


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
    i: int,
    a: float, # キャッシュファイルがあったときはそちらを優先する
    b: float, 
    cache_dir: str | Path = "data/cache_music",
    hashing: bool = False
) -> Result[FeaturesDiff, Exception]:
    match pick_cached_music(axes_name=X, filename=f"{i}.json", cache_dir=cache_dir):
        case Success(succ):     abc_a, abc_b = succ
        case Failure(_) as f:
            match pick_previous_params(axes_name=X, filename=f"{i}.json", cache_dir=cache_dir):
                case Success(succ):
                    a, b = succ
                    logging.info(f"[{i}/{X}/{a}-{b}] start regeneration...")
                case Failure(_) as f: pass
            match compose_music_with_caching(X, a, b, filename=f"{i}.json", cache_dir=cache_dir, hashing=hashing):
                case Success(succ):     abc_a, abc_b = succ
                case Failure(_) as f:   return f
    return Result.do(
        { "a": a, "b": b, "dx": b - a, "diff_features": diff_features }
        for ma in to_measures(abc_a).bind(compute_extended_global_features).map(asdict)
        for mb in to_measures(abc_b).bind(compute_extended_global_features).map(asdict)
        for diff_features in Success({k: mb[k] - ma[k] for k in FEATURE_COLUMNS})
    )


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
    except Exception as e:
        return Failure(Exception(f"safe_pearson: something wrong happened.: {e}"))


def run_experiments(
    adjs,
    N=30,
    range_a=(0.0,1.0),
    range_b=(0.0,1.0),
    seed=42,
    csv_path="param_feature_correlations.csv",
    cache_dir="cache_music",
    hashing=False
) -> SimplifiedResult[tuple[pd.DataFrame, pd.DataFrame], Exception]:
    rng = random.Random(seed)
    rows_r = []
    rows_p = []
    for X in adjs:
        logging.info(f"対象軸: {X}")
        # まず各 trial の a,b をシード固定で生成しておく
        ab_list = [sample_ab(rng, *range_a, *range_b) for _ in range(N)]
        # トライアル１つ分を実行する関数
        def run_trial(i:int, a_b_pair) -> SimplifiedResult[FeaturesDiff, Exception]:
            a, b = a_b_pair
            logging.info(f"[{X}] trial {a:.3f} -> {b:.3f} -- start to compose")
            result = compute_features_for_pair(X, i, a, b, cache_dir=cache_dir, hashing=hashing)
            match aperture(result):
                case Success(_) as s:
                    logging.info(f"[{X}] trial {a:.3f} -> {b:.3f} -- finish composing")
                    return s
                case Failure(e):
                    logging.error(f"[{X}/{i}] Failed to compose/compute: {e}")
                    return Failure(Exception(f"Failed to compose: {e}"))
        # 10スレッドで並列に実行
        deltas_x = []
        start_idx = 0
        missing_count = 0
        deltas_by_feature = {feat: [] for feat in FEATURE_COLUMNS}
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(run_trial, i, ab_list[i-start_idx]) for i in range(start_idx, start_idx+N)]
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
        def r(feat: str) -> tuple[float, float]:
            match _safe_pearson(deltas_x, deltas_by_feature[feat]):
                case Failure(err):
                    logging.info(f"replaced to NaN @ {feat} / {ab_list} / {X}: {err}")
                    return float("nan"), float("nan")
                case Success(succ):
                    return succ.correlation, succ.pvalue # type:ignore
        def plot(feat:str) -> None:
            """
            Scatter plot of deltas_x vs. deltas_by_feature[feat].
            """
            x = deltas_x
            y = deltas_by_feature[feat]            
            plt.scatter(x, y)
            plt.xlabel('deltas_x')
            plt.ylabel(feat)
            plt.title(f'Scatter plot of {feat}')
            plt.savefig(Path(cache_dir).parent/f"figures/{X}/{feat}.png")
            plt.clf()
        makedirs(Path(cache_dir).parent/f"figures/{X}", exist_ok=True)
        row_r: dict[str, str] = {}
        row_p: dict[str, str] = {}
        for feat in FEATURE_COLUMNS:
            plot(feat)
            r_value, p_value= r(feat)
            row_r[feat] = f"{r_value:.3f}"
            row_p[feat] = f"{p_value:.3f}"
        row_r["__trials__"] = str(N)
        row_p["__trials__"] = str(N)
        rows_r.append((X, row_r))
        rows_p.append((X, row_p))
    df_r = pd.DataFrame({name: data for name, data in rows_r}).T
    df_r = df_r[FEATURE_COLUMNS + ["__trials__"]]
    csv_path = Path(csv_path)
    df_r.to_csv(csv_path, encoding="utf-8")
    df_p = pd.DataFrame({name: data for name, data in rows_p}).T
    df_p = df_p[FEATURE_COLUMNS + ["__trials__"]]
    df_p.to_csv(csv_path.with_name(f"{csv_path.stem}.pvalue.csv"), encoding="utf-8")
    return Success((df_r, df_p))

# 使い方例:
# adjs = ["明るさ", "ジャズ感", "静けさ"]
# df_corr = run_experiments(adjs, N=30)
# print(df_corr)