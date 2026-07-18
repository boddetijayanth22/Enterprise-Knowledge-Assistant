from rank_bm25 import BM25Okapi
from langchain_core.documents import Document

from app.retrieval.tokenizer import tokenize


class BM25Retriever:
    """
    BM25 lexical retriever.
    """

    def __init__(self):

        self.documents: list[Document] = []
        self.index: BM25Okapi | None = None

    def build_index(
        self,
        documents: list[Document],
    ) -> None:

        self.documents = documents

        tokenized_documents = [
            tokenize(document.page_content)
            for document in documents
        ]

        self.index = BM25Okapi(tokenized_documents)

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
    ) -> list[Document]:

        if self.index is None:

            raise ValueError(
                "BM25 index has not been built."
            )

        tokenized_query = tokenize(query)

        scores = self.index.get_scores(tokenized_query)

        ranked = sorted(
            zip(scores, self.documents),
            key=lambda x: x[0],
            reverse=True,
        )

        return [
            document
            for _, document in ranked[:top_k]
        ]