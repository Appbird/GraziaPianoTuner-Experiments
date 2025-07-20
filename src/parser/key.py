import re
from typing import Optional, TypedDict

class ParsedKey(TypedDict):
    tonic: Optional[str]
    mode: str
    raw_mode_token: Optional[str]
    special: Optional[str]
    has_accidentals: bool
    accidentals: list[str]
    original: str
def dump_parsed_key(key:ParsedKey, indent:int=0):
    print("\t"*indent, end=""); print(f"Mode={str(key["tonic"])+key["mode"]}, is_major ={key["mode"]=="major"}")


_MODE_MAP = {
    "maj": "major",
    "ion": "ionian",
    "min": "minor",
    "aeo": "aeolian",
    "mix": "mixolydian",
    "dor": "dorian",
    "phr": "phrygian",
    "lyd": "lydian",
    "loc": "locrian",
    "exp": "explicit",
}

def _normalize_mode_token(token: str) -> str:
    t = token.strip().lower()
    if t == "":
        return "major"
    if t == "m":
        return "minor"
    if len(t) >= 3:
        key = t[:3]
        if key in _MODE_MAP:
            return _MODE_MAP[key]
    raise ValueError(f"Unknown mode token: '{token}'")

_TONIC_RE = re.compile(r'^[A-Ga-g]([#b])?$')
def _normalize_tonic(token: str) -> str:
    if not _TONIC_RE.match(token):
        raise ValueError(f"Invalid tonic: '{token}'")
    return token[0].upper() + token[1:]

_ACC_RE = re.compile(r'^(?:__|_|=|\^\^|\^)[A-Ga-g]$')

def parse_k_field(k_field_value: str) -> ParsedKey:
    original = k_field_value.strip()

    if original == "" or original.lower() == "none":
        return ParsedKey(tonic=None, mode="none", raw_mode_token=None,
                         special="none", has_accidentals=False,
                         accidentals=[], original=original)

    if original in ("HP", "Hp"):
        return ParsedKey(tonic=None, mode="highland_pipes",
                         raw_mode_token=original, special=f"highland_{original}",
                         has_accidentals=False, accidentals=[], original=original)

    tokens = original.split()
    if not tokens:
        return ParsedKey(tonic=None, mode="none", raw_mode_token=None,
                         special="none", has_accidentals=False,
                         accidentals=[], original=original)

    first_token = tokens[0]

    if first_token.lower().startswith("clef="):
        return ParsedKey(tonic=None, mode="none", raw_mode_token=None,
                         special="clef_only", has_accidentals=False,
                         accidentals=[], original=original)

    # ここで joined 形式 (F#Mix, BbDor, Amin, C#m など) を分離
    m_joined = re.match(r'^([A-Ga-g](?:[#b]?))([A-Za-z]+)?$', first_token)
    if m_joined:
        tonic_token = m_joined.group(1)
        joined_mode_part = m_joined.group(2) or ""
        if joined_mode_part:
            tokens = [tonic_token, joined_mode_part] + tokens[1:]
        else:
            tokens = [tonic_token] + tokens[1:]
    else:
        tonic_token = first_token  # 失敗ならそのまま（普通はここ来ない想定）

    tonic = _normalize_tonic(tonic_token)

    raw_mode_token: Optional[str] = None
    mode = "major"
    special: Optional[str] = None
    accidentals: list[str] = []

    i = 1
    if i < len(tokens):
        candidate = tokens[i]
        low = candidate.lower()
        if low == "exp":
            raw_mode_token = candidate
            mode = "explicit"
            special = "explicit"
            i += 1
        else:
            if not candidate.startswith(("_","^","=")):
                try:
                    mode = _normalize_mode_token(candidate)
                    raw_mode_token = candidate
                    i += 1
                except ValueError:
                    # accidental でない未知トークンなら例外
                    raise

    while i < len(tokens):
        tk = tokens[i]
        if _ACC_RE.match(tk):
            accidentals.append(tk)
        # else: clef= などは無視
        i += 1

    return ParsedKey(
        tonic=tonic,
        mode=mode,
        raw_mode_token=raw_mode_token,
        special=special,
        has_accidentals=bool(accidentals),
        accidentals=accidentals,
        original=original
    )

# テスト
if __name__ == "__main__":
    tests = [
        "C", "C major", "C ionian", "A minor", "A m", "A aeolian",
        "G mixolydian", "D dor", "E phrygian", "F lyd", "B locrian",
        "F#Mix", "BbDor", "Amin", "C#m", "D Phr ^f", "D exp _b _e ^f",
        "none", "", "HP", "Hp", "Bb dor _e", "D =c", "clef=bass"
    ]
    for t in tests:
        print(t, "->", parse_k_field(t))
