from functools import lru_cache

from qdrant_client import QdrantClient

from app.config.settings import settings


@lru_cache
def get_qdrant_client():
    return QdrantClient(
        host=settings.qdrant_host,
        port=settings.qdrant_port,
    )