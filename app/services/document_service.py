from pathlib import Path

from qdrant_client.models import (
    Filter,
    FieldCondition,
    MatchValue,
)

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

    pdf_path = Path("data/raw") / filename

    if not pdf_path.exists():
        raise FileNotFoundError(
            f"{filename} does not exist."
        )

    pdf_path.unlink()

    return {
        "message": f"{filename} deleted successfully."
    }