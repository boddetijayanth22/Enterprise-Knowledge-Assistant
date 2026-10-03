import time
from app.observability.metrics import metrics
from app.services.query_service import ask
from app.cache.query_cache import query_cache


def evaluate_system(
    questions: list[str],
    owner_id: int,
    documents: list[str] | None = None,
    mode: str = "hybrid_reranker",
) -> dict:
    query_cache.clear()

    cache_hits_before = metrics.cache_hits
    cache_misses_before = metrics.cache_misses

    total = len(questions)
    successful = 0
    provider_failures = 0

    for question in questions:
        start_time = time.perf_counter()

        result = ask(
            question=question,
            documents=documents,
            mode=mode,
            owner_id=owner_id,
            request_id="system-evaluation",
        )

        latency_ms = round(
            (time.perf_counter() - start_time) * 1000,
            2,
        )

        metrics.record_request_latency(latency_ms)

        answer = result.get("answer", "")

        if "temporarily unavailable" in answer.lower():
            provider_failures += 1
            continue

        successful += 1

    cache_hits = metrics.cache_hits - cache_hits_before
    cache_misses = metrics.cache_misses - cache_misses_before

    summary = metrics.summary()

    success_rate = (
        successful / total
        if total
        else 0.0
    )

    provider_failure_rate = (
        provider_failures / total
        if total
        else 0.0
    )

    cache_total = cache_hits + cache_misses

    cache_hit_rate = (
        cache_hits / cache_total
        if cache_total
        else 0.0
    )

    return {
        "queries": {
            "total": total,
            "successful": successful,
            "failed": total - successful,
            "success_rate": round(success_rate, 4),
        },
        "provider": {
            "failures": provider_failures,
            "failure_rate": round(provider_failure_rate, 4),
        },
        "latency": summary["latency"],
        "retrieval": summary["retrieval"],
        "llm": summary["llm"],
        "privacy": summary["privacy"],
        "security": summary["security"],
        "cache": {
            "hits": cache_hits,
            "misses": cache_misses,
            "hit_rate": round(cache_hit_rate, 4),
        },
    }


if __name__ == "__main__":
    questions = [
        "What does it mean that Python is a high-level language?",
        "What does it mean that Python is a high-level language?",
        "What are the three programming paradigms supported by Python?",
        "What is the difference between a compiler and an interpreter?",
        "What are the five kinds of literals in Python?",
        "How is None different from zero?",
        "What does it mean that strings are immutable?",
        "How does string slicing work in Python?",
        "What is the difference between append and extend?",
        "What is the difference between a tuple, set, and dictionary?",
    ]

    result = evaluate_system(
        questions=questions,
        owner_id=1,
        mode="hybrid_reranker",
    )

    print("\n=== SYSTEM EVALUATION ===")
    print(result)