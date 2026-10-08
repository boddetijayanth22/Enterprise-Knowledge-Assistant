from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.document_models import Document
from app.database.connection import get_db
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

    indexed_documents = [
        document
        for document in documents
        if document["status"] == "completed"
    ]

    total_documents = len(indexed_documents)

    total_chunks = sum(
        document["chunks"]
        for document in indexed_documents
    )

    return {
        "total_documents": total_documents,
        "total_chunks": total_chunks,
        "embedding_model": settings.embedding_model,
    }

@router.get("/documents/status")
def get_document_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    documents = db.scalars(
        select(Document)
        .where(Document.owner_id == current_user.id)
        .order_by(Document.created_at.desc())
    ).all()

    return {
        "documents": [
            {
                "id": document.id,
                "filename": document.filename,
                "status": document.status,
            }
            for document in documents
        ]
    }