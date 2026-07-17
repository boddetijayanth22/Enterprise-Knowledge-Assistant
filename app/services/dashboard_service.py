from collections import Counter
from pathlib import Path
from qdrant_client.http.exceptions import UnexpectedResponse

from app.config.settings import settings
from app.vectorstore.client import get_qdrant_client


def get_dashboard_data():

    client = get_qdrant_client()

    try:
        points, _ = client.scroll(
            collection_name=settings.collection_name,
            limit=10000,
            with_payload=True,
        )

    except UnexpectedResponse:
        return [], {
            "documents": 0,
            "chunks": 0,
            "embedding_model": settings.embedding_model,
            "vector_db": "Qdrant",
        }
        
    files = [
        Path(point.payload["source"]).name
        for point in points
    ]

    counter = Counter(files)

    documents = [
        {
            "filename": filename,
            "chunks": count,
        }
        for filename, count in counter.items()
    ]

    stats = {
        "documents": len(counter),
        "chunks": len(points),
        "embedding_model": settings.embedding_model,
        "vector_db": "Qdrant",
    }

    print("Documents returned:")
    for doc in documents:
        print(doc)

    return documents, stats