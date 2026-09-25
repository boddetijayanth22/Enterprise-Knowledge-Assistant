from openai import OpenAI
from langchain_core.messages import AIMessage

from app.config.settings import settings


class OpenRouterLLM:
    def __init__(self):
        self.client = OpenAI(
            api_key=settings.openrouter_api_key,
            base_url="https://openrouter.ai/api/v1",
        )

    def invoke(self, prompt):
        response = self.client.chat.completions.create(
            model=settings.llm_model,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            temperature=0,
        )

        return AIMessage(
            content=response.choices[0].message.content
        )


def get_openrouter_llm():
    return OpenRouterLLM()