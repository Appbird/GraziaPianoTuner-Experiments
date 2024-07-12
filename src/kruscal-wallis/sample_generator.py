import pandas as pd
import numpy as np

# サンプルデータを生成してCSVファイルに保存する関数
def generate_sample_data(file_path):
    np.random.seed(0)  # 再現性のためにランダムシードを設定

    # 各グループのデータを生成
    data = {
        'Column1': map(int, np.random.normal(50, 10, 100)),
        'Column2': map(int, np.random.normal(50, 10, 100)),
        'Column3': map(int, np.random.normal(50, 10, 100)),
        'Column4': map(int, np.random.normal(50, 10, 100)),
        'Column5': map(int, np.random.normal(50, 10, 100)),
        'Column6': map(int, np.random.normal(50, 10, 100)),
    }

    df = pd.DataFrame(data)
    df.to_csv(file_path, index=False)
    print(f"サンプルデータを{file_path}に保存しました。")

# サンプルデータのファイルパス
sample_file_path = 'src/kruscal-wallis/sample_data.csv'

# サンプルデータを生成して保存
generate_sample_data(sample_file_path)
