MIN_VALUE = 0
MAX_VALUE = 1

# その他
other = [
    ["躍動感"],
    ["なめらかさ"],
    ["癒し"],
    ["神秘さ"],
    ["ダイナミクスさ"]
]

ADJ_LIST    :list[list[str]] = [["ノンダイアトニックコード"]]
PARAM_LIST  :list[list[float]]  = [
    [ MIN_VALUE ],
    [ (MIN_VALUE + MAX_VALUE) / 2 ],
    [ MAX_VALUE ]
]

#TODO 元楽曲を読み込ませて編集するようにしちゃう？
def gen_user_prompt(adjs:list[str], values:list[float]):
    assert all(MIN_VALUE <= value <= MAX_VALUE for value in values)
    return f"""
# parameters
The range of the parameter is the closed interval from {MIN_VALUE} to {MAX_VALUE}.
{"\n".join([ f'"{adj}" = {value}' for (adj, value) in zip(adjs, values)])}
"""

if __name__ == "__main__":
    print(gen_user_prompt(["躍動感"], [ 0.50 ]))
    print(gen_user_prompt(["明るさ", "躍動感"], [ 0.50, 0.10 ]))