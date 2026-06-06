from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, status

from app.application.use_cases.conversations import ConversationsUseCase
from app.core.container import Container
from app.domain.errors import ConversationNotFoundError, QuerySchemaNotFoundError
from app.infrastructure.api.schemas.conversations import (
    ConversationResponse,
    ConversationSummaryResponse,
    CreateConversationRequest,
)
from app.infrastructure.api.security import get_current_user_id

router = APIRouter(prefix="/api/v1/conversations", tags=["conversations"])


@router.post("", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
@inject
async def create_conversation(
    payload: CreateConversationRequest,
    user_id: str = Depends(get_current_user_id),
    conversations_use_case: ConversationsUseCase = Depends(Provide[Container.conversations_use_case]),
) -> ConversationResponse:
    try:
        conversation = await conversations_use_case.create_conversation(payload.schema_id, user_id)
    except QuerySchemaNotFoundError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Schema not found") from error
    return ConversationResponse.model_validate(conversation, from_attributes=True)


@router.get("", response_model=list[ConversationSummaryResponse], status_code=status.HTTP_200_OK)
@inject
async def list_conversations(
    user_id: str = Depends(get_current_user_id),
    conversations_use_case: ConversationsUseCase = Depends(Provide[Container.conversations_use_case]),
) -> list[ConversationSummaryResponse]:
    conversations = await conversations_use_case.list_conversations(user_id)
    return [
        ConversationSummaryResponse.model_validate(conversation, from_attributes=True)
        for conversation in conversations
    ]


@router.get("/{conversation_id}", response_model=ConversationResponse, status_code=status.HTTP_200_OK)
@inject
async def get_conversation(
    conversation_id: str,
    user_id: str = Depends(get_current_user_id),
    conversations_use_case: ConversationsUseCase = Depends(Provide[Container.conversations_use_case]),
) -> ConversationResponse:
    try:
        conversation = await conversations_use_case.get_conversation(conversation_id, user_id)
    except ConversationNotFoundError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found") from error
    return ConversationResponse.model_validate(conversation, from_attributes=True)
