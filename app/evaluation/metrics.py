from typing import List

def precision_at_k(
    retrieved_sources: List[str],
    expected_sources: List[str],
    k: int = 5,
) -> float:
    """
    Precision@K
    """

    retrieved = retrieved_sources[:k]

    relevant = sum(
        source in expected_sources
        for source in retrieved
    )

    return relevant / len(retrieved) if retrieved else 0.0


def recall_at_k(
    retrieved_sources: List[str],
    expected_sources: List[str],
    k: int = 5,
) -> float:
    """
    Recall@K
    """

    retrieved = retrieved_sources[:k]

    relevant = sum(
        source in expected_sources
        for source in retrieved
    )

    return (
        relevant / len(expected_sources)
        if expected_sources
        else 0.0
    )


def mean_reciprocal_rank(
    retrieved_sources: List[str],
    expected_sources: List[str],
) -> float:
    """
    Mean Reciprocal Rank
    """

    for rank, source in enumerate(retrieved_sources, start=1):

        if source in expected_sources:
            return 1 / rank

    return 0.0