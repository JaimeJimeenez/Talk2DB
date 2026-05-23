from datetime import UTC, datetime

import pytest

from app.application.use_cases.query_schemas import QuerySchemas
from app.domain.entities.query_schema import QuerySchema
from app.infrastructure.rag.sql_safety import validate_select_sql
from app.testing.in_memory_query_schemas import InMemoryQuerySchemasRepository


class FakeContextBuilder:
    def __init__(self) -> None:
        self.calls: list[tuple[str, str]] = []

    async def build(self, schema_name: str, business_rules: str = "") -> str:
        self.calls.append((schema_name, business_rules))
        return f"context for {schema_name}: {business_rules}"


def test_validate_select_sql_qualifies_allowed_schema() -> None:
    sql, error = validate_select_sql("SELECT id FROM customers", "sales")

    assert error is None
    assert sql is not None
    assert "sales.customers" in sql


@pytest.mark.parametrize("sql", ["DELETE FROM sales.customers", "SELECT 1; SELECT 2", "SELECT * FROM private.users"])
def test_validate_select_sql_rejects_unsafe_or_foreign_queries(sql: str) -> None:
    validated, error = validate_select_sql(sql, "sales")

    assert validated is None
    assert error is not None


@pytest.mark.anyio
async def test_refresh_rebuilds_schema_context() -> None:
    repository = InMemoryQuerySchemasRepository()
    builder = FakeContextBuilder()
    now = datetime.now(UTC)
    await repository.save(QuerySchema("s1", "sales", "", "paid orders only", "old", now, now))
    use_case = QuerySchemas(repository, builder)  # type: ignore[arg-type]

    refreshed = await use_case.refresh("s1")

    assert refreshed.context == "context for sales: paid orders only"
    assert builder.calls == [("sales", "paid orders only")]
