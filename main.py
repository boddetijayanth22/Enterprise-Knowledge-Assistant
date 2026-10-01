from fastapi import FastAPI

from app.api.exception_handlers import (
    register_exception_handlers,
)
from app.api.middleware import request_logging_middleware
from app.api.routes import router
from app.api.query import router as query_router
from app.api.dashboard import router as dashboard_router
from app.api.documents import router as documents_router
from app.api.health import router as health_router
from app.utils.logger import configure_logging
from app.api.auth import router as auth_router
from app.api.observability import router as observability_router

configure_logging()

app = FastAPI(
    title="Enterprise RAG Assistant",
    version="1.0.0",
)

app.middleware("http")(request_logging_middleware)

register_exception_handlers(app)

app.include_router(router)
app.include_router(query_router)
app.include_router(dashboard_router)
app.include_router(documents_router)
app.include_router(auth_router)
app.include_router(observability_router)
app.include_router(health_router)