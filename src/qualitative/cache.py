import json
import os
from pathlib import Path
from datetime import datetime
import hashlib

from qualitative.gen_music import compose_music

def format_float(f: float, precision: int = 6) -> str:
    return f"{f:.{precision}f}"

def compose_music_cached(
    X: str,
    a: float,
    b: float,
    cache_dir: str | Path = "cache_music",
    precision: int = 6,
    hashing: bool = False,
    force_recompute: bool = False,
) -> tuple[str, str]:
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
        # 可読性重視
        subdir = cache_dir / X
        filename = f"{a_str}_{b_str}.json"

    subdir.mkdir(parents=True, exist_ok=True)
    path = subdir / filename

    if path.exists() and not force_recompute:
        try:
            with path.open("r", encoding="utf-8") as f:
                data = json.load(f)
            # バージョン互換チェック等あればここで
            return data["abc_a"], data["abc_b"]
        except Exception:
            # 壊れていたら再生成
            pass

    # 実際の生成（重い処理想定）
    abc_a, abc_b = compose_music(X, a, b)

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

    return abc_a, abc_b
