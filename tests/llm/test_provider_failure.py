from app.llm.exceptions import LLMProviderError


def test_llm_provider_error_is_safe():
    error = LLMProviderError("openrouter")

    assert str(error) == (
        "LLM provider 'openrouter' is temporarily unavailable."
    )


def test_llm_provider_error_does_not_expose_provider_details():
    error = LLMProviderError("openrouter")

    assert "api_key" not in str(error).lower()
    assert "traceback" not in str(error).lower()
    assert "rate_limit" not in str(error).lower()