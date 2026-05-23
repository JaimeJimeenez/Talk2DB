from abc import ABC, abstractmethod

from dataclasses import dataclass


@dataclass(slots=True)
class AssistantReply:
    content: str
    sql: str | None = None
    error: str | None = None


class AssistantGateway(ABC):
    @abstractmethod
    async def reply_to(self, content: str, schema_id: str) -> AssistantReply:
        raise NotImplementedError
