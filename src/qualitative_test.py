#!/usr/bin/env python3
"""
qualitative_test.py

エントリポイント:
1) パラメータ軸ごとの実験 (相関行列 CSV 出力)
2) キャッシュから代表サンプル抽出 (ABC / 特徴量 / 音声)
"""

from __future__ import annotations
import argparse
import sys
import json
from pathlib import Path
import logging
from typing import Sequence

from qualitative.sample import export_representatives
from qualitative.trials import run_experiments

DEFAULT_FEATURE_CORR_CSV = "./data/qualitative/param_feature_correlations.csv"
DEFAULT_CACHE_DIR = "./data/qualitative/cache_music"
DEFAULT_REPR_OUT = "./data/qualitative/representatives"

def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run param-feature correlation experiments and export representative samples."
    )

    # パラメータ軸の指定（JSON / CSV / 直接リストいずれか）
    parser.add_argument(
        "--axes", "-x",
        nargs="*",
        help="パラメータ軸名 (スペース区切り)。--axes-file があればそちら優先。"
    )
    parser.add_argument(
        "--axes-file",
        type=str,
        help="軸名を列挙した JSON(list) かテキスト(1行1軸) ファイル。"
    )

    # 実験条件
    parser.add_argument("--trials", "-n", type=int, default=2, help="各軸での試行回数 N (default: 30)")
    parser.add_argument("--range-a", type=float, nargs=2, default=[0.0, 1.0], metavar=("A_MIN", "A_MAX"),
                        help="a のサンプリング範囲 (default 0 1)")
    parser.add_argument("--range-b", type=float, nargs=2, default=[0.0, 1.0], metavar=("B_MIN", "B_MAX"),
                        help="b のサンプリング範囲 (default 0 1)")
    parser.add_argument("--seed", type=int, default=42, help="乱数シード")
    parser.add_argument("--precision", type=int, default=6, help="キャッシュキー丸め桁数")
    parser.add_argument("--hashing", action="store_true", help="キャッシュファイル名にハッシュを使用")

    # キャッシュ & 出力
    parser.add_argument("--cache-dir", type=str, default=DEFAULT_CACHE_DIR, help="compose_music キャッシュディレクトリ")
    parser.add_argument("--corr-csv", type=str, default=DEFAULT_FEATURE_CORR_CSV, help="相関行列出力 CSV パス")
    parser.add_argument("--repr-out", type=str, default=DEFAULT_REPR_OUT, help="代表サンプル出力ルート")
    parser.add_argument("--repr-k", type=int, default=1, help="代表抽出サンプル数 / 軸 (<= 既存件数)")
    parser.add_argument("--no-audio", action="store_true", help="代表抽出で音声生成をスキップ")

    # 実行フラグ
    parser.add_argument("--skip-experiments", action="store_true", help="相関計算ステップをスキップ")
    parser.add_argument("--skip-representatives", action="store_true", help="代表抽出ステップをスキップ")

    # ログ
    parser.add_argument("--log-level", type=str, default="INFO", help="ログレベル (DEBUG/INFO/WARNING/ERROR)")

    return parser.parse_args(argv)


def load_axes(args: argparse.Namespace) -> list[str]:
    # 優先順位: --axes-file > --axes > エラー
    if args.axes_file:
        p = Path(args.axes_file)
        if not p.exists():
            raise FileNotFoundError(f"axes file not found: {p}")

        if p.suffix.lower() in {".json"}:
            data = json.loads(p.read_text(encoding="utf-8"))
            if not isinstance(data, list):
                raise ValueError("JSON axes file must contain a list of strings.")
            axes = [str(x) for x in data]
        else:
            # テキスト 1行1軸
            axes = [line.strip() for line in p.read_text(encoding="utf-8").splitlines() if line.strip()]
        return axes

    if args.axes: return list(args.axes)

    raise ValueError("No axes specified. Use --axes or --axes-file.")


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    logging.basicConfig(
        level=getattr(logging, args.log_level.upper(), logging.INFO),
        format="%(levelname)s: %(message)s"
    )

    try:
        axes = load_axes(args)
    except Exception as e:
        logging.error(f"軸リスト読み込み失敗: {e}")
        return 1

    if not axes:
        logging.error("軸が空です。")
        return 1

    logging.info(f"対象軸: {axes}")

    # 1) 実験 (相関行列)
    if not args.skip_experiments:
        logging.info("=== 実験 (相関行列計算) 開始 ===")
        try:
            df_corr = run_experiments(
                adjs=axes,
                N=args.trials,
                range_a=tuple(args.range_a),
                range_b=tuple(args.range_b),
                seed=args.seed,
                csv_path=args.corr_csv,
                cache_dir=args.cache_dir,
                hashing=args.hashing
            )
            logging.info(f"相関行列 CSV 出力: {args.corr_csv}")
            logging.debug(f"\n{df_corr}")
        except Exception as e:
            logging.exception(f"相関計算中にエラー: {e}")
    else:
        logging.info("相関計算ステップをスキップ (--skip-experiments)")

    # 2) 代表サンプル抽出
    if not args.skip_representatives:
        logging.info("=== 代表サンプル抽出 開始 ===")
        try:
            export_representatives(
                cache_root=args.cache_dir,
                out_root=args.repr_out,
                k=args.repr_k,
                seed=args.seed,
                audio=not args.no_audio
            )
            logging.info(f"代表サンプル出力: {args.repr_out}")
        except Exception as e:
            logging.exception(f"代表抽出中にエラー: {e}")
            return 1
    else:
        logging.info("代表抽出ステップをスキップ (--skip-representatives)")

    logging.info("=== 完了 ===")
    return 0


if __name__ == "__main__":
    main()
