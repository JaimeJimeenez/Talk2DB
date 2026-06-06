from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Any


class MessageRole(StrEnum):
    USER = "user"
    ASSISTANT = "assistant"


@dataclass(frozen=True, slots=True)
class Message:
    id: str
    role: MessageRole
    content: str
    timestamp: datetime
    sql: str | None = None
    error: str | None = None
    artifact: dict[str, Any] | None = None
    conversation_title: str | None = None
