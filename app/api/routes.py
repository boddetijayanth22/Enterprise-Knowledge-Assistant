from pathlib import Path
import shutil

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
)

from app.api.dependencies import (
    get_chat_service,
    get_ingestion_service,
)

from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
)

from app.schemas.upload import UploadResponse
from app.services.dashboard_service import get_dashboard_data
from app.schemas.dashboard import (
    DocumentInfo,
    DashboardStats,
)

from app.services.document_service import delete_document

router = APIRouter()


@router.post(
    "/chat",
    response_model=ChatResponse,
)
def chat(
    request: ChatRequest,
    chat_service=Depends(get_chat_service),
):
    print("Received by FastAPI:", request.documents)
    
    return chat_service(
        request.question,
        request.documents,
    )


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

    # Create upload directory
    upload_dir = Path("data/raw")
    upload_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    # Prevent path traversal
    safe_filename = Path(file.filename).name
    file_path = upload_dir / safe_filename

    # Save file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Index the PDF
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


@router.get("/health")
def health():
    return {
        "status": "healthy",
    }

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

@router.delete("/documents/{filename}")
def remove_document(filename: str):

    return delete_document(filename)