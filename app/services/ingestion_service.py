from uuid import uuid4
from pathlib import Path

from qdrant_client.models import (
    Filter,
    FieldCondition,
    MatchValue,
    PointStruct,
)

from app.privacy.classifier import DataClassification
from app.utils.file_hash import calculate_file_hash
from app.utils.logger import logger
from app.chunking.chunker import split_documents
from app.embeddings.embedding_model import get_embedding_model
from app.loaders.pdf_loader import load_pdf
from app.config.settings import settings
from app.vectorstore.client import get_qdrant_client
from app.database.connection import SessionLocal
from app.database.document_models import Document


def ingest_pdf(
    pdf_path: str,
    owner_id: int,
    document_id: int,
    retry: bool = False,
) -> None:
    """
    Load a PDF, split it into chunks, generate embeddings,
    and store them in Qdrant with document ownership
    and data classification metadata.

    Updates the corresponding Document record to:
    - completed when ingestion succeeds
    - failed when ingestion raises an exception
    """

    db = SessionLocal()

    try:
        file_hash = calculate_file_hash(pdf_path)
        filename = Path(pdf_path).name
        classification = DataClassification.INTERNAL.value

        client = get_qdrant_client()

        document = db.get(Document, document_id)

        existing_points, _ = client.scroll(
            collection_name=settings.collection_name,
            scroll_filter=Filter(
                must=[
                    FieldCondition(
                        key="file_hash",
                        match=MatchValue(value=file_hash),
                    ),
                    FieldCondition(
                        key="owner_id",
                        match=MatchValue(value=owner_id),
                    ),
                ]
            ),
            limit=1,
        )

        if existing_points:
            if retry:
                logger.warning(
                    "Removing previous partial ingestion before retry."
                )

                client.delete(
                    collection_name=settings.collection_name,
                    points_selector=Filter(
                        must=[
                            FieldCondition(
                                key="file_hash",
                                match=MatchValue(value=file_hash),
                            ),
                            FieldCondition(
                                key="owner_id",
                                match=MatchValue(value=owner_id),
                            ),
                        ]
                    ),
                )
            else:
                logger.warning(
                    "PDF already indexed. Skipping....."
                )

                if document:
                    document.status = "completed"
                    db.commit()

                return

        logger.info("Loading PDF.....")
        documents = load_pdf(pdf_path)

        logger.info("Chunking.....")
        chunks = split_documents(documents)

        embedding_model = get_embedding_model()

        logger.info("Generating embeddings...")

        points = []

        for chunk in chunks:
            vector = embedding_model.embed_query(
                chunk.page_content
            )

            points.append(
                PointStruct(
                    id=str(uuid4()),
                    vector=vector,
                    payload={
                        "text": chunk.page_content,
                        "source": filename,
                        "page": chunk.metadata["page"],
                        "file_hash": file_hash,
                        "owner_id": owner_id,
                        "classification": classification,
                    },
                )
            )

        logger.info("Uploading vectors to Qdrant...")

        client.upsert(
            collection_name=settings.collection_name,
            points=points,
        )

        document = db.get(Document, document_id)

        if document:
            document.status = "completed"
            db.commit()

        logger.info(
            "Successfully stored %s chunks for user %s.",
            len(points),
            owner_id,
        )

    except Exception:
        db.rollback()

        document = db.get(Document, document_id)

        if document:
            document.status = "failed"
            db.commit()

        logger.exception(
            "PDF ingestion failed for document_id=%s.",
            document_id,
        )

    finally:
        db.close()