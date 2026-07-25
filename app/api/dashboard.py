from fastapi import APIRouter

from app.schemas.dashboard import (
    DashboardStats,
    DocumentInfo,
)

from app.services.dashboard_service import (
    get_dashboard_data,
)

router = APIRouter()


@router.get(
    "/documents",
    response_model=list[DocumentInfo],
)
def documents():

    docs, _ = get_dashboard_data()

    return docs


@router.get(
    "/stats",
    response_model=DashboardStats,
)
def stats():

    _, stats = get_dashboard_data()

    return stats