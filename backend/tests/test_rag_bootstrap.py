import asyncio
from types import SimpleNamespace

from app.application.rag.bootstrap import seed_schema_context


class FakeSchemasUseCase:
    async def get_schemas(self):
        return [
            SimpleNamespace(
                name="ventas",
                business_rules="Excluye pedidos cancelados.",
                context="Usa lineas_pedido para ingresos.",
            ),
            SimpleNamespace(
                name="soporte",
                business_rules="Tickets abiertos son abierto o en_progreso.",
                context="Usa interacciones para minutos.",
            ),
        ]


class FakeSchemaLoader:
    def __init__(self) -> None:
        self.loaded = []

    async def load_database_schema(self, schema_name: str):
        self.loaded.append(schema_name)
        return {
            schema_name: {
                "items": {
                    "description": None,
                    "columns": [{"name": "id", "type": "text", "nullable": False}],
                    "constraints": [],
                }
            }
        }


class FakeSchemaContext:
    def __init__(self) -> None:
        self.indexed = []

    async def ensure_schema_index(self, schema, *, guidance: str = ""):
        self.indexed.append({"schema": schema, "guidance": guidance})
        return 1


def _container(*, schemas=None, loader=None, context=None):
    return SimpleNamespace(
        schemas_use_case=lambda: schemas or FakeSchemasUseCase(),
        schema_loader=lambda: loader or FakeSchemaLoader(),
        schema_context=lambda: context or FakeSchemaContext(),
    )


def test_seed_schema_context_indexes_default_query_schemas():
    loader = FakeSchemaLoader()
    context = FakeSchemaContext()

    asyncio.run(seed_schema_context(_container(loader=loader, context=context)))

    assert loader.loaded == ["ventas", "soporte"]
    assert len(context.indexed) == 2
    assert "Excluye pedidos cancelados" in context.indexed[0]["guidance"]
    assert "interacciones" in context.indexed[1]["guidance"]


def test_seed_schema_context_is_best_effort_when_one_schema_fails():
    class PartiallyFailingLoader(FakeSchemaLoader):
        async def load_database_schema(self, schema_name: str):
            if schema_name == "ventas":
                raise RuntimeError("database unavailable")
            return await super().load_database_schema(schema_name)

    loader = PartiallyFailingLoader()
    context = FakeSchemaContext()

    asyncio.run(seed_schema_context(_container(loader=loader, context=context)))

    assert loader.loaded == ["soporte"]
    assert len(context.indexed) == 1
    assert "soporte" in context.indexed[0]["schema"]
