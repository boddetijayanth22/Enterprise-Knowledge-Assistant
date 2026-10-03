from collections import deque
from threading import Lock


class MetricsCollector:

    def __init__(self):
        self._lock = Lock()

        self.requests_total = 0
        self.requests_failed = 0

        self.retrieval_total = 0
        self.retrieval_latency_total_ms = 0.0

        self.llm_total = 0
        self.llm_latency_total_ms = 0.0

        self.privacy_actions = {
            "ALLOW": 0,
            "REDACT": 0,
            "BLOCK": 0,
        }

        self.security_blocks = 0
        self.cache_hits = 0
        self.cache_misses = 0
        self.request_latencies_ms = deque(maxlen=1000)
    

    def record_request(self):
        with self._lock:
            self.requests_total += 1

    def record_request_latency(self, latency_ms: float):
        with self._lock:
            self.request_latencies_ms.append(latency_ms)

    def record_request_failure(self):
        with self._lock:
            self.requests_failed += 1

    def record_retrieval(self, latency_ms: float):
        with self._lock:
            self.retrieval_total += 1
            self.retrieval_latency_total_ms += latency_ms

    def record_llm(self, latency_ms: float):
        with self._lock:
            self.llm_total += 1
            self.llm_latency_total_ms += latency_ms

    def record_privacy_action(self, action: str):
        with self._lock:
            if action in self.privacy_actions:
                self.privacy_actions[action] += 1

    def record_security_block(self):
        with self._lock:
            self.security_blocks += 1

    def _percentile(self, values: list[float], percentile: float) -> float:
        if not values:
            return 0.0

        sorted_values = sorted(values)

        rank = (percentile / 100) * (len(sorted_values) - 1)
        lower = int(rank)
        upper = min(lower + 1, len(sorted_values) - 1)

        if lower == upper:
            return sorted_values[lower]

        weight = rank - lower

        return (
            sorted_values[lower]
            + weight * (sorted_values[upper] - sorted_values[lower])
        )

    def record_cache_hit(self):
        with self._lock:
            self.cache_hits += 1

    def record_cache_miss(self):
        with self._lock:
            self.cache_misses += 1

    def summary(self) -> dict:

        with self._lock:

            retrieval_avg = (
                self.retrieval_latency_total_ms
                / self.retrieval_total
                if self.retrieval_total
                else 0.0
            )

            llm_avg = (
                self.llm_latency_total_ms
                / self.llm_total
                if self.llm_total
                else 0.0
            )

            request_latencies = list(self.request_latencies_ms)

            request_p50 = self._percentile(
                request_latencies,
                50,
            )

            request_p95 = self._percentile(
                request_latencies,
                95,
            )

            return {
                "requests": {
                    "total": self.requests_total,
                    "failed": self.requests_failed,
                },
                "retrieval": {
                    "total": self.retrieval_total,
                    "avg_latency_ms": round(
                        retrieval_avg,
                        2,
                    ),
                },
                "llm": {
                    "total": self.llm_total,
                    "avg_latency_ms": round(
                        llm_avg,
                        2,
                    ),
                },
                "latency": {
                    "p50_ms": round(request_p50, 2),
                    "p95_ms": round(request_p95, 2),
                },
                "cache": {
                    "hits": self.cache_hits,
                    "misses": self.cache_misses,
                },
                "privacy": self.privacy_actions.copy(),
                "security": {
                    "blocked": self.security_blocks,
                },
            }


metrics = MetricsCollector()