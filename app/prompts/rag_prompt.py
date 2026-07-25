from langchain_core.prompts import ChatPromptTemplate

rag_prompt = ChatPromptTemplate.from_template(
    """
You are a helpful AI assistant.

Answer ONLY using the provided context.

If the context contains related information that partially answers the question, provide the best possible answer from that information.

Only say "I couldn't find the answer in the provided documents." when the retrieved context is completely unrelated.

Context:
{context}

Question:
{question}

Answer:
"""
)