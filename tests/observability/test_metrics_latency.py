from app.observability.metrics import MetricsCollector


def test_latency_percentiles():
    collector = MetricsCollector()

    for latency in [10, 20, 30, 40, 50]:
        collector.record_request_latency(latency)

    summary = collector.summary()

    assert summary["latency"]["p50_ms"] == 30.0
    assert summary["latency"]["p95_ms"] == 48.0


def test_latency_percentiles_empty():
    collector = MetricsCollector()

    summary = collector.summary()

    assert summary["latency"]["p50_ms"] == 0.0
    assert summary["latency"]["p95_ms"] == 0.0