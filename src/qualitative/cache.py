import json
import logging
import os
from pathlib import Path
from datetime import datetime
import hashlib
from typing import Optional, Tuple, TypeVar
from qualitative.gen_music import compose_music, to_measures

from returns.result import Success, Failure, Result

from utility.result import SimplifiedResult, aperture

def format_float(f: float, precision: int = 6) -> str:
    return f"{f:.{precision}f}"

def is_valid(abc:str) -> bool:
    result = to_measures(abc)
    return isinstance(result, Success)

def pick_cached_music(
    cache_dir: str | Path,
    axes_name:str,
    filename: str,
) -> SimplifiedResult[tuple[str, str], Exception]:
    path = Path(cache_dir) / axes_name / filename
    path.parent.mkdir(parents=True, exist_ok=True)

    if path.exists():
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        # バージョン互換チェック等あればここで
        validity_a = is_valid(data["abc_a"])
        validity_b = is_valid(data["abc_b"])
        if validity_a and validity_b:
            return Success((data["abc_a"], data["abc_b"]))
        else:
            if not validity_a: logging.error("編集前の楽譜aに異常がありました。再生成を試みます。")
            if not validity_b: logging.error("編集後の楽譜bに異常がありました。再生成を試みます。")
            return Failure(Exception("Parsing failed"))
    else:
        return Failure(Exception("file not found"))

def pick_previous_params(
    cache_dir: str | Path,
    axes_name:str,
    filename: str,
) -> SimplifiedResult[tuple[float, float], Exception]:
    path = Path(cache_dir) / axes_name / filename
    path.parent.mkdir(parents=True, exist_ok=True)

    if path.exists():
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        return Success((data["a"], data["b"]))
    else:
        return Failure(Exception("file not found"))

def compose_music_with_caching(
    X: str,
    a: float,
    b: float,
    cache_dir: str | Path,
    filename: str,
    precision: int = 6,
    hashing: bool = False,
) -> SimplifiedResult[tuple[str, str], Exception]:
    """
    compose_music の結果(abc_a, abc_b) を (X,a,b) ごとにキャッシュ。
    
    Parameters
    ----------
    X : str
    a, b : float
    cache_dir : キャッシュファイル
    precision : 浮動小数の丸め桁数（キー用）
    hashing : True の場合ファイル名にハッシュを使う（衝突ほぼ無）
    force_recompute : True ならキャッシュ無視して再生成

    Returns
    -------
    (abc_a, abc_b)
    """
    path = Path(cache_dir) / X / filename
    path.parent.mkdir(parents=True, exist_ok=True)

    match compose_music(X, a, b):
        case Failure(_) as f: return f
        case succ: abc_a, abc_b = succ.unwrap()
    
    data = {
        "version": 1,
        "X": X,
        "a": float(a),
        "b": float(b),
        "abc_a": abc_a,
        "abc_b": abc_b,
        "created": datetime.utcnow().isoformat() + "Z",
        "precision": precision,
        "hashing": hashing
    }
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return Success((abc_a, abc_b))