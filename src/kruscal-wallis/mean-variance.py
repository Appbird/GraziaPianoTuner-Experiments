from numpy import sqrt
import pandas as pd
import pandas as pd

def calculate_mean_and_variance(file_path, *columns):
    """
    指定されたカラムの平均と分散を計算して出力する関数
    
    Parameters:
    file_path (str): CSVファイルのパス
    *columns (str): カラム名
    
    Returns:
    dict: カラム名をキーに持つ平均と分散の辞書
    """
    df = pd.read_csv(file_path)
    
    results = {}
    
    for column in columns:
        mean_value = f"{df[column].mean():.2f}"
        variance_value = f"{sqrt(df[column].var()):.2f}"
        results[column] = {'mean': mean_value, 'sd': variance_value}
    
    return results

def output_results_to_tsv(results, output_file):
    """
    平均と分散の計算結果をTSVファイルに出力する関数
    
    Parameters:
    results (dict): カラム名をキーに持つ平均と分散の辞書
    output_file (str): 出力するTSVファイルのパス
    """
    # 転置されたデータフレームを作成
    df = pd.DataFrame(results).T
    df.index.name = 'Column'
    
    # TSVファイルに保存
    df.to_csv(output_file, sep='\t')

def print_and_save_mean_and_variance(file_path, output_file, *columns):
    """
    指定されたカラムの平均と分散を計算して出力し、結果をTSVファイルに保存する関数
    
    Parameters:
    file_path (str): CSVファイルのパス
    output_file (str): 出力するTSVファイルのパス
    *columns (str): カラム名
    """
    results = calculate_mean_and_variance(file_path, *columns)
    
    for column, stats in results.items():
        print(f"カラム {column} の平均: {stats['mean']}, 標準偏差: {stats['sd']}")
    
    output_results_to_tsv(results, output_file)
# 使用例
file_path = 'src/kruscal-wallis/questionaires-group-means.csv'  # CSVファイルのパスを指定
output_path = 'src/kruscal-wallis/mean-sd.csv'
columns = ['春', '明るさ', '厳かな', '勇敢な', '気まぐれな', '堂々とした', "静かな", "ジャズ感", "スイング感", "クラシック感"]  # カラム名を指定
# output_path = 'src/kruscal-wallis/mean-sd-group.csv'
# columns = ["A", "B", "C"]
print_and_save_mean_and_variance(file_path, output_path, *columns)
