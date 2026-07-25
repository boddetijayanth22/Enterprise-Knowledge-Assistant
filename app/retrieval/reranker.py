from langchain_core.documents import Document
from sentence_transformers import CrossEncoder
from app.utils.logger import logger

logger.info("Loading CrossEncoder model...")

MODEL = CrossEncoder(
    "cross-encoder/ms-marco-MiniLM-L-6-v2"
)

logger.info("Loading CrossEncoder loaded.")


class CrossEncoderReranker:

    def __init__(self):
        self.model = MODEL

    def rerank(
        self,
        query: str,
        documents: list[Document],
        top_k: int = 5,
    ) -> list[Document]:

        sentence_pairs = [
            (query, document.page_content)
            for document in documents
        ]

        scores = self.model.predict(sentence_pairs)

        ranked_documents = sorted(
            zip(documents, scores),
            key=lambda item: item[1],
            reverse=True,
        )

        reranked_documents = []

        for document, score in ranked_documents[:top_k]:
            document.metadata["reranker_score"] = float(score)
            reranked_documents.append(document)

        return reranked_documents