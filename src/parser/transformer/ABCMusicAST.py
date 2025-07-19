from fractions import Fraction
from typing import List
from lark import Token, Transformer, Tree, v_args

from parser.ast.chord.chord_symbol import ChordSymbol
from parser.ast.header import HeaderLine
from parser.ast.measure import Measure
from parser.ast.primitive.duration import Duration
from parser.ast.score import Line, Score
from parser.ast.primitive.note import Note, Rest
from parser.transformer.melody_note import compute_midi
from parser.util import normalize_accidental_symbol



@v_args(inline=True)
class ABCMusicAST(Transformer):
    # ---- start / line ----
    def start(self, *lines):
        return Score([l for l in lines if l is not None])

    def line(self, content=None):
        if content is None:
            return None
        if isinstance(content, HeaderLine):
            return Line(header=content)
        # measures_line returns list[Measure]
        return Line(measures=content)

    # ---- Header ----
    def header_line(self, field_tok, value_tok=None):
        field = field_tok.value
        value = value_tok.value.strip() if value_tok else None
        return HeaderLine(field, value)

    # ---- Measures line ----
    def measures_line(self, *children):
        measures = [c for c in children if isinstance(c, Measure)]
        return measures

    def measure(self, *elems):
        return Measure(list(elems))

    # ---- Note / Rest ----
    def note_raw(self, *parts):
        # ACC? PITCH OCT? duration?
        i = 0
        acc = None
        if i < len(parts) and isinstance(parts[i], Token) and parts[i].type == "ACC":
            acc = parts[i].value; i += 1
        pitch = parts[i].value; i += 1
        octave_marks = None
        if i < len(parts) and isinstance(parts[i], Token) and parts[i].type == "OCT":
            octave_marks = parts[i].value; i += 1
        duration = parts[i] if i < len(parts) else None
        midi = compute_midi(acc, pitch, octave_marks)
        return Note(acc, pitch, octave_marks, duration, midi)

    def rest_raw(self, duration=None):
        return Rest(duration)

    # ---- Duration parts ----
    def duration(self, *parts:Duration):
        f = Fraction(1)
        for p in parts:
            f *= p.f
        return Duration(f)

    def part_frac_full(self, num, _slash, den):
        return Duration(Fraction(int(num.value), int(den.value)))

    def part_frac_missing_den(self, num, _slash):
        return Duration(Fraction(int(num.value), 2))

    def part_frac_missing_num(self, _slash, den):
        return Duration(Fraction(1, int(den.value)))

    def part_int(self, num):
        return Duration(Fraction(int(num.value)))

    def part_slashes(self, slash_token):
        c = len(slash_token.value)
        return Duration(Fraction(1, 2**c))

    # ---- Broken Pair ----
    def broken(self, left, op_tok, right):
        return BrokenPair(left, op_tok.value, right)

    # ---- Chord symbols ----
    def chord(self, _open, body, _close):
        # body already ChordSymbol
        return body

    def chord_body(self, core, *alts):
        core.alternates = list(alts)
        # reconstruct text (primary + each alt)
        alt_txt = ''.join(f'({a.text})' for a in alts)
        core.text = core.text + alt_txt
        return core

    def chord_alt(self, _lp, core, _rp):
        return core

    def chord_core(self, root, ctype=None, bass=None):
        # root_tree: chord_root -> (NOTE_LETTER, ACC?)
        raw_types: List[str] = []
        if ctype:
            # chord_type -> CHORD_TYPE_TOKEN+
            raw_types = [tok.value for tok in ctype.children]

        bass_txt = None
        if bass:
            # slash_bass: "/" bass_note
            bnode = bass.children[1]  # bass_note
            bnote = bnode.children[0].value
            bacc = bnode.children[1].value if len(bnode.children) > 1 else ''
            bacc = normalize_accidental_symbol(bacc)
            bass_txt = bnote.upper() + bacc  # case-insensitive spec

        text = root
        if raw_types:
            text += ''.join(raw_types)
        if bass_txt:
            text += '/' + bass_txt
        return ChordSymbol(root=root, raw_types=raw_types, bass=bass_txt, text=text)

    # passthrough simple nodes
    def chord_root(self, *tokens):
        root_note = tokens[0].value
        root_acc = tokens[1].value if len(tokens) > 1 else ''
        root_acc = normalize_accidental_symbol(root_acc)
        root = root_note + root_acc
        return root
    def chord_type(self, *tokens): return Tree('chord_type', list(tokens))
    def slash_bass(self, slash_tok, bass_note):
        return Tree('slash_bass', [slash_tok, bass_note])
    def bass_note(self, *tokens): return Tree('bass_note', list(tokens))

    # ---- Tokens passthrough (needed so they remain Token) ----
    def HEADER_FIELD(self, tok): return tok
    def HEADER_VALUE(self, tok): return tok
    def ACC(self, tok): return tok
    def PITCH(self, tok): return tok
    def OCT(self, tok): return tok
    def INT(self, tok): return tok
    def FSLASH(self, tok): return tok
    def BROKEN(self, tok): return tok
    def BARLINE(self, tok): return tok
    def CHORD_TYPE_TOKEN(self, tok): return tok
    def NOTE_LETTER(self, tok): return tok
    def ACC_SYM(self, tok): return tok
    def CHORD_QUOTE(self, tok): return tok
