import time
from collections.abc import Callable
from typing import TypeVar

import httpx
from openai import APIConnectionError
from openai import APITimeoutError
from openai import RateLimitError
from openai import InternalServerError


T = TypeVar("T")


RETRYABLE_EXCEPTIONS = (
    RateLimitError,
    APITimeoutError,
    APIConnectionError,
    InternalServerError,
    httpx.TimeoutException,
    TimeoutError,
)


def get_retry_after(exc: Exception) -> float | None:
    response = getattr(exc, "response", None)

    if response is None:
        return None

    headers = getattr(response, "headers", {})

    retry_after = headers.get("Retry-After")

    if retry_after is None:
        return None

    try:
        return float(retry_after)
    except (TypeError, ValueError):
        return None


def retry_with_backoff(
    operation: Callable[[], T],
    max_attempts: int = 3,
    base_delay: float = 2.0,
) -> T:

    for attempt in range(1, max_attempts + 1):

        try:
            return operation()

        except RETRYABLE_EXCEPTIONS as exc:

            if attempt == max_attempts:
                raise

            retry_after = get_retry_after(exc)

            if retry_after is not None:
                delay = retry_after
            else:
                delay = base_delay * (2 ** (attempt - 1))

            time.sleep(delay)

    raise RuntimeError("Retry operation failed")