from fastapi import APIRouter, HTTPException, Request, status

from app.domain.errors import ConversationNotFoundError, QuerySchemaNotFoundError
from app.domain.entities.user import User
from app.infrastructure.api.routers.dependencies import SessionDep
from app.infrastructure.api.schemas.conversation import ConversationResponse, CreateConversationRequest
from app.infrastructure.api.schemas.message import MessageResponse, SendMessageRequest
from app.infrastructure.api.security import requires_authentication

router = APIRouter(prefix="/api/v1/conversations", tags=["conversations"])

@router.post("", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
@requires_authentication
async def create_conversation(
    payload: CreateConversationRequest,
    request: Request,
    session: SessionDep,
) -> ConversationResponse:
    current_user: User = request.state.current_user
    conversations = request.app.container.conversations_use_case()
    try:
        conversation = await conversations.create_conversation(payload.schema_id, current_user.id)
    except QuerySchemaNotFoundError as error:
        raise HTTPException(status_code=404, detail="Schema not found") from error
    return ConversationResponse.model_validate(conversation, from_attributes=True)


@router.get("", response_model=list[ConversationResponse])
@requires_authentication
async def list_conversations(
    request: Request,
    session: SessionDep,
) -> list[ConversationResponse]:
    current_user: User = request.state.current_user
    conversations = request.app.container.conversations_use_case()
    items = await conversations.list_conversations(current_user.id)
    return [ConversationResponse.model_validate(item, from_attributes=True) for item in items]


@router.get("/{conversation_id}", response_model=ConversationResponse)
@requires_authentication
async def get_conversation(
    conversation_id: str,
    request: Request,
    session: SessionDep,
) -> ConversationResponse:
    current_user: User = request.state.current_user
    conversations = request.app.container.conversations_use_case()
    try:
        conversation = await conversations.get_conversation(conversation_id, current_user.id)
    except ConversationNotFoundError as error:
        raise HTTPException(status_code=404, detail="Conversation not found") from error
    return ConversationResponse.model_validate(conversation, from_attributes=True)


@router.post("/{conversation_id}/messages", response_model=MessageResponse)
@requires_authentication
async def send_message(
    conversation_id: str,
    payload: SendMessageRequest,
    request: Request,
    session: SessionDep,
) -> MessageResponse:
    current_user: User = request.state.current_user
    messages = request.app.container.messages_use_case()
    try:
        message = await messages.save_message(conversation_id, payload.content, current_user.id)
    except ConversationNotFoundError as error:
        raise HTTPException(status_code=404, detail="Conversation not found") from error
    return MessageResponse.model_validate(message, from_attributes=True)
