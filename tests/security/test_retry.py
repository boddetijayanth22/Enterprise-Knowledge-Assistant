import time

from openai import RateLimitError

from app.llm.retry import retry_with_backoff


def test_retry_succeeds_after_failures():
    attempts = {"count": 0}

    def fake_operation():
        attempts["count"] += 1

        if attempts["count"] < 3:
            raise TimeoutError("temporary failure")

        return "success"

    result = retry_with_backoff(
        fake_operation,
        max_attempts=3,
        base_delay=0.01,
    )

    assert result == "success"
    assert attempts["count"] == 3


def test_retry_after_header_is_respected(monkeypatch):
    attempts = {"count": 0}
    delays = []

    class FakeRequest:
        pass

    class FakeResponse:
        headers = {"Retry-After": "10"}
        request = FakeRequest()
        status_code = 429

    def fake_operation():
        attempts["count"] += 1

        if attempts["count"] == 1:
            error = RateLimitError(
                "rate limited",
                response=FakeResponse(),
                body=None,
            )
            raise error

        return "success"

    def fake_sleep(delay):
        delays.append(delay)

    monkeypatch.setattr(time, "sleep", fake_sleep)

    result = retry_with_backoff(
        fake_operation,
        max_attempts=3,
        base_delay=2.0,
    )

    assert result == "success"
    assert attempts["count"] == 2
    assert delays == [10.0]