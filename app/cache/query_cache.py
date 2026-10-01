import hashlib
import time
from threading import Lock
from app.config.settings import settings


class QueryCache:
    def __init__(self, ttl_seconds: int = 300):
        self.ttl_seconds = ttl_seconds
        self._cache = {}
        self._lock = Lock()

    def _make_key(
        self,
        question: str,
        documents: list[str] | None,
        mode: str,
        owner_id: int,
    ) -> str:
        normalized_documents = tuple(sorted(documents or []))

        raw_key = repr(
            (
                owner_id,
                question.strip(),
                normalized_documents,
                mode,
            )
        )

        return hashlib.sha256(
            raw_key.encode("utf-8")
        ).hexdigest()

    def get(
        self,
        question: str,
        documents: list[str] | None,
        mode: str,
        owner_id: int,
    ):
        key = self._make_key(
            question,
            documents,
            mode,
            owner_id,
        )

        with self._lock:
            entry = self._cache.get(key)

            if entry is None:
                return None

            value, created_at = entry

            if time.monotonic() - created_at > self.ttl_seconds:
                del self._cache[key]
                return None

            return value

    def set(
        self,
        question: str,
        documents: list[str] | None,
        mode: str,
        owner_id: int,
        value,
    ):
        key = self._make_key(
            question,
            documents,
            mode,
            owner_id,
        )

        with self._lock:
            self._cache[key] = (
                value,
                time.monotonic(),
            )

    def clear(self):
        with self._lock:
            self._cache.clear()


query_cache = QueryCache(
    ttl_seconds=settings.query_cache_ttl_seconds,
)