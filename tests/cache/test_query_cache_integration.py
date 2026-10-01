from app.services.query_service import ask


def test_cached_query_skips_retrieval_and_llm(monkeypatch):
    retrieval_calls = {"count": 0}
    llm_calls = {"count": 0}

    class FakeLLM:
        def invoke(self, prompt):
            llm_calls["count"] += 1

            class Response:
                content = "Test answer"

            return Response()

    def fake_retrieve(**kwargs):
        retrieval_calls["count"] += 1

        class Doc:
            page_content = "Test context"
            metadata = {
                "source": "test.pdf",
                "page": 0,
                "classification": "INTERNAL",
            }

        return [Doc()]

    monkeypatch.setattr(
        "app.services.query_service.retrieve",
        fake_retrieve,
    )

    monkeypatch.setattr(
        "app.services.query_service.get_llm",
        lambda: FakeLLM(),
    )

    first_result = ask(
        question="What is this?",
        documents=["test.pdf"],
        mode="semantic",
        owner_id=999,
        request_id="request-1",
    )

    second_result = ask(
        question="What is this?",
        documents=["test.pdf"],
        mode="semantic",
        owner_id=999,
        request_id="request-2",
    )

    assert first_result == second_result

    assert retrieval_calls["count"] == 1
    assert llm_calls["count"] == 1