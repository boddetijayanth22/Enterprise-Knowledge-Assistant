from collections.abc import Sequence


PROVIDER_FAILURE_MESSAGE = (
    "The AI service is temporarily unavailable. "
    "Please try again shortly."
)


def normalize_text(text: str) -> str:
    return " ".join(text.lower().split())


def fact_supported(
    answer: str,
    fact: Sequence[str],
) -> bool:
    answer_normalized = normalize_text(answer)

    return all(
        term.lower() in answer_normalized
        for term in fact
    )


def evidence_coverage(
    answer: str,
    expected_facts: Sequence[Sequence[str]],
) -> float:
    if not expected_facts:
        return 0.0

    supported = sum(
        fact_supported(answer, fact)
        for fact in expected_facts
    )

    return supported / len(expected_facts)


def source_coverage(
    returned_sources: Sequence[dict],
    relevant_pages: set[int],
) -> float:
    if not relevant_pages:
        return 0.0

    returned_pages = {
        int(source["page"])
        for source in returned_sources
    }

    matched_pages = returned_pages.intersection(
        relevant_pages
    )

    return len(matched_pages) / len(relevant_pages)


def evaluate_generation(
    question,
    answer,
    sources,
    expected_facts,
    relevant_pages,
) -> dict:
    return {
        "question": question,
        "answer": answer,
        "sources": list(sources),
        "evidence_coverage": evidence_coverage(
            answer,
            expected_facts,
        ),
        "source_coverage": source_coverage(
            sources,
            relevant_pages,
        ),
    }


def is_provider_failure(response: dict) -> bool:
    return (
        response.get("answer") == PROVIDER_FAILURE_MESSAGE
        and not response.get("sources")
    )


def evaluate_dataset(
    dataset,
    ask_fn,
    owner_id,
    documents,
    mode="hybrid_reranker",
) -> dict:
    results = []
    successful_results = []
    provider_failures = 0

    for item in dataset:
        response = ask_fn(
            question=item["question"],
            documents=documents,
            mode=mode,
            owner_id=owner_id,
        )

        if is_provider_failure(response):
            provider_failures += 1

            results.append(
                {
                    "question": item["question"],
                    "answer": response["answer"],
                    "sources": list(
                        response.get("sources", [])
                    ),
                    "status": "PROVIDER_FAILURE",
                    "evidence_coverage": None,
                    "source_coverage": None,
                }
            )

            continue

        result = evaluate_generation(
            question=item["question"],
            answer=response["answer"],
            sources=response["sources"],
            expected_facts=item["expected_facts"],
            relevant_pages=set(
                item["relevant_pages"]
            ),
        )

        result["status"] = "SUCCESS"

        results.append(result)
        successful_results.append(result)

    successful_queries = len(successful_results)

    evidence_average = (
        sum(
            result["evidence_coverage"]
            for result in successful_results
        ) / successful_queries
        if successful_queries
        else 0.0
    )

    source_average = (
        sum(
            result["source_coverage"]
            for result in successful_results
        ) / successful_queries
        if successful_queries
        else 0.0
    )

    return {
        "mode": mode,
        "queries": len(results),
        "successful_queries": successful_queries,
        "provider_failures": provider_failures,
        "evidence_coverage": evidence_average,
        "source_coverage": source_average,
        "results": results,
    }