from langchain_core.documents import Document
from app.config.settings import settings
from app.embeddings.embedding_model import get_embedding_model
from app.vectorstore.client import get_qdrant_client
from app.utils.logger import logger
from app.retrieval.bm25 import BM25Retriever
from qdrant_client.models import (
    Filter,
    FieldCondition,
    MatchValue,
)


def load_documents(
    documents: list[str] | None = None,
) -> list[Document]:
    """
    Load all matching document chunks from Qdrant.
    """

    client = get_qdrant_client()

    search_filter = None

    if documents:

        search_filter = Filter(
            should=[
                FieldCondition(
                    key="source",
                    match=MatchValue(value=document),
                )
                for document in documents
            ]
        )

    points, _ = client.scroll(
        collection_name=settings.collection_name,
        scroll_filter=search_filter,
        limit=10000,
        with_payload=True,
    )

    loaded_documents = []

    for point in points:

        payload = point.payload

        loaded_documents.append(
            Document(
                page_content=payload["text"],
                metadata={
                    "page": payload["page"],
                    "source": payload["source"],
                },
            )
        )

    return loaded_documents


def semantic_retrieve(
    query: str,
    documents: list[str] | None = None,
    top_k: int = 5,
):
    """
    Retrieve the most relevent document chunks
    using semantic vector search.
    """

    search_filter = None

    if documents:

        search_filter = Filter(
            should=[
                FieldCondition(
                    key="source",
                    match=MatchValue(value=document),
                )
                for document in documents
            ]
        )

    embedding_model = get_embedding_model()

    query_vector = embedding_model.embed_query(query)

    client = get_qdrant_client()

    logger.info(f"Selected documents: {documents}")
    logger.info(f"Filter: {search_filter}")
    
    results = client.query_points(
        collection_name=settings.collection_name,
        query=query_vector,
        query_filter=search_filter,
        limit=top_k,
    ).points

    logger.info(f"Retrieved {len(results)} chunks")

    for result in results:
        logger.info(f"Matched: {result.payload['source']}")

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
                },
            )
        )

    return retrieved_documents


def bm25_retrieve(
    query: str,
    documents: list[str] | None = None,
    top_k: int = 5,
):
    """
    Retrieve document chunks using BM25.
    """

    loaded_documents = load_documents(documents)

    retriever = BM25Retriever()

    retriever.build_index(loaded_documents)

    return retriever.retrieve(
        query=query,
        top_k=top_k,
    )


SEARCH_MODE = "bm25"
    
def retrieve(
    query: str,
    documents: list[str] | None = None,
    top_k: int = 5,
):
    if SEARCH_MODE == "semantic":

        return semantic_retrieve(
            query,
            documents,
            top_k,
        )

    elif SEARCH_MODE == "bm25":

        return bm25_retrieve(
            query,
            documents,
            top_k,
        )