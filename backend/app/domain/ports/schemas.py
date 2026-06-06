from abc import ABC, abstractmethod

class SchemasPort(ABC):

    @abstractmethod
    async def get_schemas(self):
        raise NotImplementedError

    @abstractmethod
    async def get_schema(self, schema_id: str):
        raise NotImplementedError

    @abstractmethod
    async def get_schema_detail(self, schema_id: str):
        raise NotImplementedError

    @abstractmethod
    async def import_schema(self, **kwargs):
        raise NotImplementedError
