from fastapi import APIRouter, Depends

from app.api.dependencies import get_chat_service
from app.utils.logger import logger
from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
)

router = APIRouter()


@router.post(
    "/chat",
    response_model=ChatResponse,
)
def chat(
    request: ChatRequest,
    chat_service=Depends(get_chat_service),
):

    logger.info("Chat request received")

    return chat_service(
        request.question,
        request.documents,
        request.mode,
    )