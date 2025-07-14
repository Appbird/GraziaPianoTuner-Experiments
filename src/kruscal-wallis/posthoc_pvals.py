from collections import defaultdict
import itertools
import pandas as pd
import numpy as np
from scipy.stats import friedmanchisquare
import scikit_posthocs as sp
import networkx as nx
import matplotlib.pyplot as plt
import japanize_matplotlib
import matplotlib.colors as mcolors
from sklearn.cluster import SpectralClustering
import matplotlib.cm as cm
import pingouin as pg

def main():
    # --- 1. データ読み込み & 列抽出 ---
    csv_file_path = 'src/kruscal-wallis/questionaires.csv'
    df = pd.read_csv(csv_file_path)

    cols = [
        # '春',
        '明るさ', '気まぐれな', '厳かな',
        '勇敢な（1つめ）', '勇敢な（2つめ）',
        '堂々とした（1つめ）', '堂々とした（2つめ）',
        '静かな', '沈んだ',
        # "クラシック感（1つめ）", "クラシック感（2つめ）", "ジャズ感（1つめ）", "ジャズ感（2つめ）", "スイング感（1つめ）", "スイング感（2つめ）"
    ]
    cols_en = [
        # 'spring',
        'bright', 'capriccioso', 'solemn',
        'brave1', 'brave2', 'imposing1', 'imposing2',
        'quiet', 'sunk',
        #'classic1', 'classic2', 'jazz1', 'jazz2', 'swing1', 'swing2'
    ]
    df2 = df[cols].copy().dropna()

    # --- 2. Friedman検定 ---
    stat, p_all = friedmanchisquare(*[df2[c] for c in cols])
    print(f"Friedman検定：chi2 = {stat:.3f}, p = {p_all}")
    N, k = df2.shape[0], len(cols)
    print(N, k)
    epsilon2 = (stat)/(N*(k-1))
    print(f"効果量: {epsilon2}")
    

    if p_all < 0.05:
        # --- 3. Nemenyi Post-hoc で p 値行列取得 ---
        n = df2.shape[1]
        effsize = pd.DataFrame(np.nan, index=range(n), columns=range(n))
        p_values = pd.DataFrame(np.nan, index=range(n), columns=range(n))

        for i in range(n):
            effsize.at[i, i] = 0
            p_values.at[i, i] = 1
        for i, j in itertools.combinations(range(n), 2):
            # Wilcoxon の符号付き順位検定で RBC を計算
            res = pg.wilcoxon(
                df2.values[:, i],
                df2.values[:, j],
                alternative='two-sided'
            )
            rbc = res['RBC'].values[0]
            p_value = res['p-val'].values[0]
            effsize.at[i, j], effsize.at[j, i] = rbc, -rbc
            p_values.at[i, j], p_values.at[j, i] = p_value, p_value
        smilarity = 1-abs(effsize)
        # --- 4. 重み付きグラフ G の構築 ---
        G = nx.DiGraph()
        n = len(cols_en)
        G.add_nodes_from(range(n))
        for i in range(n):
            for j in range(i+1, n):
                rbc = effsize.at[i, j]
                sim = smilarity.at[i, j]
                if sim < 0.5: continue
                if rbc > 0:
                    G.add_edge(j, i, weight=sim, p_value=p_values.at[i, j])

        # --- 5. スペクトラルクラスタリング ---
        sc = SpectralClustering(
            n_clusters=4,
            affinity='precomputed',
            random_state=10
        )
        labels = sc.fit_predict(smilarity.values)
        for k in range(4):
            members = [cols[i] for i, lbl in enumerate(labels) if lbl == k]
            print(f"Cluster{k+1}: {members}")
        
        # --- 6. グラフ描画 ---
        draw_directed_graph(G, labels, cols_en)
    else:
        print("全体差に有意性なし → Post-hoc未実施")


def draw_directed_graph(G, labels, cols_en):
    """
    G       : networkx の有向グラフ ('weight' 属性のみを使用)
    labels  : 各ノードに対するクラスタID のリスト/配列
    cols_en : ノードラベル（英語名）のリスト
    """

    # 1) Figure と Axes
    fig, ax = plt.subplots(figsize=(7,7))

    # 2) ノードカラー設定（コミュニティ別）
    comms = sorted(set(labels))
    cmap_nodes = plt.get_cmap('tab10')
    community_colors = {com: cmap_nodes(i) for i, com in enumerate(comms)}
    node_colors = [community_colors[labels[n]] for n in G.nodes()]

    # 3) エッジ幅（効果量）と濃さ（グレースケール）設定
    weights = [G[u][v]['weight'] for u, v in G.edges()]
    scale = 5
    edge_widths = [w * scale for w in weights]

    norm = mcolors.Normalize(vmin=0, vmax=1)
    cmap_edges = plt.get_cmap('Greys')
    edge_colors = [cmap_edges(norm(w)) for w in weights]

    # 4) レイアウト計算
    pos = nx.spring_layout(G, weight='weight', seed=0)

    # 5) ノード描画
    nx.draw_networkx_nodes(G, pos, ax=ax,
                           node_color=node_colors,
                           node_size=600,
                           edgecolors='black')

    # 6) エッジ（矢印）描画：色で濃淡、幅で太さを表現
    nx.draw_networkx_edges(G, pos, ax=ax,
                           arrowstyle='->',
                           arrowsize=12,
                           width=edge_widths,
                           edge_color=edge_colors,
                           connectionstyle='arc3,rad=0.1')
    # 7) ノードラベル描画
    nx.draw_networkx_labels(G, pos, ax=ax,
                            labels={i: cols_en[i] for i in G.nodes()},
                            font_size=10)
    
    # 8) カラーバー追加（Greyscale for weight）
    sm = plt.cm.ScalarMappable(cmap=cmap_edges, norm=norm)
    sm.set_array([])  # 空の配列をセット
    cbar = fig.colorbar(sm, ax=ax, shrink=0.7)
    cbar.set_label('群の間の類似度', rotation=270, labelpad=15)

    ax.set_title("Directed Graph: Edge Thickness & Darkness with Legend", fontsize=14)
    ax.axis('off')
    plt.tight_layout()
    plt.show()
if __name__ == "__main__":
    main()
