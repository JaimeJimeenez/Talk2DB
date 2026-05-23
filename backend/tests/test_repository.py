from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.domain.entities.conversation import Conversation
from app.domain.entities.message import Message, MessageRole
from app.infrastructure.persistence.repositories.conversations import (
    SqlAlchemyConversationsRepository,
)
from app.domain.entities.query_schema import QuerySchema
from app.infrastructure.persistence.orm.user_records import UserRecord
from app.infrastructure.persistence.repositories.query_schemas import SqlAlchemyQuerySchemasRepository

SCHEMA_ID = "00000000-0000-0000-0000-000000000001"
USER_ID = "00000000-0000-0000-0000-000000000101"
OTHER_USER_ID = "00000000-0000-0000-0000-000000000102"
CONVERSATION_1_ID = "00000000-0000-0000-0000-000000000011"
CONVERSATION_2_ID = "00000000-0000-0000-0000-000000000012"
MESSAGE_1_ID = "00000000-0000-0000-0000-000000000021"
MESSAGE_2_ID = "00000000-0000-0000-0000-000000000022"


@pytest.mark.anyio
async def test_sqlalchemy_repository_persists_and_lists_conversations(
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    async with session_factory() as session:
        repository = SqlAlchemyConversationsRepository(session)
        now = datetime.now(UTC)
        session.add_all(
            [
                UserRecord(id=USER_ID, username="demo_user", email="demo@example.com", password="password", created_at=now, role="user"),
                UserRecord(id=OTHER_USER_ID, username="other_user", email="other@example.com", password="password", created_at=now, role="user"),
            ]
        )
        await session.commit()
        await SqlAlchemyQuerySchemasRepository(session).save(
            QuerySchema(SCHEMA_ID, "sales", "", "", "context", now, now)
        )
        older = Conversation(id=CONVERSATION_1_ID, title="Older", created_at=now - timedelta(days=1), schema_id=SCHEMA_ID, user_id=USER_ID)
        newer = Conversation(id=CONVERSATION_2_ID, title="Newer", created_at=now, schema_id=SCHEMA_ID, user_id=USER_ID)
        other = Conversation(id="00000000-0000-0000-0000-000000000013", title="Other", created_at=now, schema_id=SCHEMA_ID, user_id=OTHER_USER_ID)

        await repository.save(older)
        await repository.save(newer)
        await repository.save(other)

        listed = await repository.list_conversations(USER_ID)

    assert [conversation.id for conversation in listed] == [CONVERSATION_2_ID, CONVERSATION_1_ID]


@pytest.mark.anyio
async def test_sqlalchemy_repository_preserves_message_order(
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    now = datetime.now(UTC)
    conversation = Conversation(
        id=CONVERSATION_1_ID,
        title="Demo",
        created_at=now,
        schema_id=SCHEMA_ID,
        user_id=USER_ID,
        messages=[
            Message(id=MESSAGE_2_ID, role=MessageRole.ASSISTANT, content="second", timestamp=now + timedelta(seconds=1)),
            Message(id=MESSAGE_1_ID, role=MessageRole.USER, content="first", timestamp=now),
        ],
    )

    async with session_factory() as session:
        session.add(UserRecord(id=USER_ID, username="demo_user", email="demo@example.com", password="password", created_at=now, role="user"))
        await session.commit()
        await SqlAlchemyQuerySchemasRepository(session).save(
            QuerySchema(SCHEMA_ID, "sales", "", "", "context", now, now)
        )
        repository = SqlAlchemyConversationsRepository(session)
        await repository.save(conversation)
        fetched = await repository.get_conversation(CONVERSATION_1_ID, USER_ID)

    assert fetched is not None
    assert [message.id for message in fetched.messages] == [MESSAGE_1_ID, MESSAGE_2_ID]
