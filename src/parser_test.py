from fractions import Fraction
from lark import Lark
from parser.ast.context import Context
from parser.ast.measure_info import MeasureInfo
from parser.transformer.ABCMusicAST import ABCMusicAST
from parser.lexer.lexer import abc_parser

text = """X: 1
T: Jazzy Serenade
C: GPT
M: 4/4
L: 1/4
Q: 1/4=120
K: D major
V:1
| "D7" D/2F/2A/2F "A7" E/2A/2c/2A/2 |
K: E major
Q: 1/4=150
| "Bm7" B/2d/2f/2d/2 "G7" G/2B/2d/2B/2 |
"""
tree = abc_parser.parse(text)      # Lark Tree
# print(tree)
ast = ABCMusicAST().transform(tree)            # 変換
c = Context(0, Fraction(0), Fraction(0), None)
measure_list:list[MeasureInfo] = []
ast.eval(c, measure_list)
for m in measure_list:
    m.dump()