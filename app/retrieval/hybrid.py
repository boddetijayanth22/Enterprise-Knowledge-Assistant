from langchain_core.documents import Document


def _document_key(document: Document) -> tuple[str, int, str]:
    """
    Create a unique key for an individual chunk.

    Source + page alone is not sufficient because multiple
    chunks can originate from the same PDF page.
    """

    return (
        document.metadata["source"],
        document.metadata["page"],
        document.page_content,
    )


def reciprocal_rank_fusion(
    semantic_results: list[Document],
    bm25_results: list[Document],
    k: int = 60,
) -> list[Document]:
    """
    Combine ranked retrieval lists using Reciprocal Rank Fusion.

    Each individual chunk is treated as a separate retrieval unit.
    """

    scores: dict[tuple[str, int, str], float] = {}
    document_map: dict[tuple[str, int, str], Document] = {}

    for rank, document in enumerate(
        semantic_results,
        start=1,
    ):
        key = _document_key(document)

        scores[key] = (
            scores.get(key, 0.0)
            + 1.0 / (k + rank)
        )

        document_map[key] = document

    for rank, document in enumerate(
        bm25_results,
        start=1,
    ):
        key = _document_key(document)

        scores[key] = (
            scores.get(key, 0.0)
            + 1.0 / (k + rank)
        )

        document_map[key] = document

    ranked = sorted(
        scores.items(),
        key=lambda item: item[1],
        reverse=True,
    )

    return [
        document_map[key]
        for key, _ in ranked
    ]