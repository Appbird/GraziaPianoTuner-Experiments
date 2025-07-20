from fractions import Fraction
from pathlib import Path
from LLM.OpenAI import GPT, Model
from LLM.prompt_template import PromptTemplate
from conversion.answer2abc import extract_abc_score
from parser.ast.context import Context
from parser.ast.measure_info import MeasureInfo
from parser.ast.score import Score
from parser.lexer.lexer import abc_parser
from parser.transformer.ABCMusicAST import ABCMusicAST

def compose_music(X:str, a:float, b:float):
    prompt_path = Path("./src/qualitative/prompt_template/")
    model = Model.gpt_4o_2024_08_06
    system_msg = PromptTemplate(prompt_path/"system.txt")
    user_msg = PromptTemplate(prompt_path/"input.txt")
    before_param = {"axis": X, "value": f"{a:.2f}"}
    after_param = {"axis": X, "value": f"{b:.2f}"}
    
    gpt = GPT(model, system_msg.embed({}))
    gpt.tell(user_msg.embed(before_param))
    result, score_a = extract_abc_score(gpt.ask(True))
    assert result.is_ok()
    gpt.tell(user_msg.embed(after_param))
    result, score_b = extract_abc_score(gpt.ask(True))
    assert result.is_ok()
    return score_a, score_b

def compose_with_two_axes(X:str, Y:str, a:float, b:float):
    prompt_path = Path("./src/qualitative/prompt_template/")
    model = Model.gpt_4o_2024_08_06
    system_msg = PromptTemplate(prompt_path/"system.txt")
    user_msg = PromptTemplate(prompt_path/"input_grid.txt")
    param = {"axis1": X, "value1": f"{a:.2f}", "axis2": Y, "value2": f"{b:.2f}"}
    gpt = GPT(model, system_msg.embed({}))
    gpt.tell(user_msg.embed(param))
    result, score_a = extract_abc_score(gpt.ask(True))
    assert result.is_ok(), result.reason
    return score_a


def to_measures(abc:str):
    tree = abc_parser.parse(abc+"\n")
    ast:Score = ABCMusicAST().transform(tree)
    c = Context()
    measure_list:list[MeasureInfo] = []
    ast.eval(c, measure_list)
    return measure_list