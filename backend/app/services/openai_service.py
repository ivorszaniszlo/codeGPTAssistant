from langchain.llms import OpenAI

class OpenAIService:
    def __init__(self, api_key: str, model: str = "gpt-4"):
        self.llm = OpenAI(api_key=api_key, model=model)

    def generate_response(self, prompt: str) -> str:
        return self.llm(prompt)
