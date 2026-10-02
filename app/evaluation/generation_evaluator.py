from collections.abc import Sequence


PROVIDER_FAILURE_MESSAGE = (
    "The AI service is temporarily unavailable. "
    "Please try again shortly."
)


CONCEPT_ALIASES = {
    "python": [
        "python",
    ],
    "high-level": [
        "high-level",
        "high level",
    ],
    "abstract": [
        "abstract",
        "abstraction",
        "hides low-level details",
        "hide low-level details",
        "hides low-level implementation details",
        "hide low-level implementation details",
        "handles the low-level details",
        "handles low-level details",        
        "without having to think about",
        "don't have to think about",
        "doesn't have to think about",
        "do not have to think about",
    ],
    "low-level-details": [
        "low-level details",
        "low level details",
        "low-level operations",
        "low level operations",
        "machine code",
        "machine-level operations",
        "machine level operations",
    ],
    "procedural": [
        "procedural",
        "procedural programming",
    ],
    "object-oriented": [
        "object-oriented",
        "object oriented",
        "oop",
    ],
    "functional": [
        "functional",
        "functional programming",
    ],
    "compiler": [
        "compiler",
        "compiled",
        "compilation",
    ],
    "translates-before-execution": [
        "translates the entire program into machine language before it runs",
        "translates the entire program before it runs",
        "translates the entire program before execution",
        "translates the whole program before execution",
        "translates the program before it runs",
    ],
    "interpreter": [
        "interpreter",
        "interpreted",
        "interpretation",
    ],
    "executes-during-translation": [
        "executes it as it goes",
        "executes as it goes",
        "executes each part as it goes",
        "translating each piece on the fly",
        "executes on the fly",
        "reads the code and carries out each part as it goes",
    ],
    "numeric": [
        "numeric",
        "number",
        "numbers",
    ],
    "string": [
        "string",
        "strings",
    ],
    "boolean": [
        "boolean",
        "bool",
        "true",
        "false",
    ],
    "collection": [
        "collection",
        "collections",
    ],
    "special": [
        "special",
    ],
    "none": [
        "none",
        "none value",
    ],
    "absence-of-value": [
        "absence of a value",
        "absence",
        "no value",
        "nothing here",
        "no actual value",
        "value is missing",
        "not applicable",
    ],
    "zero": [
        "zero",
    ],
    "numeric-value": [
        "numeric value",
        "numeric",
        "integer",
        "int",
        "float",
        "quantity is zero",
    ],
    "immutable": [
        "immutable",
        "unchangeable",
        "cannot be changed",
        "cannot change",
        "cannot be altered",
        "cannot alter",
        "cannot be modified",
        "cannot modify",
        "cannot reach into",
        "characters cannot be changed",
        "characters cannot be altered",
    ],
    "cannot-modify-existing-string": [
        "characters cannot be altered in place",
        "characters cannot be changed",
        "characters cannot be altered",
        "cannot be altered in place",
        "cannot be changed",
        "cannot be modified",
        "cannot modify",
        "cannot reach into the string and change",
    ],
    "slicing": [
        "slicing",
        "slice",
    ],
    "portion-of-string": [
        "portion of a string",
        "stretch of characters",
        "take a stretch of characters",
        "substring",
    ],
    "start": [
        "start",
        "starting index",
        "start index",
    ],
    "stop": [
        "stop",
        "stopping index",
        "stop index",
    ],
    "append": [
        "append",
    ],
    "single-element": [
        "single element",
        "single item",
        "one item",
        "one new element",
    ],
    "extend": [
        "extend",
    ],
    "multiple-elements": [
        "multiple elements",
        "multiple items",
        "each of its elements",
        "each of its items",
        "elements individually",
        "items individually",
    ],
    "tuple": [
        "tuple",
        "tuples",
    ],
    "ordered": [
        "ordered",
        "order",
        "maintains order",
        "fixed position",
    ],
    "set": [
        "set",
        "sets",
    ],
    "unique": [
        "unique",
        "unique values",
        "unique elements",
        "uniqueness",
    ],
    "dictionary": [
        "dictionary",
        "dictionaries",
        "dict",
    ],
    "key-value": [
        "key-value",
        "key value",
        "key to values",
        "keys to values",
        "mapping of keys to values",
    ],
    "key": [
        "key",
        "keys",
    ],
    "value": [
        "value",
        "values",
    ],
    "excluded": [
        "excluded",
        "exclude",
        "not included",
        "does not include",
        "does not appear",
        "left out",
    ],
    "range": [
        "range",
    ],
    "starts-before-stop": [
        "stops before its stop index",
        "stops before the stop",
        "stops before 5",
        "up to but not including",
        "up to, but not including",
    ],
}


def normalize_text(text: str) -> str:
    normalized = text.lower()

    normalized = (
        normalized
        .replace("\u2011", "-")
        .replace("\u2013", "-")
        .replace("\u2014", "-")
        .replace("\u2212", "-")
        .replace("\u00a0", " ")
    )

    return " ".join(normalized.split())


def concept_supported(
    answer: str,
    concept: str,
) -> bool:
    answer_normalized = normalize_text(answer)

    aliases = CONCEPT_ALIASES.get(
        concept.lower(),
        [concept],
    )

    return any(
        alias.lower() in answer_normalized
        for alias in aliases
    )


def fact_supported(
    answer: str,
    fact: Sequence[str],
) -> bool:
    return all(
        concept_supported(answer, concept)
        for concept in fact
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
            relevant_pages=set(item["relevant_pages"]),
        )

        result["status"] = "SUCCESS"

        results.append(result)
        successful_results.append(result)

    successful_queries = len(successful_results)

    evidence_average = (
        sum(
            result["evidence_coverage"]
            for result in successful_results
        )
        / successful_queries
        if successful_queries
        else 0.0
    )

    source_average = (
        sum(
            result["source_coverage"]
            for result in successful_results
        )
        / successful_queries
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