from fastapi import APIRouter

from app.observability.metrics import metrics


router = APIRouter()


@router.get("/metrics")
def get_metrics():
    return metrics.summary()