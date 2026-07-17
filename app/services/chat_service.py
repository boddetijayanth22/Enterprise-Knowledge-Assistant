from app.retrieval.retriever import retrieve


def chat(question: str):

    documents = retrieve(question)

    print("\nTop Retrieved Chunks\n")

    for i, doc in enumerate(documents, start=1):

        print("=" * 60)

        print(f"Result {i}")

        print(f"Score : {doc.metadata['score']:.4f}")

        print(f"Page  : {doc.metadata['page']}")

        print(doc.page_content[:300])

        print()