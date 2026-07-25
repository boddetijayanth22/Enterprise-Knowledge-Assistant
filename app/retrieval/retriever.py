from langchain_core.documents import Document
from app.config.settings import settings
from app.embeddings.embedding_model import get_embedding_model
from app.vectorstore.client import get_qdrant_client
from app.utils.logger import logger

from app.retrieval.bm25 import BM25Retriever
from app.retrieval.hybrid import reciprocal_rank_fusion
from app.retrieval.reranker import CrossEncoderReranker
from app.retrieval.semantic import semantic_retrieve
from qdrant_client.models import (
    Filter,
    FieldCondition,
    MatchValue,
)

SEARCH_MODE = settings.search_mode

BM25_CACHE: dict[tuple[str, ...], BM25Retriever] = {}

RERANKER = CrossEncoderReranker()

RERANK_CANDIDATES = 20

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

def bm25_retrieve(
    query: str,
    documents: list[str] | None = None,
    top_k: int = 5,
):
    """
    Retrieve relevant document chunks using BM25.

    A separate BM25 index is cached for each unique document
    selection to avoid rebuilding the index on every request.
    """

    global BM25_CACHE

    cache_key = (
        tuple(sorted(set(documents)))
        if documents
        else ("__ALL__",)
    )

    if cache_key not in BM25_CACHE:

        loaded_documents = load_documents(documents)

        retriever = BM25Retriever()
        retriever.build_index(loaded_documents)

        BM25_CACHE[cache_key] = retriever

        logger.info(
            f"Created BM25 index for cache key: {cache_key}"
        )

    else:

        logger.info(
            f"Using cached BM25 index for cache key: {cache_key}"
        )

    return BM25_CACHE[cache_key].retrieve(
        query=query,
        top_k=top_k,
    )
    
def retrieve(
    query: str,
    documents: list[str] | None = None,
    top_k: int = 5,
    mode: str | None = None,
):

    mode = mode or SEARCH_MODE

    if mode == "hybrid_reranker":

        return hybrid_reranker_retrieve(
            query,
            documents,
            top_k,
        )

    elif mode == "bm25":

        return bm25_retrieve(
            query,
            documents,
            top_k,
        )

    elif mode == "semantic":
        return semantic_retrieve(
            query,
            documents,
            top_k,
        )

    elif mode == "hybrid":
        return hybrid_retrieve(
            query,
            documents,
            top_k,
        )
    
    else:
        raise ValueError(
            f"Unknown retrieval mode: {mode}"
        )

def hybrid_retrieve(
    query: str,
    documents: list[str] | None = None,
    top_k: int = 5,
):
    semantic_results = semantic_retrieve(
        query,
        documents,
        top_k,
    )

    bm25_results = bm25_retrieve(
        query,
        documents,
        top_k,
    )

    return reciprocal_rank_fusion(
        semantic_results,
        bm25_results,
    )[:top_k]

def hybrid_reranker_retrieve(
    query: str,
    documents: list[str] | None = None,
    top_k: int = 5,
):
    """
    Hybrid Search followed by CrossEncoder re-ranking.
    """

    hybrid_results = hybrid_retrieve(
        query=query,
        documents=documents,
        top_k=RERANK_CANDIDATES,
    )

    print("\nHYBRID RESULTS")
    for i, doc in enumerate(hybrid_results):
        print(i + 1, doc.metadata, doc.page_content[:100])

    return RERANKER.rerank(
        query=query,
        documents=hybrid_results,
        top_k=top_k,
    )

    print("\nRERANKED RESULTS")
    for i, doc in enumerate(reranked):
        print(i + 1, doc.metadata, doc.page_content[:100])

    return reranked