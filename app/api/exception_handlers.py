from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.utils.logger import logger


def register_exception_handlers(app: FastAPI):

    @app.exception_handler(Exception)
    async def global_exception_handler(
        request: Request,
        exc: Exception,
    ):
        request_id = getattr(
            request.state,
            "request_id",
            "unknown",
        )

        logger.exception(
            "unhandled_exception | "
            "request_id=%s | "
            "method=%s | "
            "path=%s",
            request_id,
            request.method,
            request.url.path,
        )

        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "request_id": request_id,
            },
        )