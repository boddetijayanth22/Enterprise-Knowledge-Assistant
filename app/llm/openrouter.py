from openai import OpenAI
from langchain_core.messages import AIMessage

from app.config.settings import settings
from app.llm.exceptions import LLMProviderError
from app.llm.retry import retry_with_backoff
from app.utils.logger import logger


class OpenRouterLLM:
    def __init__(self):
        self.client = OpenAI(
            api_key=settings.openrouter_api_key,
            base_url="https://openrouter.ai/api/v1",
            timeout=30.0,
            max_retries=0,
        )

    def invoke(self, prompt):
        def call_provider():
            return self.client.chat.completions.create(
                model=settings.llm_model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                temperature=0,
                max_tokens=settings.llm_max_tokens,
            )

        try:
            response = retry_with_backoff(call_provider)
        except Exception as exc:
            logger.error(
                "openrouter_request_failed | "
                "error_type=%s | "
                "status_code=%s",
                type(exc).__name__,
                getattr(exc, "status_code", None),
            )
            raise LLMProviderError("openrouter") from exc
        return AIMessage(
            content=response.choices[0].message.content
        )


def get_openrouter_llm():
    return OpenRouterLLM()