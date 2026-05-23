from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


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
