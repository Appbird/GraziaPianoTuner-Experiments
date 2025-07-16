import pandas as pd

# 1) CSV を読み込む（ファイル名は適宜変更してね）
df = pd.read_csv('./questionaire/subjective_questionaire.csv')

# 2) 数値だけ入ってる列名を自動検出
#    pandas が読み込んで int/float 型になった列を選ぶ
num_cols = df.select_dtypes(include=['number']).columns.tolist()

# 3) melt で縦長フォーマットに変換
#    reset_index() で元の行番号を「被験者」列に
df_long = (
    df[num_cols]
    .reset_index()                        # index を列に
    .melt(id_vars='index',               # 被験者番号
          var_name='軸名',               # 軸名（列名がここに入る）
          value_name='評価')             # 評価値
    .rename(columns={'index':'被験者'})  # カラム名を「被験者」に
)

# 4) 必要なら被験者番号を 1 始まりにするなら＋1
# df_long['被験者'] += 1

# 5) CSV として出力
df_long.to_csv('long_format.csv', index=False, encoding='utf-8-sig')
