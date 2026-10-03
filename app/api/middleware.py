import time
import uuid

from fastapi import Request

from app.utils.logger import logger
from app.config.settings import settings
from app.observability.metrics import metrics
from fastapi.responses import JSONResponse
from app.security.rate_limiter import rate_limiter


async def request_logging_middleware(
    request: Request,
    call_next,
):
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id

    client_key = request.client.host if request.client else "unknown"

    if not rate_limiter.allow(client_key):
        logger.warning(
            "rate_limit_exceeded | "
            "request_id=%s | "
            "client=%s | "
            "path=%s",
            request_id,
            client_key,
            request.url.path,
        )

        return JSONResponse(
            status_code=429,
            content={
                "error": "Too many requests. Please try again later.",
                "request_id": request_id,
            },
            headers={
                "Retry-After": str(settings.rate_limit_window_seconds),
                "X-Request-ID": request_id,
            },
        )

    metrics.record_request()
    start_time = time.perf_counter()

    try:
        response = await call_next(request)

        return response

    finally:
        latency_ms = round(
            (time.perf_counter() - start_time) * 1000,
            2,
        )

        metrics.record_request_latency(latency_ms)

        logger.info(
            "request_completed | "
            "request_id=%s | "
            "method=%s | "
            "path=%s | "
            "status=%s | "
            "latency_ms=%s",
            request_id,
            request.method,
            request.url.path,
            getattr(
                locals().get("response"),
                "status_code",
                "exception",
            ),
            latency_ms,
        )

        if "response" in locals():
            response.headers["X-Request-ID"] = request_id