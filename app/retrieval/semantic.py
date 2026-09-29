from langchain_core.documents import Document

from app.config.settings import settings
from app.embeddings.embedding_model import get_embedding_model
from app.vectorstore.client import get_qdrant_client
from app.utils.logger import logger

from qdrant_client.models import (
    Filter,
    FieldCondition,
    MatchValue,
)


def semantic_retrieve(
    query: str,
    owner_id: int,
    documents: list[str] | None = None,
    top_k: int = 5,
):
    """
    Retrieve the most relevant document chunks using semantic vector search.

    Retrieval is always restricted to the authenticated user's documents.
    """

    must_conditions = [
        FieldCondition(
            key="owner_id",
            match=MatchValue(value=owner_id),
        )
    ]

    should_conditions = []

    if documents:
        should_conditions = [
            FieldCondition(
                key="source",
                match=MatchValue(value=document),
            )
            for document in documents
        ]

    search_filter = Filter(
        must=must_conditions,
        should=should_conditions if should_conditions else None,
    )

    embedding_model = get_embedding_model()

    query_vector = embedding_model.embed_query(query)

    client = get_qdrant_client()

    logger.info(
        f"Semantic retrieval for owner_id={owner_id}, "
        f"documents={documents}"
    )

    results = client.query_points(
        collection_name=settings.collection_name,
        query=query_vector,
        query_filter=search_filter,
        limit=top_k,
    ).points

    logger.info(
        f"Retrieved {len(results)} chunks for owner_id={owner_id}"
    )

    retrieved_documents = []

    for result in results:

        payload = result.payload

        retrieved_documents.append(
            Document(
                page_content=payload["text"],
                metadata={
                    "page": payload["page"],
                    "source": payload["source"],
                    "score": result.score,
                    "owner_id": payload.get("owner_id"),
                    "classification": payload.get(
                        "classification",
                        "INTERNAL",
                    ),
                }
            )
        )

    return retrieved_documents