from langchain_groq import ChatGroq

from app.config.settings import settings
from app.llm.exceptions import LLMProviderError


class GroqLLM:
    def __init__(self):
        self.llm = ChatGroq(
            model=settings.llm_model,
            api_key=settings.groq_api_key,
            temperature=0,
            timeout=30,
            max_retries=0,
        )

    def invoke(self, prompt):
        try:
            return self.llm.invoke(prompt)
        except Exception as exc:
            raise LLMProviderError("groq") from exc


def get_groq_llm():
    return GroqLLM()