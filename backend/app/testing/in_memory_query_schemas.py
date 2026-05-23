from app.domain.entities.query_schema import QuerySchema
from app.domain.ports.query_schemas import QuerySchemasRepository


class InMemoryQuerySchemasRepository(QuerySchemasRepository):
    def __init__(self) -> None:
        self._schemas: dict[str, QuerySchema] = {}

    async def save(self, schema: QuerySchema) -> QuerySchema:
        self._schemas[schema.id] = schema
        return schema

    async def get(self, schema_id: str) -> QuerySchema | None:
        return self._schemas.get(schema_id)

    async def list(self) -> list[QuerySchema]:
        return sorted(self._schemas.values(), key=lambda item: item.name)
