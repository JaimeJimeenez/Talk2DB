from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.query_schema import QuerySchema
from app.domain.ports.query_schemas import QuerySchemasRepository
from app.infrastructure.persistence.orm.query_schema_records import QuerySchemaRecord


class SqlAlchemyQuerySchemasRepository(QuerySchemasRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, schema: QuerySchema) -> QuerySchema:
        record = await self._session.get(QuerySchemaRecord, schema.id)
        if record is None:
            record = QuerySchemaRecord(id=schema.id)
            self._session.add(record)
        record.name = schema.name
        record.description = schema.description
        record.business_rules = schema.business_rules
        record.context = schema.context
        record.created_at = schema.created_at
        record.refreshed_at = schema.refreshed_at
        await self._session.commit()
        await self._session.refresh(record)
        return self._to_domain(record)

    async def get(self, schema_id: str) -> QuerySchema | None:
        record = await self._session.get(QuerySchemaRecord, schema_id)
        return self._to_domain(record) if record is not None else None

    async def list(self) -> list[QuerySchema]:
        records = await self._session.scalars(
            select(QuerySchemaRecord).order_by(QuerySchemaRecord.name)
        )
        return [self._to_domain(record) for record in records]

    @staticmethod
    def _to_domain(record: QuerySchemaRecord) -> QuerySchema:
        return QuerySchema(
            id=record.id,
            name=record.name,
            description=record.description,
            business_rules=record.business_rules,
            context=record.context,
            created_at=record.created_at,
            refreshed_at=record.refreshed_at,
        )
