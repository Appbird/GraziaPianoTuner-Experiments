MIN_VALUE = 0
MAX_VALUE = 1


ADJ_LIST    :list[list[str]] = [["中東風"]]
PARAM_LIST  :list[list[float]]  = [
    [ MIN_VALUE ],
    [ (MIN_VALUE + MAX_VALUE) / 2 ]
]

#TODO 元楽曲を読み込ませて編集するようにしちゃう？
def gen_user_prompt(adjs:list[str], values:list[float]):
    assert all(MIN_VALUE <= value <= MAX_VALUE for value in values)
    return f"""
# Input
Please modify the melody of the following song to match the parameters given in the #parameter section.
Feel free to change the chords, key, rhythm, and BPM as necessary.

The range of the parameter is the closed interval from {MIN_VALUE} to {MAX_VALUE}.

The current parameter values for this song are as follows:
- "中東風" = 1.0

```
X: 1
T: Middle Eastern Breeze
M: 4/4
L: 1/4
Q: 1/4=140
K: A minor
V: 1
| "Am" A/B/c/B/ A/G/F/E/ | "E7" ^G/F/E/D/ E/D/C/B/ | "Dm" D/E/F/G/ A/F/E/D/ | "Am" A2 z2 |
| "Am" A/B/c/B/ A/G/F/E/ | "E7" ^G/F/E/D/ E/D/C/B/ | "Dm" D/E/F/G/ A/F/E/D/ | "Am" A2 z2 |
| "F" F/A/c/B/ A/G/F/E/ | "E" E/D/E/^F/ G/^F/E/D/ | "Dm" D/E/F/G/ A/F/E/D/ | "Am" A2 z2 |
| "Dm" D/E/F/G/ A/F/E/D/ | "E7" E/D/^C/B/ A/B/c/B/ | "Am" A/B/c/B/ A/G/F/E/ | "Am" A4 |
```
# parameters
{"\n".join([ f'"{adj}" = {value}' for (adj, value) in zip(adjs, values)])}
"""

if __name__ == "__main__":
    print(gen_user_prompt(["躍動感"], [ 0.50 ]))
    print(gen_user_prompt(["明るさ", "躍動感"], [ 0.50, 0.10 ]))