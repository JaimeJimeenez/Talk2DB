from contextlib import AbstractContextManager
from typing import Callable

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.entities.query_schema import QuerySchema
from app.infrastructure.adapters.database.models.query_schemas import QuerySchemaRecord


class SchemasAdapter:

    def __init__(
        self,
        session_factory: Callable[..., AbstractContextManager[Session]],
    ) -> None:
        self._session_factory = session_factory

    async def get_schemas(self):
        with self._session_factory() as session:
            records = session.execute(select(QuerySchemaRecord)).scalars().all()
            return [self._to_entity(record) for record in records]
    
    async def get_schema(self, schema_id: str):
        with self._session_factory() as session:
            record = session.get(QuerySchemaRecord, schema_id)
            return self._to_entity(record) if record is not None else None

    @staticmethod
    def _to_entity(record: QuerySchemaRecord) -> QuerySchema:
        return QuerySchema(
            id=record.id,
            name=record.name,
            description=record.description,
            business_rules=record.business_rules,
            context=record.context,
            created_at=record.created_at,
            refreshed_at=record.refreshed_at,
        )
