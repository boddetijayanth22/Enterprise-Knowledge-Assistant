from app.vectorstore.client import get_qdrant_client
from app.config.settings import settings

from qdrant_client.models import Distance, VectorParams

client = get_qdrant_client()

if client.collection_exists(settings.collection_name):
    client.delete_collection(settings.collection_name)

client.create_collection(
    collection_name=settings.collection_name,
    vectors_config=VectorParams(
        size=384,      # BAAI/bge-small-en-v1.5
        distance=Distance.COSINE,
    ),
)

print("Collection created successfully.")