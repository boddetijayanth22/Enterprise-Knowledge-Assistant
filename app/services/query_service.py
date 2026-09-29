from pathlib import Path
from app.utils.logger import logger
from app.llm.router import get_llm
from app.prompts.rag_prompt import rag_prompt
from app.retrieval.retriever import retrieve
from app.privacy.classifier import DataClassification
from app.privacy.detector import detect_sensitive_data
from app.privacy.redactor import redact_sensitive_data
from app.privacy.policy import PrivacyAction, evaluate_policy


def ask(
    question: str,
    documents: list[str] | None,
    mode: str,
    owner_id: int,
):

    retrieved_docs = retrieve(
        query=question,
        owner_id=owner_id,
        documents=documents,
        mode=mode,
    )

    context = "\n\n".join(
        doc.page_content
        for doc in retrieved_docs
    )

    classifications = [
        doc.metadata.get(
            "classification",
            DataClassification.INTERNAL.value,
        )
        for doc in retrieved_docs
    ]

    if DataClassification.RESTRICTED.value in classifications:
        classification = DataClassification.RESTRICTED.value
    elif DataClassification.CONFIDENTIAL.value in classifications:
        classification = DataClassification.CONFIDENTIAL.value
    elif DataClassification.INTERNAL.value in classifications:
        classification = DataClassification.INTERNAL.value
    else:
        classification = DataClassification.PUBLIC.value

    sensitive_result = detect_sensitive_data(context)

    policy_action = evaluate_policy(
        classification=classification,
        has_sensitive_data=sensitive_result["has_sensitive_data"],
    )

    logger.info(
        "Privacy policy decision | classification=%s | "
        "sensitive_data_detected=%s | action=%s",
        classification,
        sensitive_result["has_sensitive_data"],
        policy_action.value,
    )

    if policy_action == PrivacyAction.BLOCK:
        return {
            "answer": (
                "This request cannot be processed because the "
                "retrieved information is classified as restricted."
            ),
            "sources": [],
        }

    if policy_action == PrivacyAction.REDACT:
        context = redact_sensitive_data(context)

    prompt = rag_prompt.invoke(
        {
            "context": context,
            "question": question,
        }
    )

    llm = get_llm()

    response = llm.invoke(
        prompt.to_string()
    )

    sources = []

    seen = set()

    for doc in retrieved_docs:

        file = Path(
            doc.metadata["source"]
        ).as_posix()

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

    return {
        "answer": response.content,
        "sources": sources,
    }