from unittest.mock import patch

from langchain_core.messages import AIMessage

from app.services.query_service import ask


class FakeLLM:
    def invoke(self, prompt):
        return AIMessage(
            content=(
                "The requested API key is "
                "sk-abcdefghijklmnopqrstuvwxyz"
            )
        )


def test_llm_output_secret_is_redacted():
    with patch(
        "app.services.query_service.get_llm",
        return_value=FakeLLM(),
    ):
        result = ask(
            question="What is the API key?",
            documents=["Test Document.pdf"],
            mode="semantic",
            owner_id=4,
        )

    print("Answer:", result["answer"])

    assert "sk-abcdefghijklmnopqrstuvwxyz" not in result["answer"]
    assert "[REDACTED_API_KEY]" in result["answer"]

    print("PASS: LLM output secret was redacted")


test_llm_output_secret_is_redacted()

print("Output guard integration test passed.")