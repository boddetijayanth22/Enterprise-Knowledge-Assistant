import pytest

from app.evaluation.generation_evaluator import (
    evidence_coverage,
    evaluate_generation,
    source_coverage,
)


def test_evidence_coverage():
    answer = (
        "Python is a high-level programming language. "
        "It abstracts low-level machine details."
    )

    facts = [
        "Python is a high-level programming language",
        "Python abstracts low-level machine details",
    ]

    assert evidence_coverage(
        answer,
        facts,
    ) == 1.0


def test_partial_evidence_coverage():
    answer = "Python is a high-level programming language."

    facts = [
        "Python is a high-level programming language",
        "Python abstracts low-level machine details",
    ]

    assert evidence_coverage(
        answer,
        facts,
    ) == 0.5


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
            "Python has numeric literals, string literals, "
            "boolean literals, collection literals, and special literals."
        ),
        sources=[
            {
                "file": "Python Programming Handbook.pdf",
                "page": 33,
            }
        ],
        expected_facts=[
            "numeric literals",
            "string literals",
            "boolean literals",
            "collection literals",
            "special literals",
        ],
        relevant_pages={33},
    )

    assert result["evidence_coverage"] == 1.0
    assert result["source_coverage"] == 1.0