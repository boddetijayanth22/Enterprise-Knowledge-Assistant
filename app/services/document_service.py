from pathlib import Path

from qdrant_client.models import Filter, FieldCondition, MatchValue

from app.config.settings import settings
from app.database.connection import SessionLocal
from app.database.document_models import Document
from app.vectorstore.client import get_qdrant_client


def list_documents(owner_id: int):
    client = get_qdrant_client()

    points, _ = client.scroll(
        collection_name=settings.collection_name,
        scroll_filter=Filter(
            must=[
                FieldCondition(
                    key="owner_id",
                    match=MatchValue(value=owner_id),
                )
            ]
        ),
        limit=10000,
        with_payload=True,
    )

    documents = {}

    for point in points:
        payload = point.payload or {}

        filename = payload.get("source")

        if not filename:
            continue

        documents.setdefault(filename, 0)
        documents[filename] += 1

    return [
        {
            "filename": filename,
            "chunks": chunks,
        }
        for filename, chunks in documents.items()
    ]


def delete_document(
    filename: str,
    owner_id: int,
):
    client = get_qdrant_client()

    document_filter = Filter(
        must=[
            FieldCondition(
                key="source",
                match=MatchValue(value=filename),
            ),
            FieldCondition(
                key="owner_id",
                match=MatchValue(value=owner_id),
            ),
        ]
    )

    points, _ = client.scroll(
        collection_name=settings.collection_name,
        scroll_filter=document_filter,
        limit=1,
        with_payload=True,
    )

    if not points:
        raise FileNotFoundError(
            "Document not found."
        )

    client.delete(
        collection_name=settings.collection_name,
        points_selector=document_filter,
    )

    file_path = (
        Path("data/raw")
        / str(owner_id)
        / filename
    )

    if file_path.exists():
        file_path.unlink()

    db = SessionLocal()

    try:
        document = (
            db.query(Document)
            .filter(
                Document.filename == filename,
                Document.owner_id == owner_id,
            )
            .first()
        )

        if document:
            db.delete(document)
            db.commit()

    finally:
        db.close()

    return {
        "filename": filename,
        "status": "deleted",
    }