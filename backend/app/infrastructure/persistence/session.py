from collections.abc import AsyncIterator
import asyncio
import logging

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.settings import get_settings
from app.infrastructure.persistence import orm  # noqa: F401
from app.infrastructure.persistence.orm.base import Base

logger = logging.getLogger(__name__)
settings = get_settings()
engine = create_async_engine(settings.database_url, pool_pre_ping=True)
rag_engine = create_async_engine(settings.rag_database_url, pool_pre_ping=True)
SessionFactory = async_sessionmaker(engine, expire_on_commit=False)


async def get_session() -> AsyncIterator[AsyncSession]:
    async with SessionFactory() as session:
        yield session


async def initialize_database() -> None:
    for attempt in range(1, settings.database_connection_retries + 1):
        try:
            async with engine.begin() as connection:
                await connection.run_sync(Base.metadata.create_all)
            return
        except Exception:
            if attempt >= settings.database_connection_retries:
                raise
            logger.warning(
                "Database connection failed during startup. Retrying in %.1fs (%s/%s)",
                settings.database_connection_retry_delay_seconds,
                attempt,
                settings.database_connection_retries,
                exc_info=True,
            )
            await asyncio.sleep(settings.database_connection_retry_delay_seconds)
