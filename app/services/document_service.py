from pathlib import Path

from qdrant_client.models import Filter, FieldCondition, MatchValue

from app.config.settings import settings
from app.database.connection import SessionLocal
from app.database.document_models import Document
from app.vectorstore.client import get_qdrant_client


def _build_document_filter(
    filename: str,
    owner_id: int,
) -> Filter:
    return Filter(
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


def list_documents(owner_id: int):
    client = get_qdrant_client()
    db = SessionLocal()

    try:
        db_documents = (
            db.query(Document)
            .filter(
                Document.owner_id == owner_id,
            )
            .order_by(
                Document.created_at.desc(),
            )
            .all()
        )

        documents = []

        for document in db_documents:

            chunk_count = 0

            if document.status == "completed":

                document_filter = _build_document_filter(
                    filename=document.filename,
                    owner_id=owner_id,
                )

                points, _ = client.scroll(
                    collection_name=settings.collection_name,
                    scroll_filter=document_filter,
                    limit=10000,
                    with_payload=False,
                )

                chunk_count = len(points)

            documents.append(
                {
                    "filename": document.filename,
                    "status": document.status,
                    "chunks": chunk_count,
                }
            )

        return documents

    finally:
        db.close()


def delete_document(
    filename: str,
    owner_id: int,
):
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

        if document is None:
            raise FileNotFoundError(
                "Document not found."
            )

        if document.status in {
            "processing",
            "completed",
        }:

            client = get_qdrant_client()

            document_filter = _build_document_filter(
                filename=filename,
                owner_id=owner_id,
            )

            try:

                client.delete(
                    collection_name=settings.collection_name,
                    points_selector=document_filter,
                )

            except Exception:
                if document.status == "completed":
                    raise

        safe_filename = Path(filename).name

        file_path = (
            Path("data/raw")
            / str(owner_id)
            / safe_filename
        )

        if file_path.exists():
            file_path.unlink()

        db.delete(document)
        db.commit()

        return {
            "filename": filename,
            "status": "deleted",
        }

    except FileNotFoundError:
        db.rollback()
        raise

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()