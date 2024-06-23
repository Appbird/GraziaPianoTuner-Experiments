import google.generativeai as genai
from google.generativeai import GenerativeModel, GenerationConfig
def set_gemini_API_Key():
    with open("./credential/GEMINI_KEY.txt") as f:
        gemini_key = f.read()
        genai.configure(api_key=gemini_key)

def ask_gemini_pro(
        model_name:str,
        system_prompt:str,
        user_prompt:str
    ):
    model = genai.GenerativeModel(
        model_name=model_name,
        system_instruction=system_prompt,
        generation_config=GenerationConfig(
            max_output_tokens=8192,
            temperature=1.0,
            top_p=0.95,
            top_k=64
        )
    )
    return model.generate_content(user_prompt).text

if __name__ == "__main__":
    set_gemini_API_Key()
    
    # モデルのデフォルト値情報を取る
    # model = genai.get_model('models/gemini-1.5-pro-001')
    # print(model)
    
    content = ask_gemini_pro(
        model_name='gemini-1.5-pro-001',
        system_prompt="range of numbers is from 0 to 100 in this context.",
        user_prompt="say 10 random number."
    )
    print(content)