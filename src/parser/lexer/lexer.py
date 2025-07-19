from pathlib import Path
from lark import Lark

abc_parser = Lark(Path("./src/parser/grammar.lark").read_text(), start="start", parser="lalr", lexer="contextual")
