#!/usr/bin/env python3
import argparse
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # GUI不要環境想定
import matplotlib.pyplot as plt

def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True)
    ap.add_argument("--result_dir", type=Path, required=True, default=None)
    ap.add_argument("--cmap", default="viridis")
    ap.add_argument("--annot", action="store_true", help="各セルに数値表示")
    ap.add_argument("--contour", action="store_true", help="等高線を重ねる")
    ap.add_argument("--dpi", type=int, default=200)
    ap.add_argument("--fmt", default=".2f", help="annot表示フォーマット")
    return ap.parse_args()


def plot_heatmap_for_feature(df: pd.DataFrame, feature: str, args, result_dir: Path) -> None:
    base = f"{feature}_mean"
    if base not in df.columns:
        print(f"[WARN] {base} が無いのでスキップ")
        return

    pivot = df.pivot(index="y", columns="x", values=base).sort_index()
    xs = pivot.columns.values
    ys = pivot.index.values
    Z = pivot.values

    out_img = result_dir / f"{Path(args.csv).stem}_{feature}_heatmap.png"

    fig, ax = plt.subplots(figsize=(6, 5))
    im = ax.imshow(
        Z,
        origin="lower",
        cmap=args.cmap,
        extent=[xs.min(), xs.max(), ys.min(), ys.max()], # type:ignore
        aspect="equal"
    )
    cbar = fig.colorbar(im)
    cbar.set_label(base)

    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_title(f"{feature} (mean)")

    if args.contour:
        n_levels = 8
        levels = np.linspace(np.nanmin(Z), np.nanmax(Z), n_levels)
        cs = ax.contour(
            np.linspace(xs.min(), xs.max(), Z.shape[1]),
            np.linspace(ys.min(), ys.max(), Z.shape[0]),
            Z,
            levels=levels,
            colors="k",
            linewidths=0.6
        )
        ax.clabel(cs, inline=True, fontsize=8, fmt="%.2f")

    if args.annot:
        for j, yv in enumerate(ys):
            for i, xv in enumerate(xs):
                val = Z[j, i]
                ax.text(
                    xv, yv,
                    format(val, args.fmt),
                    ha="center", va="center",
                    fontsize=7,
                    color="white" if val > (np.nanmin(Z)+np.nanmax(Z))/2 else "black"
                )

    plt.tight_layout()
    plt.savefig(out_img, dpi=args.dpi)
    plt.close(fig)
    print(f"[INFO] Saved heatmap: {out_img}")


def main():
    args = parse_args()
    df = pd.read_csv(args.csv)

    # 出力ディレクトリ作成
    result_dir = Path(args.result_dir)
    result_dir.mkdir(parents=True, exist_ok=True)

    # 特定featureのみ or 全部
    features = sorted({c[:-5] for c in df.columns if c.endswith("_mean")})

    for feat in features:
        plot_heatmap_for_feature(df, feat, args, result_dir)
if __name__ == "__main__":
    main()
