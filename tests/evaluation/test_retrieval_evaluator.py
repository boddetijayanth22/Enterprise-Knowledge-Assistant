from unittest.mock import patch

from langchain_core.documents import Document

from app.evaluation.retrieval_evaluator import evaluate_query


def test_evaluate_query():
    mocked_results = [
        Document(
            page_content="Python high-level language",
            metadata={
                "source": "Python Programming Handbook.pdf",
                "page": 6,
            },
        ),
        Document(
            page_content="Python introduction",
            metadata={
                "source": "Python Programming Handbook.pdf",
                "page": 10,
            },
        ),
        Document(
            page_content="Unrelated content",
            metadata={
                "source": "Python Programming Handbook.pdf",
                "page": 20,
            },
        ),
    ]

    with patch(
        "app.evaluation.retrieval_evaluator.retrieve",
        return_value=mocked_results,
    ):
        result = evaluate_query(
            question="What does it mean that Python is a high-level language?",
            relevant_pages={7},
            owner_id=1,
            documents=["Python Programming Handbook.pdf"],
            k=3,
        )

    assert result["retrieved_pages"] == [7, 11, 21]
    assert result["relevant_pages"] == [7]

    assert result["precision_at_k"] == 1 / 3
    assert result["recall_at_k"] == 1.0
    assert result["reciprocal_rank"] == 1.0