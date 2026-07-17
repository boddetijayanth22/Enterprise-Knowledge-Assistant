from fastapi import FastAPI

from app.api.exception_handlers import (
    register_exception_handlers,
)

from app.api.routes import router


app = FastAPI(
    title="Enterprise RAG Assistant",
    version="1.0.0",
)

register_exception_handlers(app)

app.include_router(router)