from collections.abc import Sequence


def normalize_text(text: str) -> str:
    return " ".join(text.lower().split())


def fact_supported(answer: str, fact: str) -> bool:
    answer_normalized = normalize_text(answer)
    fact_normalized = normalize_text(fact)

    if fact_normalized in answer_normalized:
        return True

    # Handle simple reference variation:
    # "Python abstracts..." vs "It abstracts..."
    if fact_normalized.startswith("python "):
        shortened_fact = fact_normalized[len("python "):]

        if f"it {shortened_fact}" in answer_normalized:
            return True

    return False


def evidence_coverage(
    answer: str,
    expected_facts: Sequence[str],
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

    matched_pages = returned_pages.intersection(relevant_pages)

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


def evaluate_dataset(
    dataset,
    ask_fn,
    owner_id,
    documents,
    mode="hybrid_reranker",
) -> dict:
    results = []

    for item in dataset:
        response = ask_fn(
            question=item["question"],
            documents=documents,
            mode=mode,
            owner_id=owner_id,
        )

        result = evaluate_generation(
            question=item["question"],
            answer=response["answer"],
            sources=response["sources"],
            expected_facts=item["expected_facts"],
            relevant_pages=set(item["relevant_pages"]),
        )

        results.append(result)

    return {
        "mode": mode,
        "queries": len(results),
        "evidence_coverage": (
            sum(
                result["evidence_coverage"]
                for result in results
            ) / len(results)
            if results
            else 0.0
        ),
        "source_coverage": (
            sum(
                result["source_coverage"]
                for result in results
            ) / len(results)
            if results
            else 0.0
        ),
        "results": results,
    }