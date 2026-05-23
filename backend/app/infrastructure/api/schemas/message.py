from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

class MessageResponse(BaseModel):
    id: str
    role: Literal["user", "assistant"]
    content: str
    timestamp: datetime
    sql: str | None = None
    error: str | None = None

class SendMessageRequest(BaseModel):
    content: str = Field(min_length=1)
