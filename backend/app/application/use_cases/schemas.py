from app.domain.ports.schemas import SchemasPort

from app.infrastructure.adapters.schemas import SchemasAdapter

class SchemasUseCase(SchemasPort):

    def __init__(self, schemas_adapter: SchemasAdapter):
        self._schemas_adapter = schemas_adapter

    async def get_schemas(self):
        return await self._schemas_adapter.get_schemas()
    
    async def get_schema(self, schema_id: str):
        return await self._schemas_adapter.get_schema(schema_id)
    
