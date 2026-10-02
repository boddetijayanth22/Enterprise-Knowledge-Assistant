from collections.abc import Sequence


def precision_at_k(
    retrieved: Sequence[str | int],
    relevant: set[str | int],
    k: int,
) -> float:
    """
    Page-level Precision@K.

    Precision@K = relevant items in top K / K.
    """

    if k <= 0:
        raise ValueError("k must be greater than 0")

    top_k = list(retrieved[:k])

    if not top_k:
        return 0.0

    relevant_retrieved = sum(
        1 for item in top_k if item in relevant
    )

    return relevant_retrieved / k


def recall_at_k(
    retrieved: Sequence[str | int],
    relevant: set[str | int],
    k: int,
) -> float:
    """
    Page-level Recall@K.

    Recall@K = relevant pages retrieved in top K
               / total relevant pages.
    """

    if k <= 0:
        raise ValueError("k must be greater than 0")

    if not relevant:
        return 0.0

    top_k = set(retrieved[:k])

    relevant_retrieved = len(
        top_k.intersection(relevant)
    )

    return relevant_retrieved / len(relevant)


def reciprocal_rank(
    retrieved: Sequence[str | int],
    relevant: set[str | int],
) -> float:
    """
    Reciprocal rank of the first relevant page.
    """

    for rank, item in enumerate(retrieved, start=1):
        if item in relevant:
            return 1.0 / rank

    return 0.0


def mean_reciprocal_rank(
    results: Sequence[
        tuple[
            Sequence[str | int],
            set[str | int],
        ]
    ],
) -> float:
    """
    Mean Reciprocal Rank across multiple queries.
    """

    if not results:
        return 0.0

    reciprocal_ranks = [
        reciprocal_rank(
            retrieved,
            relevant,
        )
        for retrieved, relevant in results
    ]

    return sum(reciprocal_ranks) / len(reciprocal_ranks)