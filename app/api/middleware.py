import time
import uuid

import jwt

from fastapi import Request
from fastapi.responses import JSONResponse

from app.config.settings import settings
from app.observability.metrics import metrics
from app.security.rate_limiter import rate_limiter
from app.utils.logger import logger


SAFE_METHODS = {
    "GET",
    "HEAD",
    "OPTIONS",
}


RATE_LIMIT_POLICIES = {
    "POST:/chat": (20, 60),
    "POST:/upload": (10, 60),
    "DELETE:/documents": (20, 60),
}


def get_rate_limit_policy(
    method: str,
    path: str,
) -> tuple[int, int] | None:

    if method in SAFE_METHODS:
        return None

    if method == "DELETE" and path.startswith("/documents/"):
        return RATE_LIMIT_POLICIES["DELETE:/documents"]

    policy = RATE_LIMIT_POLICIES.get(
        f"{method}:{path}"
    )

    if policy:
        return policy

    return (
        settings.rate_limit_requests,
        settings.rate_limit_window_seconds,
    )


def get_rate_limit_identity(
    request: Request,
) -> str:

    authorization = request.headers.get(
        "Authorization"
    )

    if authorization and authorization.startswith(
        "Bearer "
    ):
        token = authorization[7:].strip()

        try:
            payload = jwt.decode(
                token,
                settings.jwt_secret_key,
                algorithms=[settings.jwt_algorithm],
            )

            user_id = payload.get("sub")

            if user_id is not None:
                return f"user:{user_id}"

        except jwt.PyJWTError:
            pass

    client_host = (
        request.client.host
        if request.client
        else "unknown"
    )

    return f"ip:{client_host}"


async def request_logging_middleware(
    request: Request,
    call_next,
):
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id

    policy = get_rate_limit_policy(
        request.method,
        request.url.path,
    )

    if policy is not None:

        max_requests, window_seconds = policy

        rate_limit_identity = get_rate_limit_identity(
            request
        )

        allowed = rate_limiter.allow(
            key=rate_limit_identity,
            max_requests=max_requests,
            window_seconds=window_seconds,
        )

        if not allowed:

            logger.warning(
                "rate_limit_exceeded | "
                "request_id=%s | "
                "identity=%s | "
                "method=%s | "
                "path=%s",
                request_id,
                rate_limit_identity,
                request.method,
                request.url.path,
            )

            return JSONResponse(
                status_code=429,
                content={
                    "error": (
                        "Too many requests. "
                        "Please try again later."
                    ),
                    "request_id": request_id,
                },
                headers={
                    "Retry-After": str(
                        window_seconds
                    ),
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
            (
                time.perf_counter()
                - start_time
            ) * 1000,
            2,
        )

        metrics.record_request_latency(
            latency_ms
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
            response.headers[
                "X-Request-ID"
            ] = request_id