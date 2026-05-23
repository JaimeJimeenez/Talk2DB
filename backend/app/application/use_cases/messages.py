from datetime import UTC, datetime
from uuid import uuid4

from app.domain.entities.message import Message, MessageRole
from app.domain.errors import ConversationNotFoundError
from app.domain.ports.assistant import AssistantGateway
from app.domain.ports.conversations import ConversationsRepository


class Messages:
    def __init__(self, repository: ConversationsRepository, assistant: AssistantGateway) -> None:
        self._repository = repository
        self._assistant = assistant

    async def save_message(self, conversation_id: str, content: str, user_id: str) -> Message:
        conversation = await self._repository.get_conversation(conversation_id, user_id)
        if conversation is None:
            raise ConversationNotFoundError(conversation_id)

        prompt = Message(
            id=str(uuid4()),
            role=MessageRole.USER,
            content=content,
            timestamp=datetime.now(UTC),
        )
        reply = await self._assistant.reply_to(prompt.content, conversation.schema_id)
        response_message = Message(
            id=str(uuid4()),
            role=MessageRole.ASSISTANT,
            content=reply.content,
            timestamp=datetime.now(UTC),
            sql=reply.sql,
            error=reply.error,
        )
        conversation.messages.extend([prompt, response_message])
        await self._repository.save(conversation)
        return response_message
