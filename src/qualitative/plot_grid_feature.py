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
    ap.add_argument("--feature", required=True, help="例: pitch_entropy")
    ap.add_argument("--out-img", default=None)
    ap.add_argument("--cmap", default="viridis")
    ap.add_argument("--annot", action="store_true", help="各セルに数値表示")
    ap.add_argument("--contour", action="store_true", help="等高線を重ねる")
    ap.add_argument("--dpi", type=int, default=200)
    ap.add_argument("--fmt", default=".2f", help="annot表示フォーマット")
    return ap.parse_args()

def main():
    args = parse_args()
    df = pd.read_csv(args.csv)

    base = f"{args.feature}_mean"
    if base not in df.columns:
        raise ValueError(f"{base} が列に無いよ。利用可能: {[c for c in df.columns if c.endswith('_mean')]}")

    pivot = df.pivot(index="y", columns="x", values=base).sort_index()
    xs = pivot.columns.values
    ys = pivot.index.values
    Z = pivot.values  # shape (len(ys), len(xs))

    out_img = args.out_img or f"{Path(args.csv).stem}_{args.feature}_heatmap.png"

    fig, ax = plt.subplots(figsize=(6,5))
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
    ax.set_title(f"{args.feature} (mean)")

    if args.contour:
        # 等高線（値がほぼ一定なら自動レベル調整）
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
        # グリッド位置をセル座標に合わせて annotation
        # xs, ys は 0.0,0.1,... と均等なので index を使っても良い
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
    print(f"[INFO] Saved heatmap: {out_img}")

if __name__ == "__main__":
    main()
