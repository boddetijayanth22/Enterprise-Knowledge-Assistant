from langchain_groq import ChatGroq

from app.config.settings import settings


def get_groq_llm():
    return ChatGroq(
        model=settings.llm_model,
        api_key=settings.groq_api_key,
        temperature=0,
    )