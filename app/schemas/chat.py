from pydantic import BaseModel


class ChatRequest(BaseModel):
    question: str
    documents: list[str]
    mode: str = "semantic"
    

class Source(BaseModel):
    file: str
    page: int


class ChatResponse(BaseModel):
    answer: str
    sources: list[Source]