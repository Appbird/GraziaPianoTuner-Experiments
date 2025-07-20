from pathlib import Path


class PromptTemplate:
    template:str
    def __init__(self, path:Path) -> None:
        self.template = path.read_text(encoding="utf-8")
    def embed(self, variable:dict[str, str]) -> str:
        prompt = self.template
        for key, value in variable.items():
            prompt = prompt.replace("${"+key+"}", value)
        assert "${" not in prompt
        return prompt
