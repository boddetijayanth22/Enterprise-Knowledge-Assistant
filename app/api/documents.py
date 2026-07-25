from pathlib import Path
import shutil

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
)
from fastapi.responses import FileResponse

from app.api.dependencies import (
    get_ingestion_service,
)

from app.schemas.upload import UploadResponse
from app.services.document_service import delete_document

router = APIRouter()


@router.post(
    "/upload",
    response_model=UploadResponse,
    status_code=201,
)
async def upload_pdf(
    file: UploadFile = File(...),
    ingestion_service=Depends(get_ingestion_service),
):

    # Validate uploaded file
    if (
        file.content_type != "application/pdf"
        and not file.filename.lower().endswith(".pdf")
    ):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed.",
        )

    upload_dir = Path("data/raw")
    upload_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    safe_filename = Path(file.filename).name
    file_path = upload_dir / safe_filename

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        ingestion_service(str(file_path))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to ingest PDF: {e}",
        )

    return UploadResponse(
        filename=safe_filename,
        status="uploaded",
    )


@router.delete("/documents/{filename}")
def remove_document(filename: str):

    try:
        return delete_document(filename)

    except FileNotFoundError as e:

        raise HTTPException(
            status_code=404,
            detail=str(e),
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )

@router.get("/documents/{filename}/download")
def download_document(filename: str):

    file_path = Path("data/raw") / filename

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