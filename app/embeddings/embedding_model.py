from langchain_huggingface import HuggingFaceEmbeddings

from app.config.settings import settings


embedding_model = HuggingFaceEmbeddings(
    model_name=settings.embedding_model,
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": True},
)


def get_embedding_model() -> HuggingFaceEmbeddings:
    return embedding_model