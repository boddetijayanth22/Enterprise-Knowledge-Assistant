from fastapi import APIRouter, Depends

from app.api.dependencies import get_chat_service
from app.auth.dependencies import get_current_user
from app.auth.models import User
from app.utils.logger import logger

from app.schemas.chat import ChatRequest, ChatResponse


router = APIRouter()


@router.post(
    "/chat",
    response_model=ChatResponse,
)
def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    chat_service=Depends(get_chat_service),
):

    logger.info(
        f"Chat request received for user_id={current_user.id}"
    )

    return chat_service(
        question=request.question,
        documents=request.documents,
        mode=request.mode,
        owner_id=current_user.id,
    )