from langchain_core.prompts import ChatPromptTemplate

rag_prompt = ChatPromptTemplate.from_template(
    """
You are a helpful AI assistant.

Answer ONLY from the provided context.

If the answer is not present, say:

"I couldn't find the answer in the provided documents."

Context:
{context}

Question:
{question}

Answer:
"""
)