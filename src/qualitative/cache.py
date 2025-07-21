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

def compose_music_cached(
    X: str,
    a: float,
    b: float,
    cache_dir: str | Path = "cache_music",
    precision: int = 6,
    hashing: bool = False,
    force_recompute: bool = False,
) -> SimplifiedResult[tuple[str, str], Exception]:
    """
    compose_music の結果(abc_a, abc_b) を (X,a,b) ごとにキャッシュ。
    
    Parameters
    ----------
    X : str
    a, b : float
    cache_dir : ルートキャッシュディレクトリ
    precision : 浮動小数の丸め桁数（キー用）
    hashing : True の場合ファイル名にハッシュを使う（衝突ほぼ無）
    force_recompute : True ならキャッシュ無視して再生成

    Returns
    -------
    (abc_a, abc_b)
    """
    cache_dir = Path(cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)

    a_str = format_float(a, precision)
    b_str = format_float(b, precision)

    if hashing:
        key_raw = f"{X}|{a_str}|{b_str}"
        key = hashlib.sha256(key_raw.encode()).hexdigest()[:16]
        subdir = cache_dir / X
        filename = f"{key}.json"
    else:
        subdir = cache_dir / X
        filename = f"{a_str}_{b_str}.json"

    subdir.mkdir(parents=True, exist_ok=True)
    path = subdir / filename

    if path.exists() and not force_recompute:
        try:
            with path.open("r", encoding="utf-8") as f:
                data = json.load(f)
            # バージョン互換チェック等あればここで
            validity_a = is_valid(data["abc_a"])
            validity_b = is_valid(data["abc_b"])
            if validity_a and validity_b:
                return Success((data["abc_a"], data["abc_b"]))
            else:
                if validity_a: logging.error("編集前の楽譜aに異常がありました。再生成を試みます。")
                if validity_b: logging.error("編集後の楽譜bに異常がありました。再生成を試みます。")
        except Exception:
            pass

    match compose_music(X, a, b):
        case Failure(_) as f: return f
        case succ: abc_a, abc_b = succ.unwrap()

    data = {
        "version": 1,
        "X": X,
        "a": float(a_str),
        "b": float(b_str),
        "abc_a": abc_a,
        "abc_b": abc_b,
        "created": datetime.utcnow().isoformat() + "Z",
        "precision": precision,
        "hashing": hashing
    }
    tmp_path = path.with_suffix(".tmp")
    with tmp_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp_path, path)  # atomic-ish

    return Success((abc_a, abc_b))