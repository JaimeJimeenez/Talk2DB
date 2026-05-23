from datetime import UTC, datetime
from uuid import uuid4

from app.domain.entities.query_schema import QuerySchema
from app.domain.errors import QuerySchemaNotFoundError
from app.domain.ports.query_schemas import QuerySchemasRepository
from app.infrastructure.rag.schema_context import SchemaContextBuilder


class QuerySchemas:
    def __init__(self, repository: QuerySchemasRepository, context_builder: SchemaContextBuilder) -> None:
        self._repository = repository
        self._context_builder = context_builder

    async def register(self, name: str, description: str = "", business_rules: str = "") -> QuerySchema:
        now = datetime.now(UTC)
        context = await self._context_builder.build(name, business_rules)
        schema = QuerySchema(
            id=str(uuid4()),
            name=name,
            description=description,
            business_rules=business_rules,
            context=context,
            created_at=now,
            refreshed_at=now,
        )
        return await self._repository.save(schema)

    async def refresh(self, schema_id: str) -> QuerySchema:
        schema = await self._repository.get(schema_id)
        if schema is None:
            raise QuerySchemaNotFoundError(schema_id)
        schema.context = await self._context_builder.build(schema.name, schema.business_rules)
        schema.refreshed_at = datetime.now(UTC)
        return await self._repository.save(schema)

    async def get(self, schema_id: str) -> QuerySchema:
        schema = await self._repository.get(schema_id)
        if schema is None:
            raise QuerySchemaNotFoundError(schema_id)
        return schema

    async def list(self) -> list[QuerySchema]:
        return await self._repository.list()
