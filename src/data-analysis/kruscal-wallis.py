import pandas as pd
from scipy.stats import kruskal, mannwhitneyu, wilcoxon
import numpy as np

# CSVファイルを読み込む
csv_file_path = 'data/subjective/questionaires.csv'
# csv_file_path = 'src/kruscal-wallis/sample_data.csv'
df = pd.read_csv(csv_file_path)

# 群と対応するカラムのリストを指定
groups = {
    #'Group-A': ['明るさ', "厳かな"],
    # "Group-B": ["堂々とした2"]
    'Group-A': ["気まぐれな","沈んだ", "堂々とした2", "クラシック感2", "スイング感1"],
    'Group-B': [ "勇敢な1", "勇敢な2", "静かな", "堂々とした1", "ジャズ感1", "ジャズ感2", "クラシック感1", "スイング感2"],
}
# 春,明るさ,気まぐれな,厳かな,勇敢な（1つめ）,勇敢な（2つめ）,堂々とした（1つめ）,堂々とした（2つめ）,静かな,沈んだ,
# クラシック感（1つめ）,クラシック感（2つめ）,ジャズ感（1つめ）,ジャズ感（2つめ）,スイング感（1つめ）,スイング感（2つめ）

# ---- 補助関数たち ----
def wilcoxon_effect_size_r(W, n_nonzero):
    """r = |Z| / sqrt(n) を Wilcoxon の W から計算"""
    mean_W = n_nonzero * (n_nonzero + 1) / 4
    sd_W = np.sqrt(n_nonzero * (n_nonzero + 1) * (2 * n_nonzero + 1) / 24)
    z = (W - mean_W) / sd_W
    r = abs(z) / np.sqrt(n_nonzero)
    return r, z

def try_wilcoxon_if_paired(df, groups):
    """条件を満たせば Wilcoxon を実行して結果を返す。満たさなければ None を返す。"""
    if len(groups) != 2:
        return None  # 2群じゃない

    # 各群が1列だけか？
    if not all(len(cols) == 1 for cols in groups.values()):
        return None

    colA = groups['Group-A'][0]
    colB = groups['Group-B'][0]

    sA = df[colA]
    sB = df[colB]

    # 対応を取るため、両方Non-NaNの行だけ残す
    mask = sA.notna() & sB.notna()
    x = sA[mask].to_numpy()
    y = sB[mask].to_numpy()

    # サイズが同じならペアOK（基本的に同じはずだけど念のため）
    if len(x) == 0 or len(x) != len(y):
        return None

    # 差が全部0だとwilcoxonできないのでチェック
    diff = x - y
    nonzero_mask = diff != 0
    if nonzero_mask.sum() == 0:
        return {'stat': np.nan, 'p': 1.0, 'r': 0.0, 'test': 'wilcoxon', 'note': 'all differences were 0'}

    # Wilcoxon 符号付順位検定
    W, p = wilcoxon(x, y, zero_method='pratt', correction=False, alternative='two-sided')

    # 効果量 r
    r, z = wilcoxon_effect_size_r(W, nonzero_mask.sum())

    return {'stat': W, 'p': p, 'r': r, 'z': z, 'n': nonzero_mask.sum(), 'test': 'wilcoxon', 'note': ''}

# ---- メイン処理 ----
# まず Wilcoxon 条件を満たすか試す
wilcox_result = try_wilcoxon_if_paired(df, groups)

if wilcox_result is not None:
    print("### Wilcoxon signed-rank test ###")
    print(f"W-statistic: {wilcox_result['stat']}")
    print(f"p-value    : {wilcox_result['p']}")
    print(f"r (|Z|/√n) : {wilcox_result['r']:.4f}")
    print(f"Z          : {wilcox_result['z']:.3f}")
    print(f"n (nonzero diffs): {wilcox_result['n']}")
    if wilcox_result['note']:
        print(f"Note       : {wilcox_result['note']}")
else:
    # それ以外は今まで通りの処理
    # 各群データをまとめる（注意：Wilcoxonの条件を満たさないので合算でOK）
    group_data = {}
    for group, columns in groups.items():
        combined = []
        for column in columns:
            combined.extend(df[column].dropna().tolist())
        group_data[group] = combined

    group_values = list(group_data.values())

    if len(groups) > 2:
        # Kruskal-Wallis
        stat, p_value = kruskal(*group_values)
        print("### Kruskal–Wallis test ###")
        print(f"H-statistic: {stat}")
        print(f"p-value    : {p_value}")
        H = stat
        k = len(groups)
        n = sum(len(v) for v in group_values)
        eps2 = (H - k + 1) / (n - k)
        print(f"epsilon^2  : {eps2:.4f}")
    else:
        # Mann–Whitney
        g1 = group_data['Group-A']
        g2 = group_data['Group-B']
        stat, p_value = mannwhitneyu(g1, g2, alternative='two-sided')
        print("### Mann–Whitney U test ###")
        print(f"U-statistic: {stat}")
        print(f"p-value    : {p_value}")

        n1, n2 = len(g1), len(g2)
        mean_U = n1 * n2 / 2
        std_U = np.sqrt(n1 * n2 * (n1 + n2 + 1) / 12)
        z = (stat - mean_U) / std_U
        r = abs(z) / np.sqrt(n1 + n2)
        print(f"r (|Z|/√N) : {r:.4f}")