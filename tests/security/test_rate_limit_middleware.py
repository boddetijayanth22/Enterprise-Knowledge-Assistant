from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.middleware import request_logging_middleware
from app.security.rate_limiter import RateLimiter
import app.api.middleware as middleware_module


def test_rate_limit_middleware_returns_429(monkeypatch):
    app = FastAPI()
    app.middleware("http")(request_logging_middleware)

    limiter = RateLimiter(
        max_requests=1,
        window_seconds=60,
    )

    monkeypatch.setattr(
        middleware_module,
        "rate_limiter",
        limiter,
    )
    monkeypatch.setattr(
    	middleware_module.settings,
    	"rate_limit_requests",
    	1,
    )

    @app.post("/test")
    def test_endpoint():
        return {"status": "ok"}

    client = TestClient(app)

    first_response = client.post("/test")
    second_response = client.post("/test")

    assert first_response.status_code == 200

    assert second_response.status_code == 429
    assert second_response.json()["error"] == (
        "Too many requests. Please try again later."
    )

    assert "X-Request-ID" in second_response.headers
    assert second_response.headers["Retry-After"] == "60"