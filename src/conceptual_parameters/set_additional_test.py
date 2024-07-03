MIN_VALUE = 0
MAX_VALUE = 1


ADJ_LIST    :list[list[str]] = [
    ["クラシック"],
    ["スイング感"],
    ["ジャズ感"],
    ["静かな"],
    ["沈んだ"],
    ["静かな"],
]
PARAM_LIST  :list[list[float]]  = [
    [ MIN_VALUE ],
    [ (MIN_VALUE + MAX_VALUE) / 2 ],
    [ MAX_VALUE ]
]

#TODO 元楽曲を読み込ませて編集するようにしちゃう？
def gen_user_prompt(adjs:list[str], values:list[float]):
    assert all(MIN_VALUE <= value <= MAX_VALUE for value in values)
    return f"""
# Input
Firstly, please evaluate the parameter ("{"\",\"".join(adjs)}") on following music, and report it.
Then, please modify the melody of the following music to match the parameters' value given in the #parameter section.
Feel free to change the chords, key, rhythm, and BPM as necessary.

The range of the parameter is the closed interval from {MIN_VALUE} to {MAX_VALUE}.
        
```
X:1
T:Lively Serenade
C:AI Composer
M:4/4
L:1/4
Q:1/4=160
K:D major
V:1
| "D" D2 FA | "A" E2 A2 | "Bm" BFdB | "G" G2 Bd |
| "D" AFdF | "A" EAcA | "G" BdBG | "A" E4 |
| "D" d2 fa | "Bm" bfdb | "G" gdBG | "A" E2 E2 |
| "D" d2 FA | "A" E2 A2 | "G" BdBG | "D" D4 |
| "Bm" B2 dB | "F#m" F2 A2 | "G" G2 Bd | "A" EAcA |
| "G" BdgB | "D" AfdF | "A" E2 E2 | "D" D4 |
```
# parameters
{"\n".join([ f'"{adj}" = {value}' for (adj, value) in zip(adjs, values)])}
"""

if __name__ == "__main__":
    print(gen_user_prompt(["躍動感"], [ 0.50 ]))
    print(gen_user_prompt(["明るさ", "躍動感"], [ 0.50, 0.10 ]))