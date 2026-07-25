from langchain_huggingface import HuggingFaceEmbeddings

from app.config.settings import settings

_cached_embedding_model = None


def get_embedding_model() -> HuggingFaceEmbeddings:
    global _cached_embedding_model

    if _cached_embedding_model is None:

        _cached_embedding_model = HuggingFaceEmbeddings(
            model_name=settings.embedding_model,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )

    return _cached_embedding_model