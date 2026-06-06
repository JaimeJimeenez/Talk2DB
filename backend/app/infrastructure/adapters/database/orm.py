from contextlib import contextmanager
from typing import Generator


from sqlalchemy import MetaData, create_engine, orm, text
from sqlalchemy.exc import OperationalError, PendingRollbackError
from sqlalchemy.orm import Session, registry

from app.core.settings import get_settings
from app.infrastructure.adapters.database.models.base import Base
from app.infrastructure.adapters.database.models import (
    ConversationsRecord,
    MessageRecord,
    QuerySchemaRecord,
    RagRunRecord,
    UserRecord,
)

settings = get_settings()

class Database:

    def __init__(self, db_url: str) -> None:
        engine_kwargs = {
            "echo": True,
            "echo_pool": True,
            "pool_recycle": 100,
            "pool_pre_ping": True,
        }
        if not db_url.startswith("sqlite"):
            engine_kwargs.update(
                {
                    "pool_timeout": 30,
                    "max_overflow": 10,
                    "pool_size": 30,
                }
            )
        self._engine = create_engine(db_url, **engine_kwargs)

        self._session_factory = orm.scoped_session(
            orm.sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self._engine
            )
        )

        self._metadata = MetaData(schema=settings.database_schema)
        self._mapper_registry = registry(metadata=self._metadata)
        self._tables = {}
        self._models = {}

        self._define_tables()

    def _define_tables(self) -> None:
        """
            TODO: Define tables here using self._metadata and store them in self._tables
        """
        return
    
    def start_mappers(self) -> None:
        """
            TODO: Start mappers here using self._mapper_registry
        """
        return
    
    def create_database(self) -> None:
        with self._engine.begin() as connection:
            if self._engine.dialect.name != "sqlite":
                connection.execute(text(f"CREATE SCHEMA IF NOT EXISTS {settings.database_schema}"))
            Base.metadata.create_all(bind=connection)
        return
    
    @contextmanager
    def session(self) -> Generator[Session, None, None]:
        """Provide a transactional scope around a series of operations."""
        session = self._session_factory()
        try:
            yield session
            session.commit()
        except (OperationalError, PendingRollbackError):
            session.rollback()
            self._session_factory.remove()
            try:
                with self._engine.begin() as new_session:
                    yield new_session
            except Exception as e:
                new_session.rollback()
                raise e
            raise
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
