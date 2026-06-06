from datetime import datetime
from typing import Any
from pydantic import BaseModel, Field


class CreateConversationRequest(BaseModel):
    schema_id: str


class MessageResponse(BaseModel):
    id: str
    role: str
    content: str
    timestamp: datetime
    sql: str | None = None
    error: str | None = None
    artifact: dict[str, Any] | None = None
    conversation_title: str | None = None


class ConversationResponse(BaseModel):
    id: str
    title: str
    created_at: datetime
    schema_id: str
    schema_name: str = ""
    messages: list[MessageResponse]


class ConversationSummaryResponse(BaseModel):
    id: str
    title: str


class PromptRequest(BaseModel):
    conversation_id: str | None = None
    prompt: str
    schema_id: str

class PromptResponse(BaseModel):
    title: str
    conversation_id: str
    answer: str
    id: str = Field(alias="message_id")
    role: str = "assistant"
    content: str
    timestamp: datetime
    sql: str | None = None
    error: str | None = None
    artifact: dict[str, Any] | None = None
    conversation_title: str
