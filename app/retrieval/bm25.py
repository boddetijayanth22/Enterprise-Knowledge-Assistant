from langchain_core.documents import Document


class BM25Retriever:
    """
    BM25 lexical retriever.
    """

    def __init__(self):

        self.documents: list[Document] = []

        self.index = None

    def build_index(
        self,
        documents: list[Document],
    ) -> None:

        pass

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
    ) -> list[Document]:

        pass