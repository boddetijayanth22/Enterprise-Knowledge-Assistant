from app.evaluation.retrieval_metrics import (
    mean_reciprocal_rank,
    precision_at_k,
    recall_at_k,
    reciprocal_rank,
)
from app.retrieval.retriever import retrieve


def _unique_pages(retrieved_docs) -> list[int]:
    """
    Convert retrieved chunks into an ordered list of unique
    one-based PDF page numbers.
    """
    pages = []
    seen = set()

    for doc in retrieved_docs:
        page = int(doc.metadata["page"]) + 1

        if page not in seen:
            seen.add(page)
            pages.append(page)

    return pages


def evaluate_query(
    question: str,
    relevant_pages: set[int],
    owner_id: int,
    documents: list[str] | None = None,
    mode: str = "hybrid_reranker",
    k: int = 5,
) -> dict:
    """
    Evaluate one query against the production retrieval pipeline.

    Ground truth uses one-based PDF page numbers.
    """

    retrieved_docs = retrieve(
        query=question,
        owner_id=owner_id,
        documents=documents,
        top_k=k,
        mode=mode,
    )

    retrieved_pages = _unique_pages(retrieved_docs)[:k]

    return {
        "question": question,
        "retrieved_pages": retrieved_pages,
        "relevant_pages": sorted(relevant_pages),
        "precision_at_k": precision_at_k(
            retrieved_pages,
            relevant_pages,
            k,
        ),
        "recall_at_k": recall_at_k(
            retrieved_pages,
            relevant_pages,
            k,
        ),
        "reciprocal_rank": reciprocal_rank(
            retrieved_pages,
            relevant_pages,
        ),
    }


def evaluate_dataset(
    dataset: list[dict],
    owner_id: int,
    documents: list[str] | None = None,
    mode: str = "hybrid_reranker",
    k: int = 5,
) -> dict:
    """
    Evaluate an entire retrieval benchmark.
    """

    results = []

    for item in dataset:
        result = evaluate_query(
            question=item["question"],
            relevant_pages=set(item["relevant_pages"]),
            owner_id=owner_id,
            documents=documents,
            mode=mode,
            k=k,
        )

        results.append(result)

    metric_pairs = [
        (
            result["retrieved_pages"],
            set(result["relevant_pages"]),
        )
        for result in results
    ]

    return {
        "mode": mode,
        "k": k,
        "queries": len(results),
        "precision_at_k": (
            sum(r["precision_at_k"] for r in results)
            / len(results)
            if results
            else 0.0
        ),
        "recall_at_k": (
            sum(r["recall_at_k"] for r in results)
            / len(results)
            if results
            else 0.0
        ),
        "mrr": mean_reciprocal_rank(metric_pairs),
        "results": results,
    }