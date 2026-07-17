from langchain_groq import ChatGroq

from app.config.settings import settings


def get_llm():

    return ChatGroq(
        model="llama-3.3-70b-versatile",
        api_key=settings.groq_api_key,
        temperature=0,
    )