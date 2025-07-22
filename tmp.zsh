# リネーム用関数を定義〜
function rename_json_offset() {
  # 第1引数を対象ディレクトリ（なければ ./P）
  local target_dir=${1:-./P}
  # 第2引数をオフセット値（なければ 0）
  local offset=${2:-0}

  # ディレクトリ末尾のスラッシュを外してglob用に整形
  target_dir=${target_dir%/}

  # 数字+.json をループ〜
  for f in "${target_dir}"/<->.json; do
    # ファイル名だけ取り出して拡張子除去（例: "12.json" → "12"）
    local num=${f:t:r}
    # 新しい数字を計算
    local new_num=$(( num + offset ))
    # リネーム実行！
    mv -- "$f" "${target_dir}/${new_num}.json"
  done
}


# JSON ファイルを別ディレクトリにまとめて移動する関数〜
move_json_dir() {
  # 第1引数: 移動元ディレクトリ（省略時は ./P）
  local src_dir=${1:-./P}
  # 第2引数: 移動先ディレクトリ（省略時は ./Q）
  local dst_dir=${2:-./Q}

  # ディレクトリ末尾のスラッシュを除去
  src_dir=${src_dir%/}
  dst_dir=${dst_dir%/}

  # 移動先がなければ作成〜
  mkdir -p "$dst_dir"

  # JSON ファイルをループして mv！
  for f in "${src_dir}"/*.json; do
    # 同名ファイルを移動先に
    mv -- "$f" "${dst_dir}/${f:t}"
  done

  echo "✅ ${src_dir}/*.json を ${dst_dir}/ に移動したよ〜！"
}