from pathlib import Path
import shutil

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    HTTPException,
    UploadFile,
)

from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import get_ingestion_service
from app.auth.dependencies import get_current_user
from app.auth.models import User
from app.database.connection import get_db
from app.database.document_models import Document
from app.schemas.upload import UploadResponse
from app.services.document_service import delete_document
from app.utils.file_hash import calculate_file_hash

router = APIRouter()


@router.post(
    "/upload",
    response_model=UploadResponse,
    status_code=201,
)
async def upload_pdf(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    ingestion_service=Depends(get_ingestion_service),
):

    if (
        not file.filename
        or (
            file.content_type != "application/pdf"
            and not file.filename.lower().endswith(".pdf")
        )
    ):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed.",
        )

    safe_filename = Path(file.filename).name

    user_upload_dir = Path("data/raw") / str(current_user.id)
    user_upload_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    file_path = user_upload_dir / safe_filename

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        file_hash = calculate_file_hash(str(file_path))

        existing_document = db.scalar(
            select(Document).where(
                Document.owner_id == current_user.id,
                Document.file_hash == file_hash,
            )
        )

        if existing_document:
            if existing_document.status == "failed":
                existing_document.status = "processing"
                db.commit()

                background_tasks.add_task(
                    ingestion_service,
                    str(file_path),
                    current_user.id,
                    existing_document.id,
                    True,
                )

                return UploadResponse(
                    filename=safe_filename,
                    status="processing",
                )

            file_path.unlink()

            raise HTTPException(
                status_code=409,
                detail="You have already uploaded this document.",
            )

        document = Document(
            filename=safe_filename,
            file_hash=file_hash,
            owner_id=current_user.id,
        )

        db.add(document)
        db.commit()
        db.refresh(document)

        background_tasks.add_task(
            ingestion_service,
            str(file_path),
            current_user.id,
            document.id,
        )

    except HTTPException:
        raise

    except Exception:
        if file_path.exists():
            file_path.unlink()

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Failed to ingest PDF.",
        )

    return UploadResponse(
        filename=safe_filename,
        status="processing",
    )

@router.delete("/documents/{filename}")
def remove_document(
    filename: str,
    current_user: User = Depends(get_current_user),
):
    try:
        return delete_document(
            filename=filename,
            owner_id=current_user.id,
        )

    except FileNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e),
        )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Failed to delete document.",
        )


@router.get("/documents/{filename}/download")
def download_document(
    filename: str,
    current_user: User = Depends(get_current_user),
):
    file_path = (
        Path("data/raw")
        / str(current_user.id)
        / filename
    )

    if not file_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Document not found.",
        )

    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="application/pdf",
    )