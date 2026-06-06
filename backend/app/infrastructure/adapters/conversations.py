import logging

from contextlib import AbstractContextManager
from typing import Callable

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.infrastructure.adapters.database.models.conversations import ConversationsRecord
from app.infrastructure.adapters.database.models.messages import MessageRecord

from app.domain.entities.conversation import Conversation
from app.domain.entities.message import Message, MessageRole

logger = logging.getLogger(__name__)

class ConversationsAdapter:

    def __init__(
        self,
        session_factory: Callable[..., AbstractContextManager[Session]],
    ) -> None:
        self._session_factory = session_factory

    async def save(self, conversation: Conversation) -> Conversation:
        with self._session_factory() as session:
            logger.info(f"Saving conversation {conversation.id} to the database")
            record = session.get(ConversationsRecord, conversation.id)
            if record is None:
                record = ConversationsRecord(
                    id=conversation.id,
                    title=conversation.title,
                    created_at=conversation.created_at,
                    schema_id=conversation.schema_id,
                    user_id=conversation.user_id,
                )
                session.add(record)
            else:
                record.title = conversation.title
                record.schema_id = conversation.schema_id
                record.user_id = conversation.user_id

            existing_message_ids = {
                message_id
                for (message_id,) in session.execute(
                    select(MessageRecord.id).where(MessageRecord.conversation_id == conversation.id)
                ).all()
            }
            for message in conversation.messages:
                if message.id in existing_message_ids:
                    continue
                session.add(
                    MessageRecord(
                        id=message.id,
                        conversation_id=conversation.id,
                        role=message.role.value,
                        content=message.content,
                        timestamp=message.timestamp,
                        sql=message.sql,
                        error=message.error,
                        artifact=message.artifact,
                    )
                )
            session.flush()
            return self._to_entity(session, record)

    async def get_conversation(self, conversation_id: str, user_id: str) -> Conversation | None:
        with self._session_factory() as session:
            record = session.execute(
                select(ConversationsRecord).where(
                    ConversationsRecord.id == conversation_id,
                    ConversationsRecord.user_id == user_id,
                )
            ).scalar_one_or_none()
            if record is None:
                return None
            return self._to_entity(session, record)

    async def list_conversations(self, user_id: str) -> list[Conversation]:
        with self._session_factory() as session:
            records = session.execute(
                select(ConversationsRecord)
                .where(ConversationsRecord.user_id == user_id)
                .order_by(ConversationsRecord.created_at.desc())
            ).scalars().all()
            return [self._to_entity(session, record) for record in records]

    def _to_entity(self, session: Session, record: ConversationsRecord) -> Conversation:
        messages = session.execute(
            select(MessageRecord)
            .where(MessageRecord.conversation_id == record.id)
            .order_by(MessageRecord.timestamp.asc(), MessageRecord.id.asc())
        ).scalars().all()
        return Conversation(
            id=record.id,
            title=record.title,
            created_at=record.created_at,
            schema_id=record.schema_id,
            user_id=record.user_id,
            schema_name="",
            messages=[
                Message(
                    id=message.id,
                    role=MessageRole(message.role),
                    content=message.content,
                    timestamp=message.timestamp,
                    sql=message.sql,
                    error=message.error,
                    artifact=message.artifact,
                )
                for message in messages
            ],
        )
