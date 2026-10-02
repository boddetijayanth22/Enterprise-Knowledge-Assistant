import pytest

from app.evaluation.retrieval_metrics import (
    mean_reciprocal_rank,
    precision_at_k,
    recall_at_k,
    reciprocal_rank,
)


def test_precision_at_k_uses_k_as_denominator():
    retrieved = [7, 11, 6, 5]
    relevant = {7}

    assert precision_at_k(
        retrieved,
        relevant,
        5,
    ) == 0.2


def test_recall_at_k():
    retrieved = [7, 11, 6, 5]
    relevant = {7, 9}

    assert recall_at_k(
        retrieved,
        relevant,
        5,
    ) == 0.5


def test_reciprocal_rank():
    retrieved = [11, 9, 7]
    relevant = {7}

    assert reciprocal_rank(
        retrieved,
        relevant,
    ) == pytest.approx(1 / 3)


def test_reciprocal_rank_when_not_found():
    retrieved = [11, 9, 8]
    relevant = {7}

    assert reciprocal_rank(
        retrieved,
        relevant,
    ) == 0.0


def test_mean_reciprocal_rank():
    results = [
        ([7, 11], {7}),
        ([11, 9, 7], {7}),
    ]

    assert mean_reciprocal_rank(
        results
    ) == pytest.approx(
        (1.0 + 1 / 3) / 2
    )