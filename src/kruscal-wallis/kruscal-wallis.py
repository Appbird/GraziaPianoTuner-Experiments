import pandas as pd
from scipy.stats import kruskal, mannwhitneyu
import numpy as np

# CSVファイルを読み込む
csv_file_path = 'src/kruscal-wallis/questionaires.csv'
# csv_file_path = 'src/kruscal-wallis/sample_data.csv'
df = pd.read_csv(csv_file_path)

# 群と対応するカラムのリストを指定
groups = {
    'Group-A': ['明るさ', "沈んだ"],
    # 'Group-A': ["ジャズ感（1つめ）","ジャズ感（2つめ）"],
    # 'Group-B': [ "スイング感（1つめ）", "スイング感（2つめ）" ],
    # 'Group-B': ["クラシック感（1つめ）", "クラシック感（2つめ）"]
    # 'Group-B': ["勇敢な（1つめ）", "勇敢な（2つめ）", "気まぐれな"]
    "Group-B": ["厳かな", "勇敢な（1つめ）",  "勇敢な（2つめ）", "堂々とした（1つめ）", "堂々とした（2つめ）", "気まぐれな"],

    # 'Group-A': ['Column1', 'Column2'],
    # 'Group-B': ['Column3', 'Column4'],
    # 'Group-C': ['堂々とした（1つめ）', '堂々とした（2つめ）', '静かな']
}
# 春,明るさ,気まぐれな,厳かな,勇敢な（1つめ）,勇敢な（2つめ）,堂々とした（1つめ）,堂々とした（2つめ）,静かな,沈んだ,
# クラシック感（1つめ）,クラシック感（2つめ）,ジャズ感（1つめ）,ジャズ感（2つめ）,スイング感（1つめ）,スイング感（2つめ）

# 各群のデータを結合してリストにまとめる
group_data = {}
for group, columns in groups.items():
    combined_data = []
    for column in columns:
        combined_data.extend(df[column].dropna().tolist())  # 欠損値は除外
    group_data[group] = combined_data

# Kruskal-Wallis検定を実行する
group_values = list(group_data.values())
if len(groups) > 2:
    stat, p_value = kruskal(*group_values)

    print(f"Kruskal-Wallis H-statistic: {stat}")
    print(f"p-value: {p_value}")

    H = stat
    k = len(groups)
    n = sum(len(values) for values in group_values)
    epsilon_sq = (H - k + 1) / (n - k)
    print(f"Effect size (epsilon squared): {epsilon_sq:.4f}")
else:
    # Mann-Whitney U検定を実行する
    group1_data = group_data['Group-A']
    group2_data = group_data['Group-B']
    stat, p_value = mannwhitneyu(group1_data, group2_data)

    print(f"Mann-Whitney U-statistic: {stat}")
    print(f"p-value: {p_value}")

     # 効果量 r = |Z| / sqrt(n)
    n1 = len(group1_data)
    n2 = len(group2_data)
    n = n1 + n2

    # U値からZ値を計算
    mean_U = n1 * n2 / 2
    std_U = np.sqrt(n1 * n2 * (n1 + n2 + 1) / 12)
    z = (stat - mean_U) / std_U
    r = abs(z) / np.sqrt(n)
    print(f"Effect size (r): {r:.4f}")