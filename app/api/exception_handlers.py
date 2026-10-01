from fastapi import Request
from fastapi.responses import JSONResponse

from app.utils.logger import logger
from app.observability.metrics import metrics


async def global_exception_handler(
    request: Request,
    exc: Exception,
):
    request_id = getattr(
        request.state,
        "request_id",
        None,
    )

    metrics.record_request_failure()

    logger.exception(
        "request_failed | "
        "request_id=%s | "
        "method=%s | "
        "path=%s | "
        "error_type=%s",
        request_id,
        request.method,
        request.url.path,
        type(exc).__name__,
    )

    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "request_id": request_id,
        },
    )


def register_exception_handlers(app):
    app.add_exception_handler(
        Exception,
        global_exception_handler,
    )