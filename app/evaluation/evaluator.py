import json
from pathlib import Path

from app.evaluation.metrics import (
    precision_at_k,
    recall_at_k,
    mean_reciprocal_rank,
)

from app.retrieval.retriever import (
    retrieve,
    SEARCH_MODE,
)


def load_queries() -> list[dict]:
    """
    Load evaluation queries from queries.json.
    """

    query_file = Path(__file__).parent / "queries.json"

    with open(query_file, "r", encoding="utf-8") as f:
        return json.load(f)


def evaluate_query(
    query_data: dict,
    mode: str,
    top_k: int = 5,
):
    """
    Evaluate a single query.
    """

    query = query_data["query"]

    results = retrieve(
        query=query,
        top_k=top_k,
        mode=mode,
    )

    expected_sources = [
        source.lower()
        for source in query_data["expected_sources"]
    ]

    retrieved_sources = list(
        dict.fromkeys(
            document.metadata["source"].lower()
            for document in results
        )
    )

    precision = precision_at_k(
        retrieved_sources,
        expected_sources,
        top_k,
    )

    recall = recall_at_k(
        retrieved_sources,
        expected_sources,
        top_k,
    )

    mrr = mean_reciprocal_rank(
        retrieved_sources,
        expected_sources,
    )

    return {
        "query": query,
        "expected_sources": expected_sources,
        "retrieved_sources": retrieved_sources,
        "precision": round(precision, 3),
        "recall": round(recall, 3),
        "mrr": round(mrr, 3),
    }


def evaluate_dataset(
    mode: str,
    top_k: int = 5,
) -> list[dict]:
    """
    Evaluate every query in the dataset.
    """

    queries = load_queries()

    if not queries:
        raise ValueError("Evaluation dataset is empty.")

    results = []

    for query in queries:

        results.append(
            evaluate_query(
                query,
                mode,
                top_k,
            )
        )

    return results


def generate_report(
    query_results: list[dict],
    retriever_name: str,
    top_k: int,
) -> dict:
    """
    Generate evaluation report.
    """

    precision_scores = [
        result["precision"]
        for result in query_results
    ]

    recall_scores = [
        result["recall"]
        for result in query_results
    ]

    mrr_scores = [
        result["mrr"]
        for result in query_results
    ]

    report = {
        "retriever": retriever_name,
        "top_k": top_k,
        "queries": len(query_results),
        f"average_precision@{top_k}": round(
            sum(precision_scores) / len(precision_scores),
            3,
        ),
        f"average_recall@{top_k}": round(
            sum(recall_scores) / len(recall_scores),
            3,
        ),
        f"average_mrr@{top_k}": round(
            sum(mrr_scores) / len(mrr_scores),
            3,
        ),
        "results": query_results,
    }

    return report


def save_report(
    report: dict,
):
    """
    Save evaluation report.
    """

    reports_dir = (
        Path(__file__).parent
        / "reports"
    )

    reports_dir.mkdir(
        exist_ok=True
    )

    report_file = (
        reports_dir
        / f"{report['retriever']}.json"
    )

    with open(
        report_file,
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            report,
            f,
            indent=4,
        )

    print(f"\n Report saved: {report_file}\n")
    print(json.dumps(report, indent=4))


if __name__ == "__main__":

    TOP_K = 5

    RETRIEVERS = [
        "semantic",
        "hybrid",
        "hybrid_reranker",
    ]

    for mode in RETRIEVERS:

        query_results = evaluate_dataset(
            mode=mode,
            top_k=TOP_K,
        )

        report = generate_report(
            query_results=query_results,
            retriever_name=mode,
            top_k=TOP_K,
        )

        save_report(report)