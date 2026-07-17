from pydantic import BaseModel


class DocumentInfo(BaseModel):
    filename: str
    chunks: int


class DashboardStats(BaseModel):
    documents: int
    chunks: int
    embedding_model: str
    vector_db: str