from datetime import UTC, datetime

import pytest

from app.application.use_cases.conversations import Conversations
from app.application.use_cases.messages import Messages
from app.application.use_cases.users import Users
from app.domain.entities.conversation import Conversation
from app.domain.entities.user import User, UserRole
from app.domain.errors import ConversationNotFoundError
from app.domain.errors import UserAlreadyExistsError
from app.testing.in_memory_conversations import (
    InMemoryConversationRepository,
)
from app.testing.mock_assistant import MockAssistantGateway
from app.infrastructure.security.passwords import verify_password

USER_ID = "user-1"


class InMemoryUsersRepository:
    def __init__(self) -> None:
        self.users: dict[str, User] = {}

    async def get_by_username(self, username: str) -> User | None:
        return next((user for user in self.users.values() if user.username == username), None)

    async def get_by_email(self, email: str) -> User | None:
        return next((user for user in self.users.values() if user.email == email), None)

    async def save(self, user: User) -> User:
        self.users[user.id] = user
        return user


@pytest.mark.anyio
async def test_conversation_use_cases_create_get_and_list() -> None:
    repository = InMemoryConversationRepository()
    use_case = Conversations(repository)

    created = await use_case.create_conversation("sales", USER_ID)
    fetched = await use_case.get_conversation(created.id, USER_ID)
    listed = await use_case.list_conversations(USER_ID)

    assert fetched == created
    assert listed == [created]


@pytest.mark.anyio
async def test_get_unknown_conversation_raises_domain_error() -> None:
    use_case = Conversations(InMemoryConversationRepository())

    with pytest.raises(ConversationNotFoundError):
        await use_case.get_conversation("unknown", USER_ID)


@pytest.mark.anyio
async def test_messages_use_case_persists_prompt_and_response() -> None:
    repository = InMemoryConversationRepository()
    conversation = Conversation(id="c1", title="Demo", created_at=datetime.now(UTC), schema_id="sales", user_id=USER_ID)
    await repository.save(conversation)
    use_case = Messages(repository, MockAssistantGateway())

    response = await use_case.save_message("c1", "show users", USER_ID)
    stored = await repository.get_conversation("c1", USER_ID)

    assert response.role.value == "assistant"
    assert stored is not None
    assert [message.role.value for message in stored.messages] == ["user", "assistant"]


@pytest.mark.anyio
async def test_users_use_case_creates_default_user() -> None:
    repository = InMemoryUsersRepository()
    use_case = Users(repository)

    user = await use_case.create_user("demo_user", "demo@example.com", "password")

    assert user.id
    assert user.username == "demo_user"
    assert user.email == "demo@example.com"
    assert user.password != "password"
    assert verify_password("password", user.password)
    assert user.role == UserRole.User
    assert repository.users[user.id] == user


@pytest.mark.anyio
async def test_users_use_case_logs_in_with_email_and_password() -> None:
    repository = InMemoryUsersRepository()
    use_case = Users(repository)
    created = await use_case.create_user("demo_user", "demo@example.com", "password")

    logged_in = await use_case.login("demo@example.com", "password")

    assert logged_in == created


@pytest.mark.anyio
async def test_users_use_case_rejects_existing_username() -> None:
    repository = InMemoryUsersRepository()
    use_case = Users(repository)
    await use_case.create_user("demo_user", "demo@example.com", "password")

    with pytest.raises(UserAlreadyExistsError):
        await use_case.create_user("demo_user", "other@example.com", "password")


@pytest.mark.anyio
async def test_users_use_case_rejects_existing_email() -> None:
    repository = InMemoryUsersRepository()
    use_case = Users(repository)
    await use_case.create_user("demo_user", "demo@example.com", "password")

    with pytest.raises(UserAlreadyExistsError):
        await use_case.create_user("other_user", "demo@example.com", "password")
