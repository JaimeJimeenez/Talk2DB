from abc import ABC, abstractmethod

from app.domain.entities.conversation import Conversation

class ConversationsRepository(ABC):
    @abstractmethod
    async def save(self, conversation: Conversation) -> Conversation:
        raise NotImplementedError

    @abstractmethod
    async def get_conversation(self, conversation_id: str, user_id: str) -> Conversation | None:
        raise NotImplementedError

    @abstractmethod
    async def list_conversations(self, user_id: str) -> list[Conversation]:
        raise NotImplementedError
