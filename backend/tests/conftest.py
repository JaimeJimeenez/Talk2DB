import asyncio
from collections.abc import AsyncIterator, Iterator

import pytest
import jwt
from dependency_injector import providers
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.settings import get_settings
from app.testing.mock_assistant import MockAssistantGateway
from app.infrastructure.persistence.orm.base import Base
from app.domain.entities.query_schema import QuerySchema
from app.infrastructure.persistence.orm.user_records import UserRecord
from app.infrastructure.persistence.repositories.query_schemas import SqlAlchemyQuerySchemasRepository
from app.infrastructure.persistence.session import get_session
from app.infrastructure.security.passwords import hash_password
from app.main import app

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
TEST_SCHEMA_ID = "00000000-0000-0000-0000-000000000001"
TEST_USER_ID = "00000000-0000-0000-0000-000000000101"
OTHER_USER_ID = "00000000-0000-0000-0000-000000000102"
TEST_USERNAME = "demo_user"
OTHER_USERNAME = "other_user"
TEST_EMAIL = "demo@example.com"
OTHER_EMAIL = "other@example.com"
TEST_PASSWORD = "password"


@pytest.fixture
async def session_factory() -> AsyncIterator[async_sessionmaker[AsyncSession]]:
    engine = create_async_engine(TEST_DATABASE_URL)
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    factory = async_sessionmaker(engine, expire_on_commit=False)
    yield factory
    await engine.dispose()


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


def build_token(username: str) -> str:
    settings = get_settings()
    return jwt.encode(
        {"sub": username},
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )


@pytest.fixture
def auth_headers() -> dict[str, str]:
    return {"Authorization": f"Bearer {build_token(TEST_USERNAME)}"}


@pytest.fixture
def other_auth_headers() -> dict[str, str]:
    return {"Authorization": f"Bearer {build_token(OTHER_USERNAME)}"}


@pytest.fixture
def client() -> Iterator[TestClient]:
    engine = create_async_engine(TEST_DATABASE_URL)
    factory = async_sessionmaker(engine, expire_on_commit=False)

    async def create_schema() -> None:
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)
        async with factory() as session:
            from datetime import UTC, datetime
            now = datetime.now(UTC)
            session.add_all(
                [
                    UserRecord(
                        id=TEST_USER_ID,
                        username=TEST_USERNAME,
                        email=TEST_EMAIL,
                        password=hash_password(TEST_PASSWORD),
                        created_at=now,
                        role="user",
                    ),
                    UserRecord(
                        id=OTHER_USER_ID,
                        username=OTHER_USERNAME,
                        email=OTHER_EMAIL,
                        password=hash_password(TEST_PASSWORD),
                        created_at=now,
                        role="user",
                    ),
                ]
            )
            await session.commit()
            await SqlAlchemyQuerySchemasRepository(session).save(
                QuerySchema(TEST_SCHEMA_ID, "sales", "", "", "context", now, now)
            )

    asyncio.run(create_schema())

    async def override_get_session() -> AsyncIterator[AsyncSession]:
        async with factory() as session:
            yield session

    app.state.skip_database_initialization = True
    app.dependency_overrides[get_session] = override_get_session
    with app.container.assistant_gateway.override(providers.Object(MockAssistantGateway())):
        with TestClient(app) as test_client:
            yield test_client
    app.dependency_overrides.clear()
    app.state.skip_database_initialization = False
    asyncio.run(engine.dispose())
