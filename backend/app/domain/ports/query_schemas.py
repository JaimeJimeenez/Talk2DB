from abc import ABC, abstractmethod

from app.domain.entities.query_schema import QuerySchema


class QuerySchemasRepository(ABC):
    @abstractmethod
    async def save(self, schema: QuerySchema) -> QuerySchema:
        raise NotImplementedError

    @abstractmethod
    async def get(self, schema_id: str) -> QuerySchema | None:
        raise NotImplementedError

    @abstractmethod
    async def list(self) -> list[QuerySchema]:
        raise NotImplementedError
