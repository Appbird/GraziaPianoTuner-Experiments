MIN_VALUE = 0
MAX_VALUE = 1
# 音楽作品の感情価測定尺度の作成および多面的感情状態尺度との関連の検討
emotional_scale = [
    ["明るさ"],
    ["沈んだ"],
    ["優しさ"],
    ["静かさ"],
    ["優しさ"],
    ["恋しさ"],
    ["強さ"],
    ["猛烈な"],
    ["刺激的な"],
    ["勇敢な"],
    ["堂々とした"],
    ["気まぐれな"],
    ["浮かれた"],
    ["厳粛な"],
    ["おごそかな"]
]

# 概念系
conceptual_scale = [
    ["刺激的な"],
    ["のどかさ"],
    ["連弾度合い"],
    ["レゲエ"],
    ["クラシック感"],
    ["ジャズ感"],
    ["スイング感"],
    ["ワルツ感"],
    ["ロック"],
    ["ベース"],
    ["春"],
    ["夏"],
    ["秋"],
    ["冬"]
]

# その他
other = [
    ["躍動感"],
    ["なめらかさ"],
    ["癒し"],
    ["神秘さ"],
    ["ダイナミクスさ"]
]

ADJ_LIST    :list[list[str]] = emotional_scale + conceptual_scale + other
PARAM_LIST  :list[list[float]]  = [
    [ MIN_VALUE ],
    [ (MIN_VALUE + MAX_VALUE) / 2 ],
    [ MAX_VALUE ]
]

INITIAL_SCORE = """X: 1
T: Breezy Afternoon
M: 4/4
L: 1/4
Q: 1/4=140
K: G major
V:1
| "G" G2 D2 | "Em" E2 B2 | "Am" A2 C2 | "D7" D2 A2 |
| "G" GBAG | "C" CDEF | "G" G2 B2 | "D7" D2 A2 |
| "C" ED E2 | "G/B" GB d2 | "A7" cA A2 | "Am7" A2 E2 |
| "G" G2 D2 | "D7" D2 A2 | "G" GG B2 | "D7" A3 D |
| "G" GBAG | "C" CDEF | "G" G2 B2 | "D7" D2 A2 |
| "G" G2 D2 | "Em" E2 B2 | "Am" A2 C2 | "D7" D2 A2 |
"""

#TODO 元楽曲を読み込ませて編集するようにしちゃう？
def gen_user_prompt(adjs:list[str], values:list[float]):
    assert all(MIN_VALUE <= value <= MAX_VALUE for value in values)
    return f"""
# Input
Please follow the conceptual parameters indicated in section #parameters to edit and arrange the following music tracks.
```
{INITIAL_SCORE}
```

# parameters
The range of the parameter is the closed interval from {MIN_VALUE} to {MAX_VALUE}.
{"\n".join([ f'"{adj}" = {value}' for (adj, value) in zip(adjs, values)])}
"""

if __name__ == "__main__":
    print(gen_user_prompt(["躍動感"], [ 0.50 ]))
    print(gen_user_prompt(["明るさ", "躍動感"], [ 0.50, 0.10 ]))