from app.utils.file_hash import calculate_file_hash
from uuid import uuid4
from app.utils.logger import logger
from qdrant_client.models import PointStruct
from qdrant_client.models import Filter, FieldCondition, MatchValue
from pathlib import Path
from app.chunking.chunker import split_documents
from app.embeddings.embedding_model import get_embedding_model
from app.loaders.pdf_loader import load_pdf
from app.config.settings import settings
from app.vectorstore.client import get_qdrant_client

def ingest_pdf(pdf_path: str) -> None:

    """
    Load a PDF, split it into chunks, generate embeddings,
    and store then in Qdrant.
    """

    file_hash = calculate_file_hash(pdf_path)

    client = get_qdrant_client()

    existing_points, _ = client.scroll(
        collection_name=settings.collection_name,
        scroll_filter=Filter(
            must=[
                FieldCondition(
                    key="file_hash",
                    match=MatchValue(value=file_hash),
                )
            ]
        ),
        limit=1,
    )

    if existing_points:
        logger.warning("PDF already indexed. Skipping.....")
        return

    logger.info("Loading PDF.....")
    documents = load_pdf(pdf_path)

    logger.info("Chunking.....")
    chunks = split_documents(documents)

    embedding_model = get_embedding_model()
    logger.info("Generating embeddings.....")

    points = []

    for chunk in chunks:

        vector = embedding_model.embed_query(chunk.page_content)

        points.append(
            PointStruct(
                id=str(uuid4()),
                vector=vector,
                payload={
                    "text": chunk.page_content,
                    "page": chunk.metadata["page"],
                    "source": Path(chunk.metadata["source"]).name,
                    "file_hash": file_hash,
                },
            )
        )

    logger.info("Uploading vectors to Qdrant...")

    print(points[0].payload)

    client.upsert(
        collection_name=settings.collection_name,
        points=points,
    )

    logger.info(f"Successfully stored {len(points)} chunks.")