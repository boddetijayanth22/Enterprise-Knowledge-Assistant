from app.llm.exceptions import LLMProviderError
from app.services.query_service import ask


def test_query_returns_safe_response_when_llm_provider_fails(monkeypatch):
    class FakeLLM:
        def invoke(self, prompt):
            raise LLMProviderError("openrouter")

    monkeypatch.setattr(
        "app.services.query_service.get_llm",
        lambda: FakeLLM(),
    )

    monkeypatch.setattr(
        "app.services.query_service.retrieve",
        lambda **kwargs: [],
    )

    result = ask(
        question="What is this document about?",
        documents=["test.pdf"],
        mode="semantic",
        owner_id=1,
        request_id="test-request-123",
    )

    assert result["answer"] == (
        "The AI service is temporarily unavailable. "
        "Please try again shortly."
    )

    assert result["sources"] == []