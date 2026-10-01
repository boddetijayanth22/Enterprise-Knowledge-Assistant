import time
from pathlib import Path
from app.config.settings import settings

from app.utils.logger import logger
from app.security.output_guard import (
    detect_secret_leakage,
    redact_secret_leakage,
)
from app.llm.router import get_llm
from app.llm.exceptions import LLMProviderError
from app.prompts.rag_prompt import rag_prompt
from app.security.prompt_injection import detect_prompt_injection
from app.security.retrieval_guard import detect_retrieval_injection
from app.security.audit import log_security_event
from app.retrieval.retriever import retrieve
from app.privacy.classifier import DataClassification
from app.privacy.detector import detect_sensitive_data
from app.privacy.redactor import redact_sensitive_data
from app.privacy.policy import PrivacyAction, evaluate_policy
from app.observability.metrics import metrics
from app.cache.query_cache import query_cache

def ask(
    question: str,
    documents: list[str] | None,
    mode: str,
    owner_id: int,
    request_id: str | None = None,
):

    injection_result = detect_prompt_injection(question)

    if injection_result["is_injection"]:
        metrics.record_security_block()

        log_security_event(
            event_type="PROMPT_INJECTION",
            owner_id=owner_id,
            request_id=request_id,
            action="BLOCK",
            result="DETECTED",
            finding_count=len(injection_result["findings"]),
        )

        logger.warning(
            "Prompt injection blocked | owner_id=%s | findings=%s",
            owner_id,
            len(injection_result["findings"]),
        )

        return {
            "answer": (
                "This request was blocked because it contains "
                "an unsafe instruction pattern."
            ),
            "sources": [],
        }

    if documents == []:
        logger.info(
            "No documents selected | "
            "owner_id=%s | "
            "request_id=%s",
            owner_id,
            request_id,
        )

        return {
            "answer": (
                "Please select at least one document "
                "before asking a question."
            ),
            "sources": [],
        }

    cached_result = query_cache.get(
        question=question,
        documents=documents,
        mode=mode,
        owner_id=owner_id,
    )

    if cached_result is not None:
        logger.info(
            "query_cache_hit | "
            "owner_id=%s | "
            "request_id=%s",
            owner_id,
            request_id,
        )

        return cached_result

    logger.info(
        "query_cache_miss | "
        "owner_id=%s | "
        "request_id=%s",
        owner_id,
        request_id,
    )

    retrieved_docs = retrieve(
        query=question,
        owner_id=owner_id,
        documents=documents,
        mode=mode,
    )

    retrieval_injection_findings = 0

    for doc in retrieved_docs:
        result = detect_retrieval_injection(
            doc.page_content
        )

        if result["is_injection"]:
            retrieval_injection_findings += len(
                result["findings"]
            )

    if retrieval_injection_findings:
        metrics.record_security_block()

        log_security_event(
            event_type="INDIRECT_PROMPT_INJECTION",
            owner_id=owner_id,
            request_id=request_id,
            action="BLOCK",
            result="DETECTED",
            finding_count=retrieval_injection_findings,
        )

        logger.warning(
            "Indirect prompt injection blocked | "
            "owner_id=%s | findings=%s",
            owner_id,
            retrieval_injection_findings,
        )

        return {
            "answer": (
                "This request cannot be processed because "
                "the retrieved content contains an unsafe "
                "instruction pattern."
            ),
            "sources": [],
        }

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

    metrics.record_privacy_action(policy_action.value)

    logger.info(
        "Privacy policy decision | classification=%s | "
        "sensitive_data_detected=%s | action=%s",
        classification,
        sensitive_result["has_sensitive_data"],
        policy_action.value,
    )

    logger.info(
        "llm_policy_decision | "
        "owner_id=%s | "
        "request_id=%s | "
        "provider=%s | "
        "model=%s | "
        "classification=%s | "
        "action=%s",
        owner_id,
        request_id,
        settings.llm_provider,
        settings.llm_model,
        classification,
        policy_action.value,
    )

    log_security_event(
        event_type="PRIVACY_POLICY",
        owner_id=owner_id,
        request_id=request_id,
        action=policy_action.value,
        result=(
            "SENSITIVE_DATA_DETECTED"
            if sensitive_result["has_sensitive_data"]
            else "CLEAR"
        ),
        finding_count=len(sensitive_result["findings"]),
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

    llm_start_time = time.perf_counter()

    try:
        response = llm.invoke(prompt.to_string())
    except LLMProviderError:
        logger.error(
            "llm_provider_failure | "
            "request_id=%s | "
            "owner_id=%s",
            request_id,
            owner_id,
        )

        return {
            "answer": (
                "The AI service is temporarily unavailable. "
                "Please try again shortly."
            ),
            "sources": [],
        }

    llm_latency_ms = round(
        (time.perf_counter() - llm_start_time) * 1000,
        2,
    )

    metrics.record_llm(llm_latency_ms)

    logger.info(
        "llm_completed | "
        "owner_id=%s | "
        "request_id=%s | "
        "provider=%s | "
        "model=%s | "
        "latency_ms=%s",
        owner_id,
        request_id,
        settings.llm_provider,
        settings.llm_model,
        llm_latency_ms,
    )

    answer = response.content

    secret_result = detect_secret_leakage(answer)

    if secret_result["has_secret"]:
        log_security_event(
            event_type="SECRET_LEAKAGE",
            owner_id=owner_id,
            request_id=request_id,
            action="REDACT",
            result="DETECTED",
            finding_count=len(secret_result["findings"]),
        )

        answer = redact_secret_leakage(answer)

        logger.warning(
            "LLM output secret leakage detected | owner_id=%s | findings=%s",
            owner_id,
            len(secret_result["findings"]),
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
            
    result = {
        "answer": answer,
        "sources": sources,
    }

    query_cache.set(
        question=question,
        documents=documents,
        mode=mode,
        owner_id=owner_id,
        value=result,
    )

    logger.info(
        "query_cache_set | "
        "owner_id=%s | "
        "request_id=%s",
        owner_id,
        request_id,
    )

    return result