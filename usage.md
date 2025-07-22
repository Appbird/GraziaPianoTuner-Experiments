# 概念パラメータによる楽曲制御の統計的調査
```
python3 ./src/qualitative_test.py -n 5 --axes-file data/qualitative/small_axes.txt --cache-dir CACHE_DIR
```

# 二軸での楽曲制作とその統計的解析
```
python3 ./src/qualitative_grid_sample.py --axes 明るさ 暗さ
python3 ./src/qualitative_grid_plot.py --csv data/qualitative_grid/grid_features.csv  --feature ioi_entropy --out-img ./data/qualitative_grid/a.png
```
# 既知の問題
- ./src/qualitative_test.pyについて、すでに生成を終えているフォルダで、jsonファイルに欠けがあるものに楽曲生成した分は異様にr値が低くなる。
    - jsonファイル自体がある場合に再生成を行ってもr値は低くならない
    - 何かregenerationの挙動にバグがある？