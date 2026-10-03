from app.evaluation.system_evaluator import evaluate_system


def test_system_evaluator(monkeypatch):
    def fake_ask(
        question,
        documents,
        mode,
        owner_id,
        request_id,
    ):
        return {
            "answer": "Test answer",
            "sources": [],
        }

    monkeypatch.setattr(
        "app.evaluation.system_evaluator.ask",
        fake_ask,
    )

    result = evaluate_system(
        questions=[
            "Question 1",
            "Question 2",
        ],
        owner_id=1,
    )

    assert result["queries"]["total"] == 2
    assert result["queries"]["successful"] == 2
    assert result["queries"]["failed"] == 0
    assert result["queries"]["success_rate"] == 1.0

    assert result["provider"]["failures"] == 0
    assert result["provider"]["failure_rate"] == 0.0

    assert "p50_ms" in result["latency"]
    assert "p95_ms" in result["latency"]

    assert "hits" in result["cache"]
    assert "misses" in result["cache"]
    assert "hit_rate" in result["cache"]