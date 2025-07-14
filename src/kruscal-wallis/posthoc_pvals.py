from collections import defaultdict
import pandas as pd
import numpy as np
from scipy.stats import friedmanchisquare, rankdata
import scikit_posthocs as sp
import networkx as nx
import matplotlib.pyplot as plt
import japanize_matplotlib
from sklearn.cluster import SpectralClustering
import matplotlib.cm as cm

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
        #"クラシック感（1つめ）", "クラシック感（2つめ）",
        #"ジャズ感（1つめ）", "ジャズ感（2つめ）",
        #"スイング感（1つめ）", "スイング感（2つめ）"
    ]
    cols_en = [
        # 'spring',
        'bright', 'capriccioso', 'solemn',
        'brave1', 'brave2', 'imposing1', 'imposing2',
        'quiet', 'sunk',
        # 'classic1', 'classic2', 'jazz1', 'jazz2', 'swing1', 'swing2'
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
        posthoc_pvals = sp.posthoc_nemenyi_friedman(df2.values)

        # --- 4. 重み付きグラフ G の構築 ---
        G = nx.Graph()
        n = len(cols_en)
        G.add_nodes_from(range(n))
        for i in range(n):
            for j in range(i+1, n):
                G.add_edge(i, j, weight=posthoc_pvals.iloc[i, j])

        # --- 5. スペクトラルクラスタリング ---
        sc = SpectralClustering(
            n_clusters=4,
            affinity='precomputed',
        )
        labels = sc.fit_predict(posthoc_pvals.values)
        for k in range(4):
            members = [cols[i] for i, lbl in enumerate(labels) if lbl == k]
            print(f"Cluster{k+1}: {members}")
        
        # --- 6. グラフ描画 ---
        draw_graph(G, labels, cols_en)
    else:
        print("全体差に有意性なし → Post-hoc未実施")


def draw_graph(G, labels, cols_en):
    """
    G       : networkx の重み付き無向グラフ
    labels  : 各ノードに対するクラスタID のリスト/配列
    cols_en : ノードラベル（英語名）のリスト
    """

    # コミュニティ数と色マップ
    comms = sorted(set(labels))
    cmap = plt.get_cmap('tab10')
    community_colors = {com: cmap(i) for i, com in enumerate(comms)}

    # ノードごとの色リスト
    node_colors = [community_colors[labels[n]] for n in G.nodes()]

    # エッジ幅（p値に比例）
    scale = 5
    edge_widths = [G[u][v]['weight'] * scale for u, v in G.edges()]

    # レイアウト（重みを反映）
    pos = nx.spring_layout(G, weight='weight', seed=0)

    plt.figure(figsize=(7,7))
    # ノード
    nx.draw_networkx_nodes(G, pos,
                           node_color=node_colors,
                           node_size=600)
    # エッジ
    nx.draw_networkx_edges(G, pos,
                           width=edge_widths,
                           alpha=0.7,
                           edge_color='gray')
    # ラベル
    nx.draw_networkx_labels(G, pos,
                            labels={i: cols_en[i] for i in G.nodes()},
                            font_size=10)

    plt.title("スペクトルクラスタリングによるコミュニティ分割", fontsize=14)
    plt.axis('off')
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
