from langchain_core.documents import Document
from sentence_transformers import CrossEncoder

from app.utils.logger import logger


logger.info("Loading CrossEncoder model...")

MODEL = CrossEncoder(
    "cross-encoder/ms-marco-MiniLM-L-6-v2"
)

logger.info("CrossEncoder loaded.")


class CrossEncoderReranker:

    def __init__(self):
        self.model = MODEL

    def rerank(
        self,
        query: str,
        documents: list[Document],
        top_k: int = 5,
    ) -> list[Document]:

        if not documents:
            logger.info(
                "RERANKER INPUT | query=%s | candidates=0",
                query,
            )
            return []

        sentence_pairs = [
            (query, document.page_content)
            for document in documents
        ]

        scores = self.model.predict(sentence_pairs)

        ranked_documents = sorted(
            zip(documents, scores),
            key=lambda item: float(item[1]),
            reverse=True,
        )

        logger.info(
            "RERANKER INPUT | query=%s | candidates=%s",
            query,
            len(documents),
        )

        for rank, (document, score) in enumerate(
            ranked_documents,
            start=1,
        ):
            logger.info(
                "RERANKER RESULT | rank=%s | score=%.4f | source=%s | page=%s",
                rank,
                float(score),
                document.metadata.get("source"),
                document.metadata.get("page"),
            )

        selected_documents = []

        for document, score in ranked_documents[:top_k]:

            document.metadata["reranker_score"] = float(score)

            selected_documents.append(document)

        logger.info(
            "RERANKER OUTPUT | selected=%s | top_k=%s | best_score=%.4f",
            len(selected_documents),
            top_k,
            float(ranked_documents[0][1]),
        )

        return selected_documents