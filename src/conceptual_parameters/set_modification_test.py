MIN_VALUE = 0
MAX_VALUE = 1

MODIFICATION_LIST    :list[tuple[str, str]] = [
    #("darker", "この曲を暗くアレンジして"),
    #("faster", "もう少し曲を早くして"),
    #("arrange-3-4", "3/4拍子にアレンジして"),
    #("rhythm-pattern", "このリズムパターンに沿ってこの曲を演奏して"),
    #("eighth-note", "8分音符の数をもっと増やして"),
    ("fixed-chord", "コードはそのままにして、メロディだけを4/4拍子のメロディに変化させて"),
    ("fixed-ranged-chord", "5小節目から8小節目まで、コードを固定したままメロディだけを4/4拍子のメロディに変化させて。その他はそのままにして。"),
    #("swing-style", "スイングっぽくして")
]

def gen_user_prompt(instruction:str):
    return f"""
# Original Music
Modify the following piece of music to comply with the instructions given in the # Input. 

```abc
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

# Input
{instruction}

"""

if __name__ == "__main__":
    print(gen_user_prompt("コード進行を変えずに、メロディだけ変えて"))
    print(gen_user_prompt("コード進行を変えずに、メロディだけを変えて"))