from datetime import datetime

from pydantic import BaseModel

from app.infrastructure.api.schemas.message import MessageResponse

class ConversationResponse(BaseModel):
    id: str
    title: str
    created_at: datetime
    schema_id: str
    messages: list[MessageResponse]


class CreateConversationRequest(BaseModel):
    schema_id: str
