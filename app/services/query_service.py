from app.llm.gemini import get_llm
from app.prompts.rag_prompt import rag_prompt
from app.retrieval.retriever import retrieve
from pathlib import Path

def ask(question, documents, mode):
    
    retrieved_docs = retrieve(
        question,
        documents,
        mode = mode,
    )

    context = "\n\n".join(
        doc.page_content
        for doc in retrieved_docs
    )

    prompt = rag_prompt.invoke(
        {
            "context": context,
            "question": question,
        }
    )

    llm = get_llm()

    response = llm.invoke(prompt)

    sources = []

    seen = set()

    print("=" * 80)
    print("Retrieved Context")
    print(context)
    print("=" * 80)

    for doc in retrieved_docs:
        file = Path(doc.metadata["source"]).as_posix()
        page = doc.metadata["page"]
    
        key = (file, page)

        if key not in seen:
            seen.add(key)

            sources.append(
                {
                    "file": file,
                    "page": page + 1,
                }
            )

    return{
        "answer": response.content,
        "sources": sources,
    }