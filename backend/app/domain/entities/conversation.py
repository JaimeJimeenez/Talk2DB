from dataclasses import dataclass, field
from datetime import datetime

from app.domain.entities.message import Message

@dataclass(slots=True)
class Conversation:
    id: str
    title: str
    created_at: datetime
    schema_id: str
    user_id: str
    messages: list[Message] = field(default_factory=list)
