from app.config.settings import settings
from app.llm.groq import get_groq_llm
from app.llm.openrouter import get_openrouter_llm


def get_llm():

    provider = settings.llm_provider.lower()

    if provider == "openrouter":
        return get_openrouter_llm()

    if provider == "groq":
        return get_groq_llm()

    raise ValueError(
        f"Unsupported LLM provider: {settings.llm_provider}"
    )