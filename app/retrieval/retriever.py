import time

from langchain_core.documents import Document

from app.config.settings import settings
from app.vectorstore.client import get_qdrant_client
from app.utils.logger import logger

from app.retrieval.bm25 import BM25Retriever
from app.retrieval.hybrid import reciprocal_rank_fusion
from app.retrieval.reranker import CrossEncoderReranker
from app.retrieval.semantic import semantic_retrieve
from app.observability.metrics import metrics

from qdrant_client.models import (
    Filter,
    FieldCondition,
    MatchValue,
)


SEARCH_MODE = settings.search_mode

BM25_CACHE: dict[
    tuple[int, tuple[str, ...]],
    BM25Retriever,
] = {}

RERANKER = CrossEncoderReranker()

RERANK_CANDIDATES = 20


def load_documents(
    owner_id: int,
    documents: list[str] | None = None,
) -> list[Document]:
    """
    Load document chunks belonging only to the authenticated user.
    """

    client = get_qdrant_client()

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
                    "owner_id": payload.get("owner_id"),
                    "classification": payload.get(
                        "classification",
                        "INTERNAL",
                    ),
                },
            )
        )

    logger.info(
        "Loaded %s chunks for owner_id=%s",
        len(loaded_documents),
        owner_id,
    )

    return loaded_documents


def expand_page_context(
    retrieved_documents: list[Document],
    owner_id: int,
    documents: list[str] | None = None,
) -> list[Document]:
    """
    Expand retrieved chunks with other chunks from the same
    source and PDF page.

    This improves context completeness when a logical answer
    spans multiple chunks on the same PDF page.
    """

    if not retrieved_documents:
        return []

    client = get_qdrant_client()

    expanded_documents = []
    seen_chunks = set()

    for document in retrieved_documents:

        source = document.metadata["source"]
        page = int(document.metadata["page"])

        must_conditions = [
            FieldCondition(
                key="owner_id",
                match=MatchValue(value=owner_id),
            ),
            FieldCondition(
                key="source",
                match=MatchValue(value=source),
            ),
            FieldCondition(
                key="page",
                match=MatchValue(value=page),
            ),
        ]

        if documents and source not in documents:
            continue

        page_filter = Filter(
            must=must_conditions,
        )

        points, _ = client.scroll(
            collection_name=settings.collection_name,
            scroll_filter=page_filter,
            limit=100,
            with_payload=True,
        )

        for point in points:

            payload = point.payload

            chunk_key = (
                source,
                page,
                payload["text"],
            )

            if chunk_key in seen_chunks:
                continue

            seen_chunks.add(chunk_key)

            expanded_documents.append(
                Document(
                    page_content=payload["text"],
                    metadata={
                        "page": payload["page"],
                        "source": payload["source"],
                        "owner_id": payload.get("owner_id"),
                        "classification": payload.get(
                            "classification",
                            "INTERNAL",
                        ),
                    },
                )
            )

    logger.info(
        "Expanded retrieval context | "
        "original_chunks=%s | expanded_chunks=%s",
        len(retrieved_documents),
        len(expanded_documents),
    )

    return expanded_documents


def bm25_retrieve(
    query: str,
    owner_id: int,
    documents: list[str] | None = None,
    top_k: int = 5,
):
    """
    Retrieve relevant document chunks using BM25.

    BM25 indexes are isolated by authenticated user and document
    selection to prevent cross-user cache contamination.
    """

    global BM25_CACHE

    document_key = (
        tuple(sorted(set(documents)))
        if documents
        else ("__ALL__",)
    )

    cache_key = (
        owner_id,
        document_key,
    )

    if cache_key not in BM25_CACHE:

        loaded_documents = load_documents(
            owner_id=owner_id,
            documents=documents,
        )

        retriever = BM25Retriever()

        retriever.build_index(
            loaded_documents
        )

        BM25_CACHE[cache_key] = retriever

        logger.info(
            "Created BM25 index for owner_id=%s, documents=%s",
            owner_id,
            document_key,
        )

    else:

        logger.info(
            "Using cached BM25 index for owner_id=%s, documents=%s",
            owner_id,
            document_key,
        )

    return BM25_CACHE[cache_key].retrieve(
        query=query,
        top_k=top_k,
    )


def retrieve(
    query: str,
    owner_id: int,
    documents: list[str] | None = None,
    top_k: int = 5,
    mode: str | None = None,
):

    mode = mode or SEARCH_MODE

    start_time = time.perf_counter()

    if mode == "hybrid_reranker":

        results = hybrid_reranker_retrieve(
            query=query,
            owner_id=owner_id,
            documents=documents,
            top_k=top_k,
        )

    elif mode == "bm25":

        results = bm25_retrieve(
            query=query,
            owner_id=owner_id,
            documents=documents,
            top_k=top_k,
        )

    elif mode == "semantic":

        results = semantic_retrieve(
            query=query,
            owner_id=owner_id,
            documents=documents,
            top_k=top_k,
        )

    elif mode == "hybrid":

        results = hybrid_retrieve(
            query=query,
            owner_id=owner_id,
            documents=documents,
            top_k=top_k,
        )

    else:

        raise ValueError(
            f"Unknown retrieval mode: {mode}"
        )

    expanded_results = expand_page_context(
        retrieved_documents=results,
        owner_id=owner_id,
        documents=documents,
    )

    retrieval_latency_ms = round(
        (time.perf_counter() - start_time) * 1000,
        2,
    )

    metrics.record_retrieval(
        retrieval_latency_ms
    )

    logger.info(
        "retrieval_completed | "
        "owner_id=%s | "
        "mode=%s | "
        "results=%s | "
        "expanded_results=%s | "
        "latency_ms=%s",
        owner_id,
        mode,
        len(results),
        len(expanded_results),
        retrieval_latency_ms,
    )

    return expanded_results


def hybrid_retrieve(
    query: str,
    owner_id: int,
    documents: list[str] | None = None,
    top_k: int = 5,
):

    semantic_results = semantic_retrieve(
        query=query,
        owner_id=owner_id,
        documents=documents,
        top_k=top_k,
    )

    bm25_results = bm25_retrieve(
        query=query,
        owner_id=owner_id,
        documents=documents,
        top_k=top_k,
    )

    logger.info(
        "HYBRID SEMANTIC | query=%s | results=%s",
        query,
        len(semantic_results),
    )

    for rank, document in enumerate(
        semantic_results,
        start=1,
    ):
        logger.info(
            "HYBRID SEMANTIC RESULT | rank=%s | source=%s | page=%s",
            rank,
            document.metadata.get("source"),
            document.metadata.get("page"),
        )

    logger.info(
        "HYBRID BM25 | query=%s | results=%s",
        query,
        len(bm25_results),
    )

    for rank, document in enumerate(
        bm25_results,
        start=1,
    ):
        logger.info(
            "HYBRID BM25 RESULT | rank=%s | source=%s | page=%s",
            rank,
            document.metadata.get("source"),
            document.metadata.get("page"),
        )

    fused_results = reciprocal_rank_fusion(
        semantic_results,
        bm25_results,
    )

    return fused_results[:top_k]


def hybrid_reranker_retrieve(
    query: str,
    owner_id: int,
    documents: list[str] | None = None,
    top_k: int = 5,
):
    """
    Hybrid Search followed by CrossEncoder re-ranking.
    """

    hybrid_results = hybrid_retrieve(
        query=query,
        owner_id=owner_id,
        documents=documents,
        top_k=RERANK_CANDIDATES,
    )

    return RERANKER.rerank(
        query=query,
        documents=hybrid_results,
        top_k=top_k,
    )