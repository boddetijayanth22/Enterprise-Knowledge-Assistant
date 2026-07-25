from fastapi import FastAPI

from app.api.exception_handlers import (
    register_exception_handlers,
)

from app.api.routes import router
from app.api.query import router as query_router
from app.api.dashboard import router as dashboard_router
from app.api.documents import router as documents_router

app = FastAPI(
    title="Enterprise RAG Assistant",
    version="1.0.0",
)

register_exception_handlers(app)

app.include_router(router)
app.include_router(query_router)
app.include_router(dashboard_router)
app.include_router(documents_router)