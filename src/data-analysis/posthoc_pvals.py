from collections import defaultdict
import pandas as pd
import numpy as np
from scipy.stats import friedmanchisquare, rankdata, wilcoxon
import scikit_posthocs as sp
import matplotlib.pyplot as plt
import japanize_matplotlib
import seaborn as sns  # 追加
from statsmodels.stats.libqsturng import qsturng  # CD計算用（必要なら）
# import networkx as nx ...（グラフ不要なら省略でOK）

def compute_avg_ranks(data):
    ranks = np.array([rankdata(row) for row in data])
    return ranks.mean(axis=0)

def wilcoxon_r(x, y):
    """対応あり2群用 r を返す (|Z|/sqrt(n_nonzero))"""
    # NaN除去
    mask = (~np.isnan(x)) & (~np.isnan(y))
    x, y = x[mask], y[mask]
    diff = x - y
    nz = np.count_nonzero(diff)  # 非ゼロ差のみ使う
    if nz == 0:
        return np.nan  # 全部同点ならr定義できない
    W, p = wilcoxon(x, y, zero_method='pratt', alternative='two-sided', correction=False)
    # Zを手計算
    mean_W = nz * (nz + 1) / 4
    sd_W = np.sqrt(nz * (nz + 1) * (2 * nz + 1) / 24)
    z = (W - mean_W) / sd_W
    r = abs(z) / np.sqrt(nz)
    return r

def main():
    csv_file_path = 'data/subjective/questionaires.csv'
    df = pd.read_csv(csv_file_path)

    cols = [
        # '春',
        '明るさ', '気まぐれな', '厳かな',
        '勇敢な1', '勇敢な2',
        '堂々とした1', '堂々とした2',
        '静かな', '沈んだ',
        "クラシック感1", "クラシック感2",
        "ジャズ感1", "ジャズ感2",
        "スイング感1", "スイング感2"
    ]
    cols_en = [
        # 'spring',
        'bright', 'capriccioso', 'solemn',
        'brave1', 'brave2', 'imposing1', 'imposing2',
        'quiet', 'sunk',
        'classic1', 'classic2', 'jazz1', 'jazz2', 'swing1', 'swing2'
    ]

    df2 = df[cols].copy().dropna()

    # --- Friedman ---
    stat, p_all = friedmanchisquare(*[df2[c] for c in cols])
    N, k = df2.shape
    epsilon2 = stat / (N * (k - 1))
    print(f"Friedman: chi2={stat:.3f}, p={p_all:.3g}, epsilon^2={epsilon2:.3f}")

    if p_all >= 0.05:
        print("全体差なし → ここで終了（または探索的に進めるなら進める）")
        return

    # --- Posthoc (Nemenyi) p行列 ---
    posthoc_pvals = sp.posthoc_nemenyi_friedman(df2.values)
    posthoc_pvals.index = cols
    posthoc_pvals.columns = cols

    # --- r行列（Wilcoxon符号付） ---
    rmat = pd.DataFrame(np.nan, index=cols, columns=cols)
    for i, c1 in enumerate(cols):
        for j, c2 in enumerate(cols):
            if i >= j:  # 下三角だけ計算してコピーでOK
                continue
            r = wilcoxon_r(df2[c1].values, df2[c2].values)
            rmat.loc[c1, c2] = r
            rmat.loc[c2, c1] = r

    # --- CD 図順（平均順位順） ---
    avg_ranks = compute_avg_ranks(df2.values)  # 小さいほど良いならこのまま
    order_idx = np.argsort(avg_ranks)          # CD図と同じ並べ方にしたいならこれで
    ordered_cols = [cols[i] for i in order_idx]

    # 並べ替え
    pmat_ord = posthoc_pvals.loc[ordered_cols, ordered_cols]
    rmat_ord = rmat.loc[ordered_cols, ordered_cols]

    # --- ヒートマップ描画 ---
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    # p値ヒートマップ（-log10にしてもよい）
    mask = np.triu(np.ones_like(pmat_ord, dtype=bool))
    sns.heatmap(pmat_ord, mask=mask, ax=axes[0], annot=True, fmt=".2f",
                cmap="Blues_r", cbar_kws={"label":"p-value"})
    axes[0].set_title("補正済みp値 (Nemenyi)")
    axes[0].tick_params(axis='x', labelrotation=45)
    plt.setp(axes[0].get_xticklabels(), ha='right')

    # rヒートマップ（|r|推奨）
    sns.heatmap(rmat_ord.abs(), mask=mask, ax=axes[1], annot=True, fmt=".2f",
                cmap="magma", vmin=0, vmax=1, cbar_kws={"label":"|r|"})
    axes[1].set_title("Rosenthalの効果量r")
    axes[1].tick_params(axis='x', labelrotation=45)
    plt.setp(axes[1].get_xticklabels(), ha='right')

    plt.tight_layout()
    plt.show()

    # --- もしCD図も描きたいならここでavg_ranksとCD計算して別途描画 ---
    # 例:
    # q_alpha = qsturng(0.95, k, np.inf)  # α=0.05
    # CD = q_alpha * np.sqrt(k*(k+1)/(6*N))
    # cd_plot(avg_ranks, CD, labels=cols_en)  # 自作関数で

if __name__ == "__main__":
    main()
