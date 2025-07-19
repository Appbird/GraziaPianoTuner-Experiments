from enum import Enum
from openai import OpenAI
from openai.types.chat.chat_completion_message_param import ChatCompletionMessageParam
from utility.paths import credential_path

class Model(Enum):
    gpt_4_1_2025_04_14       = "gpt-4.1-2025-04-14"
    gpt_4o_2024_11_20       = "gpt-4o-2024-11-20"
    gpt_4o_2024_08_06       = "gpt-4o-2024-08-06"
    gpt_4o_2024_05_13       = "gpt-4o-2024-05-13"
    gpt_4_turbo_2024_04_09  = "gpt-4-turbo-2024-04-09"
    gpt_4_0613              = "gpt-4-0613"
    gpt_3_5_turbo_0125      = "gpt-3.5-turbo-0125"
    
class GPT:
    def __init__(self, model:Model, system_message:str, temparature:float = 1.0):
        """
        クライアントオブジェクトを作る。これを作らないとAPIへの問い合わせができない。
        ターミナルのカレントディレクトリから見て、`./src/credential/OPEN_AI_KEY.txt`に記述されているAPIキーを読み取って実行します。
        """
        OPEN_AI_KEY = ""
        with open(credential_path()/"OPEN_AI_KEY.txt") as f:
            OPEN_AI_KEY = f.read()
        self.client = OpenAI(api_key=OPEN_AI_KEY)
        self.dialog:list[ChatCompletionMessageParam] = [ {"role": "system", "content": system_message} ]
        self.model = model
        self.system_msg = system_message
        self.temparature = temparature
    
    def tell(self, message:str):
        self.dialog.append({
            "role": "user", "content": message
        })
    def remember(self, message:str):
        self.dialog.append({
            "role": "assistant", "content": message
        })
    def forget_without_system_msg(self):
        self.dialog = list(filter((lambda msg: msg["role"] == "system"), self.dialog))
    
    def dump_dialog(self):
        print(f"[dump_dialog]")
        for msg in self.dialog:
            if msg["role"] == "system": continue
            assert "content" in msg
            print(f"{msg['role']}: {msg['content']}\n")
        print(f"[end dump_dialog]\n\n")
    def ask(self, remember_self_msg:bool) -> str:
        """
        clientオブジェクトを使って、promptの内容でGPT-4に問い合わせる。
        問い合わせた結果が返り値になります。
        """
        
        response = self.client.chat.completions.create(
            model = self.model.value,
            messages=self.dialog,
            temperature=self.temparature
        )
        result = response.choices[0].message.content
        if result != None:
            if remember_self_msg: self.remember(result)
            return result
        else:
            return  "[There is no content in response.choices[0].message.]"

    if __name__ == "__main__":
        print()