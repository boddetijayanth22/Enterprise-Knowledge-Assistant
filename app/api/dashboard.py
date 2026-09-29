from fastapi import APIRouter, Depends

from app.auth.dependencies import get_current_user
from app.auth.models import User
from app.config.settings import settings
from app.services.document_service import list_documents

router = APIRouter()


@router.get("/documents")
def get_documents(
    current_user: User = Depends(get_current_user),
):
    documents = list_documents(
        owner_id=current_user.id,
    )

    return {
        "documents": documents,
    }


@router.get("/stats")
def get_stats(
    current_user: User = Depends(get_current_user),
):
    documents = list_documents(
        owner_id=current_user.id,
    )

    total_documents = len(documents)

    total_chunks = sum(
        document["chunks"]
        for document in documents
    )

    return {
        "total_documents": total_documents,
        "total_chunks": total_chunks,
        "embedding_model": settings.embedding_model,
    }