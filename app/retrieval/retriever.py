from langchain_core.documents import Document
from app.config.settings import settings
from app.embeddings.embedding_model import get_embedding_model
from app.vectorstore.client import get_qdrant_client
from qdrant_client.models import (
    Filter,
    FieldCondition,
    MatchValue,
)


def retrieve(
    query: str,
    documents: list[str] | None = None,
    top_k: int = 5,
):
    """
    Retrieve the most relevent document chunks
    using semantic vector search.
    """

    search_filter = None

    if documents:

        search_filter = Filter(
            should=[
                FieldCondition(
                    key="source",
                    match=MatchValue(value=document),
                )
                for document in documents
            ]
        )

    embedding_model = get_embedding_model()

    query_vector = embedding_model.embed_query(query)

    client = get_qdrant_client()

    print("Selected documents:", documents)
    print("Filter:", search_filter)
    
    results = client.query_points(
        collection_name=settings.collection_name,
        query=query_vector,
        query_filter=search_filter,
        limit=top_k,
    ).points

    print("Results:",len(results))

    for result in results:
        print("Matched:", result.payload["source"])

    retrieved_documents = []

    for result in results:

        payload = result.payload

        retrieved_documents.append(
            Document(
                page_content=payload["text"],
                metadata={
                    "page": payload["page"],
                    "source": payload["source"],
                    "score": result.score,
                },
            )
        )

    return retrieved_documents