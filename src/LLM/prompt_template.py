from pathlib import Path


class PromptTemplate:
    template:str
    def __init__(self, path:Path) -> None:
        self.template = path.read_text(encoding="utf-8")
    def embed(self, variable:dict[str, str]) -> None:
        for key, value in variable.items():
            self.template.replace("${"+key+"}", value)
