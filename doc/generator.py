# 対応表を辞書形式で定義
mapping = {
    "春": "spring",
    "明るさ": "brightness",
    "厳かな": "solemn",
    "気まぐれな": "capricious",
    "勇敢な(case 1)": "brave1",
    "勇敢な(case 2)": "brave2",
    "堂々とした(case 1)": "dignified1",
    "堂々とした(case 2)": "dignified2",
    "静かな": "quiet",
    "沈んだ": "sank",
    "クラシック感(case 1)": "classic1",
    "クラシック感(case 2)": "classic2",
    "ジャズ感(case 1)": "jazz1",
    "ジャズ感(case 2)": "jazz2",
    "スイング感(case 1)": "swing1",
    "スイング感(case 2)": "swing2"
}

# HTML出力ファイル
output_file = "music_table.html"

# HTMLヘッダー
html_content = """
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>音楽ファイル対応表</title>
</head>
<body>
    <h1>音楽ファイル対応表</h1>
    <table class="u-full-width">
        <thead>
            <tr>
                <th>軸の名前</th>
                <th>0</th>
                <th>0.5</th>
                <th>1</th>
            </tr>
        </thead>
        <tbody>
"""

# 各軸に対して行を生成
for axis_name, file_name in mapping.items():
    html_content += f"""
        <tr>
            <td><code>{axis_name}</code></td>
            <td>
                <audio controls>
                    <source src="music/{file_name}-00.mp3" type="audio/mpeg">
                </audio>
            </td>
            <td>
                <audio controls>
                    <source src="music/{file_name}-05.mp3" type="audio/mpeg">
                </audio>
            </td>
            <td>
                <audio controls>
                    <source src="music/{file_name}-10.mp3" type="audio/mpeg">
                </audio>
            </td>
        </tr>
    """

# HTMLフッター
html_content += """
        </tbody>
    </table>
</body>
</html>
"""

# HTMLファイルに書き出し
with open(output_file, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"HTMLファイルが作成されました: {output_file}")
