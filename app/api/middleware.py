import time
import uuid

from fastapi import Request

from app.utils.logger import logger
from app.observability.metrics import metrics


async def request_logging_middleware(
    request: Request,
    call_next,
):
    request_id = str(uuid.uuid4())

    request.state.request_id = request_id

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