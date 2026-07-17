from qdrant_client.models import Filter, FieldCondition, MatchValue

from app.config.settings import settings
from app.vectorstore.client import get_qdrant_client


def delete_document(filename: str):

    client = get_qdrant_client()

    client.delete(
        collection_name=settings.collection_name,
        points_selector=Filter(
            must=[
                FieldCondition(
                    key="source",
                    match=MatchValue(value=filename),
                )
            ]
        ),
    )

    return {
        "message": f"{filename} deleted successfully."
    }