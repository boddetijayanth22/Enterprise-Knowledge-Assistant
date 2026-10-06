import time
from collections import defaultdict, deque
from threading import Lock


class RateLimiter:
    def __init__(
        self,
        max_requests: int = 30,
        window_seconds: int = 60,
    ):
        self.max_requests = max_requests
        self.window_seconds = window_seconds

        self._requests = defaultdict(deque)
        self._lock = Lock()

    def allow(
        self,
        key: str,
        max_requests: int | None = None,
        window_seconds: int | None = None,
    ) -> bool:
        now = time.monotonic()

        limit = (
            max_requests
            if max_requests is not None
            else self.max_requests
        )

        window = (
            window_seconds
            if window_seconds is not None
            else self.window_seconds
        )

        window_start = now - window

        bucket_key = f"{key}:{limit}:{window}"

        with self._lock:
            timestamps = self._requests[bucket_key]

            while timestamps and timestamps[0] <= window_start:
                timestamps.popleft()

            if len(timestamps) >= limit:
                return False

            timestamps.append(now)
            return True

    def reset(self) -> None:
        with self._lock:
            self._requests.clear()


rate_limiter = RateLimiter()