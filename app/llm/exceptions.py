class LLMProviderError(Exception):
    """Raised when an LLM provider request fails after retries."""

    def __init__(self, provider: str):
        self.provider = provider
        super().__init__(
            f"LLM provider '{provider}' is temporarily unavailable."
        )