from app.domain.entities.conversation import Conversation
from app.domain.ports.conversations import ConversationsRepository


class InMemoryConversationRepository(ConversationsRepository):
    def __init__(self) -> None:
        self._conversations: dict[str, Conversation] = {}

    async def save(self, conversation: Conversation) -> Conversation:
        self._conversations[conversation.id] = conversation
        return conversation

    async def get_conversation(self, conversation_id: str, user_id: str) -> Conversation | None:
        conversation = self._conversations.get(conversation_id)
        if conversation is None or conversation.user_id != user_id:
            return None
        return conversation

    async def list_conversations(self, user_id: str) -> list[Conversation]:
        return sorted(
            [
                conversation
                for conversation in self._conversations.values()
                if conversation.user_id == user_id
            ],
            key=lambda conversation: (conversation.created_at, conversation.id),
            reverse=True,
        )
