from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.entities.conversation import Conversation
from app.domain.entities.message import Message, MessageRole
from app.domain.ports.conversations import ConversationsRepository

from app.infrastructure.persistence.orm.conversation_records import ConversationRecord, MessageRecord

class SqlAlchemyConversationsRepository(ConversationsRepository):

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, conversation: Conversation) -> Conversation:
        record = await self._session.get(ConversationRecord, conversation.id)
        if record is None:
            record = ConversationRecord(
                id=conversation.id,
                title=conversation.title,
                created_at=conversation.created_at,
                schema_id=conversation.schema_id,
                user_id=conversation.user_id,
            )
            self._session.add(record)
        else:
            record.title = conversation.title
            record.created_at = conversation.created_at
            record.schema_id = conversation.schema_id
            record.user_id = conversation.user_id

        record.messages = [
            MessageRecord(
                id=message.id,
                conversation_id=conversation.id,
                role=message.role.value,
                content=message.content,
                timestamp=message.timestamp,
                sql=message.sql,
                error=message.error,
            )
            for message in conversation.messages
        ]
        await self._session.commit()
        await self._session.refresh(record)
        return self._to_domain(record)
    
    async def get_conversation(self, conversation_id: str, user_id: str) -> Conversation | None:
        statement = (
            select(ConversationRecord)
            .options(selectinload(ConversationRecord.messages))
            .where(ConversationRecord.id == conversation_id)
            .where(ConversationRecord.user_id == user_id)
        )
        record = await self._session.scalar(statement)
        return self._to_domain(record) if record is not None else None

    async def list_conversations(self, user_id: str) -> list[Conversation]:
        statement = (
            select(ConversationRecord)
            .options(selectinload(ConversationRecord.messages))
            .where(ConversationRecord.user_id == user_id)
            .order_by(ConversationRecord.created_at.desc(), ConversationRecord.id.desc())
        )
        records = await self._session.scalars(statement)
        return [self._to_domain(record) for record in records]

    @staticmethod
    def _to_domain(record: ConversationRecord) -> Conversation:
        return Conversation(
            id=record.id,
            title=record.title,
            created_at=record.created_at,
            schema_id=record.schema_id,
            user_id=record.user_id,
            messages=[
                Message(
                    id=message.id,
                    role=MessageRole(message.role),
                    content=message.content,
                    timestamp=message.timestamp,
                    sql=message.sql,
                    error=message.error,
                )
                for message in record.messages
            ],
        )
