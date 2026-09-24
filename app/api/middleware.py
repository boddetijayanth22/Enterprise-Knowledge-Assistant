import time
import uuid

from fastapi import Request

from app.utils.logger import logger


async def request_logging_middleware(
    request: Request,
    call_next,
):
    request_id = str(uuid.uuid4())

    request.state.request_id = request_id

    start_time = time.perf_counter()

    response = await call_next(request)

    latency_ms = round(
        (time.perf_counter() - start_time) * 1000,
        2,
    )

    response.headers["X-Request-ID"] = request_id

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
        response.status_code,
        latency_ms,
    )

    return response