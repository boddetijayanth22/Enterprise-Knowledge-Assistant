from langchain_core.documents import Document
from sentence_transformers import CrossEncoder


class CrossEncoderReranker:

    def __init__(self):

        self.model = CrossEncoder(
            "cross-encoder/ms-marco-MiniLM-L-6-v2"
        )

    def rerank(
        self,
        query: str,
        documents: list[Document],
        top_k: int = 5,
    ) -> list[Document]:

        hybrid_results = ...

        reranker = CrossEncoderReranker()

        return reranker.rerank(
            query=query,
            documents=hybrid_results,
            top_k=top_k,
        )