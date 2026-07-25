from app.services.query_service import ask
from app.services.ingestion_service import ingest_pdf


def get_chat_service():
    return ask


def get_ingestion_service():
    return ingest_pdf