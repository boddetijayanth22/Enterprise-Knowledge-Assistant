from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
)


def split_documents(documents: list[Document]) -> list[Document]:
    """
    Split LangChain Documents into smaller chunks.
    """
    chunks = text_splitter.split_documents(documents)
    return chunks