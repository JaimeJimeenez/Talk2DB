from typing import Literal, List
from pydantic import BaseModel

class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str

class Completion(BaseModel):
    message: str
    history: List[ChatMessage]

class Response(BaseModel):
    response: str
    command: str | None = None
