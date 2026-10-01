from app.services.ingestion_service import ingest_pdf
from app.utils.logger import logger


def run_ingestion(
    pdf_path: str,
    owner_id: int,
):
    try:
        logger.info(
            "background_ingestion_started | "
            "owner_id=%s | "
            "file=%s",
            owner_id,
            pdf_path,
        )

        ingest_pdf(
            pdf_path=pdf_path,
            owner_id=owner_id,
        )

        logger.info(
            "background_ingestion_completed | "
            "owner_id=%s | "
            "file=%s",
            owner_id,
            pdf_path,
        )

    except Exception:
        logger.exception(
            "background_ingestion_failed | "
            "owner_id=%s | "
            "file=%s",
            owner_id,
            pdf_path,
        )