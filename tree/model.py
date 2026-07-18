from dotenv import load_dotenv
from google import genai

load_dotenv()


class AIModel:
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.client = genai.Client() 

    def summarize_code(self, code_snippet: str) -> str:
        prompt = f"Summarize the following code snippet in one line:\n\n{code_snippet}"
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
        )
        return response.text

if __name__ == "__main__":
    model_name = "gemini-3.1-flash-lite"
    snippet = '''
    # Example code snippet
    for i in range(5):
        print(i)
    '''

    obj = AIModel(model_name)
    summary = obj.summarize_code(snippet)
    print("Summary of the code snippet:\n",summary)