# 必要ライブラリ（あらかじめ入れておいてね〜）
# pip install numpy scipy matplotlib

import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import rankdata, studentized_range

def compute_avg_ranks(data):
    """
    data: N行×k列の行列（各データセットでの各手法のスコア）
          ※スコアが小さいほど良い場合はそのまま、スコアが大きいほど良い場合は -data を渡してね
    return: k要素の平均ランク配列
    """
    # データセットごとにランクをつけて（小さい方がランク1）、平均を返す
    ranks = np.array([rankdata(row) for row in data])
    return ranks.mean(axis=0)

def compute_CD(k, N, alpha=0.05):
    """
    k: 手法の数
    N: データセットの数（Friedman検定に使った繰り返し数）
    alpha: 有意水準
    return: critical difference の値
    """
    # studentized range 分布から q_alpha を取得（自由度∞）
    q = studentized_range.ppf(1-alpha, k, np.inf) / np.sqrt(2)
    return q * np.sqrt(k*(k+1) / (6.0 * N))

def plot_cd(avg_ranks, names, pvals, N, alpha=0.05, title='CD Diagram'):
    """
    avg_ranks: compute_avg_ranks で得た平均ランク（長さ k）  
    names: 手法名のリスト（長さ k）  
    pvals: k×k のペアごとの p 値行列  
    N: データセット数  
    """
    k = len(avg_ranks)
    # ランクが良い順（1 が一番良い）にソート
    idx = np.argsort(avg_ranks)
    ranks = avg_ranks[idx]
    labels = [names[i] for i in idx]
    p = pvals[np.ix_(idx, idx)]
    CD = compute_CD(k, N, alpha)

    fig, ax = plt.subplots(figsize=(10, 2))
    # 軸（平均ランク軸）
    ax.hlines(0, ranks.min()-0.5, ranks.max()+0.5, color='black')
    for x, lbl in zip(ranks, labels):
        ax.plot(x, 0, 'o')
        ax.text(x, 0.1, lbl, rotation=90, va='bottom', ha='center')

    # CD バー（左端から CD 幅分）
    ax.plot([ranks.min(), ranks.min() + CD],
            [0.3, 0.3], lw=2)
    ax.text(ranks.min() + CD/2, 0.4,
            f'CD = {CD:.2f}', ha='center')

    # 非有意差グループをつなぐ
    intervals = []
    for i in range(k):
        for j in range(i+1, k):
            # i〜j までの全ペアが p > alpha なら非有意差グループ
            if np.all(p[i:j+1, i:j+1] > alpha):
                intervals.append((i, j))
    # 含まれる小区間を除去（最大区間だけ残す）
    intervals = [
        iv for iv in intervals
        if not any(iv != other and iv[0] >= other[0] and iv[1] <= other[1]
                   for other in intervals)
    ]
    # 重ならないようにレベル割当
    levels = []
    iv_levels = {}
    for iv in sorted(intervals, key=lambda x: x[1]-x[0], reverse=True):
        for lv, placed in enumerate(levels):
            if all(iv[1] < pj[0] or iv[0] > pj[1] for pj in placed):
                placed.append(iv)
                iv_levels[iv] = lv
                break
        else:
            levels.append([iv])
            iv_levels[iv] = len(levels)-1

    # 描画
    for iv, lv in iv_levels.items():
        i, j = iv
        x1, x2 = ranks[i], ranks[j]
        y = 0.6 + lv * 0.2
        ax.plot([x1, x2], [y, y], lw=2)
        ax.plot([x1, x1], [y-0.02, y], lw=2)
        ax.plot([x2, x2], [y-0.02, y], lw=2)

    ax.set_ylim(-0.5, y + 0.5)
    ax.axis('off')
    plt.title(title)
    plt.show()

# 使い方例〜
# data: N×13 の NumPy 配列（データセット×手法）
# names: 長さ13の手法名リスト
# pvals: 13×13 のペアワイズ p 値行列
# N: データセット数
avg_ranks = compute_avg_ranks(data)
plot_cd(avg_ranks, names, pvals, N)
