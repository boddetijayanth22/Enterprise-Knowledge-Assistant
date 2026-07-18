from langchain_core.documents import Document


def reciprocal_rank_fusion(
    semantic_results: list[Document],
    bm25_results: list[Document],
    k: int = 60,
) -> list[Document]:
    """
    Combine ranked lists using Reciprocal Rank Fusion (RRF).
    """

    scores = {}

    document_map = {}

    for rank, document in enumerate(semantic_results):

        key = (
            document.metadata["source"],
            document.metadata["page"],
        )

        scores[key] = scores.get(key, 0) + 1 / (k + rank + 1)

        document_map[key] = document

    for rank, document in enumerate(bm25_results):

        key = (
            document.metadata["source"],
            document.metadata["page"],
        )

        scores[key] = scores.get(key, 0) + 1 / (k + rank + 1)

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