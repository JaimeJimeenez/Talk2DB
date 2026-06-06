from datetime import datetime, UTC
from uuid import uuid4
from typing import Any

from app.domain.ports.conversations import ConversationsPort
from app.domain.ports.schemas import SchemasPort
from app.domain.errors import ConversationNotFoundError, QuerySchemaNotFoundError
from app.domain.entities.conversation import Conversation


class ConversationCompletion:
    def __init__(self, title: str, conversation_id: str, answer: str) -> None:
        self.title = title
        self.conversation_id = conversation_id
        self.answer = answer

class ConversationsUseCase:

    DEFAULT_USER_ID = "anonymous"

    def __init__(
        self,
        conversations_port: ConversationsPort,
        schemas_port: SchemasPort | None = None,
        rag_use_case: Any | None = None,
    ) -> None:
        self._conversations_port = conversations_port
        self._schemas_port = schemas_port
        self._rag_use_case = rag_use_case

    async def create_conversation(self, schema_id: str, user_id: str):
        schema_name: str = ''
        if self._schemas_port is not None:
            schema = await self._get_schema(schema_id)
            if schema is None:
                raise QuerySchemaNotFoundError(schema_id)
            schema_name = schema.name
        conversation = Conversation(
            id=str(uuid4()),
            title='New Conversation',
            created_at=datetime.now(UTC),
            schema_id=schema_id,
            user_id=user_id,
            schema_name=schema_name,
        )

        return await self._conversations_port.save(conversation)

    async def get_conversation(self, conversation_id: str, user_id: str) -> Conversation:
        conversation = await self._conversations_port.get_conversation(conversation_id, user_id)
        if conversation is None:
            raise ConversationNotFoundError(conversation_id)
        return conversation

    async def list_conversations(self, user_id: str) -> list[Conversation]:
        return await self._conversations_port.list_conversations(user_id)

    async def save_conversation(self, conversation: Conversation) -> Conversation:
        return await self._conversations_port.save(conversation)

    async def new_conversation(self, prompt: str, schema_id: str, user_id: str) -> Conversation:
        schema_name = ""
        if self._schemas_port is not None:
            schema = await self._get_schema(schema_id)
            if schema is None:
                raise QuerySchemaNotFoundError(schema_id)
            schema_name = schema.name
        title = (
            await self._rag_use_case.generate_conversation_title(prompt)
            if self._rag_use_case is not None
            else self._fallback_title(prompt)
        )
        return Conversation(
            id=str(uuid4()),
            title=title,
            created_at=datetime.now(UTC),
            schema_id=schema_id,
            user_id=user_id,
            schema_name=schema_name,
        )

    async def _get_schema(self, schema_id: str):
        if hasattr(self._schemas_port, "get_schema"):
            return await self._schemas_port.get_schema(schema_id)
        return await self._schemas_port.get(schema_id)

    @staticmethod
    def _fallback_title(prompt: str) -> str:
        normalized = " ".join(prompt.strip().split()).strip(" ¿?¡!.,;:")
        if not normalized:
            return "New Conversation"
        return normalized[:53].rstrip(" .,;:") + ("..." if len(normalized) > 56 else "")

    @staticmethod
    def _artifact_from_rag_result(prompt: str, rag_result) -> dict | None:
        if rag_result.error or not rag_result.sql:
            return None
        return {
            "id": str(uuid4()),
            "title": ConversationsUseCase._fallback_title(prompt),
            "type": "query_result",
            "generatedFrom": prompt,
            "summary": rag_result.answer,
            "sql": rag_result.sql,
            "columns": [{"name": column, "type": "unknown"} for column in rag_result.columns],
            "rows": rag_result.rows,
            "rowCount": rag_result.row_count,
            "truncated": rag_result.row_count >= 100,
            "error": None,
        }
