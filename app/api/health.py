from fastapi import APIRouter
from sqlalchemy import text

from app.database.connection import engine
from app.vectorstore.client import get_qdrant_client
from app.config.settings import settings

router = APIRouter()


@router.get("/health")
def health():
    return {
        "status": "ok",
    }


@router.get("/ready")
def readiness():
    checks = {}

    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        checks["database"] = "ok"

    except Exception:
        checks["database"] = "unavailable"

    try:
        client = get_qdrant_client()

        client.get_collection(
            collection_name=settings.collection_name
        )

        checks["qdrant"] = "ok"

    except Exception:
        checks["qdrant"] = "unavailable"

    ready = all(
        status == "ok"
        for status in checks.values()
    )

    return {
        "status": "ready" if ready else "not_ready",
        "checks": checks,
    }