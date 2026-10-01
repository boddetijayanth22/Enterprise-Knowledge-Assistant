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

    def record_request(self):
        with self._lock:
            self.requests_total += 1

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
                "privacy": self.privacy_actions.copy(),
                "security": {
                    "blocked": self.security_blocks,
                },
            }


metrics = MetricsCollector()