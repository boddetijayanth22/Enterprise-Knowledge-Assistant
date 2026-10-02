import pytest

from app.evaluation.generation_evaluator import (
    concept_supported,
    evidence_coverage,
    evaluate_dataset,
    evaluate_generation,
    fact_supported,
    is_provider_failure,
    source_coverage,
)


def test_evidence_coverage():
    answer = (
        "Python is a high-level programming language. "
        "It abstracts low-level machine details."
    )

    facts = [
        ["python", "high-level"],
        ["abstracts", "low-level"],
    ]

    assert evidence_coverage(answer, facts) == 1.0


def test_partial_evidence_coverage():
    answer = "Python is a high-level programming language."

    facts = [
        ["python", "high-level"],
        ["abstracts", "low-level"],
    ]

    assert evidence_coverage(answer, facts) == 0.5


def test_source_coverage():
    sources = [
        {"file": "Python Programming Handbook.pdf", "page": 33},
        {"file": "Python Programming Handbook.pdf", "page": 37},
    ]

    assert source_coverage(
        sources,
        {33},
    ) == 1.0


def test_partial_source_coverage():
    sources = [
        {"file": "Python Programming Handbook.pdf", "page": 33},
    ]

    assert source_coverage(
        sources,
        {33, 34},
    ) == 0.5


def test_evaluate_generation():
    result = evaluate_generation(
        question="What are the five kinds of literals in Python?",
        answer=(
            "Python has numeric, string, boolean, "
            "collection, and special literals."
        ),
        sources=[
            {
                "file": "Python Programming Handbook.pdf",
                "page": 33,
            }
        ],
        expected_facts=[
            ["numeric"],
            ["string"],
            ["boolean"],
            ["collection"],
            ["special"],
        ],
        relevant_pages={33},
    )

    assert result["evidence_coverage"] == 1.0
    assert result["source_coverage"] == 1.0


def test_provider_failure_is_detected():
    response = {
        "answer": (
            "The AI service is temporarily unavailable. "
            "Please try again shortly."
        ),
        "sources": [],
    }

    assert is_provider_failure(response) is True


def test_successful_queries_are_separated_from_provider_failures():
    dataset = [
        {
            "question": "Q1",
            "expected_facts": [["python"]],
            "relevant_pages": [7],
        },
        {
            "question": "Q2",
            "expected_facts": [["python"]],
            "relevant_pages": [8],
        },
    ]

    responses = [
        {
            "answer": "Python is a programming language.",
            "sources": [{"page": 7}],
        },
        {
            "answer": (
                "The AI service is temporarily unavailable. "
                "Please try again shortly."
            ),
            "sources": [],
        },
    ]

    def fake_ask(**kwargs):
        return responses.pop(0)

    result = evaluate_dataset(
        dataset=dataset,
        ask_fn=fake_ask,
        owner_id=1,
        documents=["test.pdf"],
    )

    assert result["queries"] == 2
    assert result["successful_queries"] == 1
    assert result["provider_failures"] == 1
    assert result["evidence_coverage"] == 1.0
    assert result["source_coverage"] == 1.0


def test_all_provider_failures_return_zero_quality_metrics():
    dataset = [
        {
            "question": "Q1",
            "expected_facts": [["python"]],
            "relevant_pages": [7],
        },
        {
            "question": "Q2",
            "expected_facts": [["python"]],
            "relevant_pages": [8],
        },
    ]

    def fake_ask(**kwargs):
        return {
            "answer": (
                "The AI service is temporarily unavailable. "
                "Please try again shortly."
            ),
            "sources": [],
        }

    result = evaluate_dataset(
        dataset=dataset,
        ask_fn=fake_ask,
        owner_id=1,
        documents=["test.pdf"],
    )

    assert result["queries"] == 2
    assert result["successful_queries"] == 0
    assert result["provider_failures"] == 2
    assert result["evidence_coverage"] == 0.0
    assert result["source_coverage"] == 0.0


def test_concept_alias_is_supported():
    answer = (
        "Python is a high-level language because "
        "it abstracts away low-level implementation details."
    )

    assert concept_supported(answer, "abstract")


def test_immutable_concept_accepts_equivalent_wording():
    answer = (
        "Strings cannot be changed after they are created."
    )

    assert concept_supported(answer, "immutable")


def test_slicing_concept_accepts_equivalent_wording():
    answer = (
        "Slicing extracts a portion of a string "
        "using start and stop positions."
    )

    assert concept_supported(answer, "slicing")


def test_fact_requires_all_concepts():
    answer = (
        "Python is a high-level language that "
        "abstracts away low-level details."
    )

    assert fact_supported(
        answer,
        ["python", "high-level", "abstract"],
    )


def test_unknown_concept_falls_back_to_literal_match():
    answer = "Python supports recursion."

    assert concept_supported(answer, "recursion")


def test_unicode_hyphen_is_normalized():
    answer = (
        "Python is a high-level language that "
        "hides low-level implementation details."
    )

    assert concept_supported(answer, "high-level")
    assert concept_supported(answer, "abstract")


def test_high_level_language_accepts_abstraction_wording():
    answer = (
        "A high-level language is one that sits far above "
        "the computer's raw machine code. With Python you don't "
        "have to think about memory addresses, registers, or how "
        "data is physically stored. The language handles the "
        "low-level details for you."
    )

    assert concept_supported(answer, "high-level")
    assert concept_supported(answer, "abstract")


def test_compiler_interpreter_accepts_equivalent_wording():
    answer = (
        "A compiler translates the entire program into machine code "
        "before it runs. An interpreter reads the source code as it "
        "goes and executes it."
    )

    assert concept_supported(answer, "compiler")
    assert concept_supported(answer, "interpreter")


def test_immutable_accepts_alter_wording():
    answer = (
        "Once a string has been created you cannot alter any of "
        "its characters in place."
    )

    assert concept_supported(answer, "immutable")


def test_append_extend_accepts_element_wording():
    answer = (
        "append adds a single element to the end of a list, "
        "while extend adds each element individually."
    )

    assert concept_supported(answer, "append")
    assert concept_supported(answer, "extend")


def test_low_level_concept_accepts_machine_code_wording():
    answer = (
        "A high-level language hides low-level details "
        "such as machine code and memory management."
    )

    assert concept_supported(answer, "low-level")