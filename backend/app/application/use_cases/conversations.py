from datetime import UTC, datetime
from uuid import uuid4

from app.domain.entities.conversation import Conversation
from app.domain.errors import ConversationNotFoundError, QuerySchemaNotFoundError
from app.domain.ports.conversations import ConversationsRepository
from app.domain.ports.query_schemas import QuerySchemasRepository


class Conversations:
    def __init__(
        self,
        repository: ConversationsRepository,
        schemas: QuerySchemasRepository | None = None,
    ) -> None:
        self._repository = repository
        self._schemas = schemas

    async def create_conversation(self, schema_id: str, user_id: str) -> Conversation:
        if self._schemas is not None and await self._schemas.get(schema_id) is None:
            raise QuerySchemaNotFoundError(schema_id)
        conversation = Conversation(
            id=str(uuid4()),
            title="New Conversation",
            created_at=datetime.now(UTC),
            schema_id=schema_id,
            user_id=user_id,
        )
        return await self._repository.save(conversation)

    async def get_conversation(self, conversation_id: str, user_id: str) -> Conversation:
        conversation = await self._repository.get_conversation(conversation_id, user_id)
        if conversation is None:
            raise ConversationNotFoundError(conversation_id)
        return conversation

    async def list_conversations(self, user_id: str) -> list[Conversation]:
        return await self._repository.list_conversations(user_id)
