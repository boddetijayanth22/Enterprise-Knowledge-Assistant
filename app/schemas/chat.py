from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    question: str
    documents: list[str] | None = Field(default=None)
    mode: str
    

class Source(BaseModel):
    file: str
    page: int


class ChatResponse(BaseModel):
    answer: str
    sources: list[Source]