import pytest

from app.evaluation.generation_evaluator import (
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