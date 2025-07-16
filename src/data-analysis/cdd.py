import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from scipy.stats import rankdata, studentized_range
from scipy.stats import friedmanchisquare, rankdata
import scikit_posthocs as sp
import japanize_matplotlib
from adjustText import adjust_text

def compute_avg_ranks(data):
    """
    data: N行×k列の行列（各データセットでの各手法のスコア）
          ※スコアが小さいほど良い場合はそのまま、スコアが大きいほど良い場合は -data を渡してね
    return: k要素の平均ランク配列
    """
    # データセットごとにランクをつけて（小さい方がランク1）、平均を返す
    ranks = np.array([rankdata(row) for row in data])
    return ranks.mean(axis=0)

def compute_CD(k, N, alpha=0.01):
    """
    k: 手法の数
    N: データセットの数（Friedman検定に使った繰り返し数）
    alpha: 有意水準
    return: critical difference の値
    """
    # studentized range 分布から q_alpha を取得（自由度∞）
    q = studentized_range.ppf(1-alpha, k, np.inf) / np.sqrt(2)
    return q * np.sqrt(k*(k+1) / (6.0 * N))
def plot_cd(
    avg_ranks, names, pvals, N,
    alpha=0.05, title='CD Diagram'
):
    k = len(avg_ranks)
    idx = np.argsort(avg_ranks)
    ranks = avg_ranks[idx]
    labels = [names[i] for i in idx]
    p_arr = (pvals.values if hasattr(pvals, 'values') else np.array(pvals))
    p = p_arr[np.ix_(idx, idx)]
    CD = compute_CD(k, N, alpha)

    fig, ax = plt.subplots(figsize=(10, 3))
    # -- 中央軸 --
    ax.hlines(0, ranks.min()-0.5, ranks.max()+0.5, color='black')
    # 目盛りにする
    tick_positions = np.arange(int(round(ranks.min())), int(round(ranks.max()+1)))
    tick_length = 0.05  # 目盛りの長さ（上下の幅）
    for tp in tick_positions:
        # 短い縦線 (tick)
        ax.plot([tp, tp], [-tick_length, +tick_length], color='black', lw=1)
        # ラベル
        ax.text(tp, -tick_length - 0.02, str(tp),
                ha='center', va='top', fontsize=10)

    # -- CDバーを上側に --
    cd_y = 0.6  # ← プラス値にして上に配置
    x_start, x_end = ranks.min(), ranks.min() + CD
    ax.plot([x_start, x_end], [cd_y, cd_y], lw=2, color="mediumseagreen")
    # 両端の縦線
    ax.plot([x_start, x_start], [cd_y-0.02, cd_y], lw=2, color="mediumseagreen")
    ax.plot([x_end,   x_end],   [cd_y-0.02, cd_y], lw=2, color="mediumseagreen")
    ax.text((x_start + x_end)/2, cd_y + 0.05,
            f'CD = {CD:.2f}', ha='center')

    # -- 手法を点でプロット --
    for x in ranks:
        ax.plot(x, 0, 'o', markersize=8)

    # 非有意差グループ線
    intervals = []
    for i in range(k):
        for j in range(i+1, k):
            if np.all(p[i:j+1, i:j+1] > alpha):
                intervals.append((i, j))
    intervals = [
        iv for iv in intervals
        if not any(iv != other and iv[0] >= other[0] and iv[1] <= other[1]
                   for other in intervals)
    ]
    levels = []; iv_levels = {}
    for iv in sorted(intervals, key=lambda x: x[1]-x[0], reverse=True):
        for lv, placed in enumerate(levels):
            if all(iv[1] < pj[0] or iv[0] > pj[1] for pj in placed):
                placed.append(iv); iv_levels[iv] = lv; break
        else:
            levels.append([iv]); iv_levels[iv] = len(levels)-1

    for iv, lv in iv_levels.items():
        i, j = iv
        x1, x2 = ranks[i], ranks[j]
        y = 0.1 + lv * 0.1
        # 横線
        ax.plot([x1, x2], [y, y],
                lw=2, color='gray')            # ← 線色をライトグレーに
        # 両端の縦線
        ax.plot([x1, x1], [y-0.02, y],
                lw=2, color='gray')
        ax.plot([x2, x2], [y-0.02, y],
                lw=2, color='gray')

    # -- ラベルも下側に --
    texts:list = []
    prev_x = ranks[-1]*2
    bound = 0.13
    for i, (x, lbl) in enumerate(zip(ranks, labels)):
        if abs(x - prev_x) < bound:
            print("a")
            old_lbl = texts[-1].get_text()
            texts[-1].remove()
            texts[-1] = ax.text((prev_x+x)/2, -0.4, old_lbl+"/"+lbl, rotation=45, va = 'center', ha='right')
            continue
        else:
            t = ax.text(x, -0.4, lbl, rotation=45, va='center', ha='right')
            texts.append(t)
        prev_x = x
        

    ax.set_ylim(-1.0, cd_y+0.2)  # 上限をCDバーが見えるように調整
    ax.axis('off')
    plt.title(title)
    plt.show()
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def plot_boxplots(data: pd.DataFrame, names, title='Score Distributions (Sorted by Mean)'):
    """
    箱ひげ図を平均点の高さ順（高い→低い）に並び替えて描画します。
    data: N×k の pandas.DataFrame
    names: 手法名リスト（長さ k）
    """
    # 1) 各軸（列）の平均点を計算（NaN は自動で無視）
    means = data.mean(axis=0).values
    # 2) 平均点の降順ソート用インデックス
    order = np.argsort(means)[::-1]

    # 3) データと名前をソート
    #    dropna() で箱ひげ図用に NaN を除外してから ndarray に
    data_sorted = [
        data.iloc[:, i].dropna().values
        for i in order
    ]
    names_sorted = [names[i] for i in order]

    # 4) 箱ひげ図を描画
    fig, ax = plt.subplots(figsize=(10, 6))
    bp = ax.boxplot(
        data_sorted,
        tick_labels=names_sorted,
        patch_artist=True,
        showmeans=True,
        meanprops={
            'marker': 'D',
            'markerfacecolor': 'white',
            'markeredgecolor': 'black'
        }
    )
    # 箱の色を薄いブルーに設定
    for box in bp['boxes']:
        box.set(facecolor='lightblue', alpha=0.7)

    ax.set_title(title)
    ax.set_ylabel('評価値')
    ax.set_xlabel('軸（平均点の高い順）')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.show()


def main():
    # --- 1. データ読み込み & 列抽出 ---
    csv_file_path = 'questionaire/subjective_questionaire.csv'
    df = pd.read_csv(csv_file_path)

    cols = [
        # '春',
        '明るさ', '気まぐれな', '厳かな',
        '勇敢な1', '勇敢な2',
        '堂々とした1', '堂々とした2',
        '静かな', '沈んだ',
        "クラシック感1", "クラシック感2", "ジャズ感1", "ジャズ感2", "スイング感1", "スイング感2"
    ]
    df = df[cols]
    plot_boxplots(df, cols, title='')
    # --- 2. Friedman検定 ---
    df = df.dropna()
    stat, p_all = friedmanchisquare(*[df[c] for c in cols])
    print(f"Friedman検定：chi2 = {stat:.3f}, p = {p_all}")
    N, k = df.shape[0], len(cols)
    print(N, k)
    epsilon2 = (stat)/(N*(k-1))
    print(f"効果量: {epsilon2}")
    posthoc_pvals = sp.posthoc_nemenyi_friedman(df.values)
    avg_ranks = compute_avg_ranks(df.values)
    plot_cd(avg_ranks, cols, posthoc_pvals.values, N)

if __name__ == "__main__":
    main()
