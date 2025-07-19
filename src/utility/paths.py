from pathlib import Path

def result_dir(result_path:Path, MODEL_NAME:str, exp_name:str):
    return result_path/MODEL_NAME/exp_name

def filename(path:Path, ext:str):
    return path.parent/Path(f"{path.stem}.{ext}")

def credential_path():
    return Path("./credential")

def prompt_path():
    return Path("./prompts")