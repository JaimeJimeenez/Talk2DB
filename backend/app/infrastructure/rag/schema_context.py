import re

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from app.domain.errors import QuerySchemaUnavailableError

SAFE_IDENTIFIER = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
INTERNAL_SCHEMAS = {"public", "information_schema", "pg_catalog"}


class SchemaContextBuilder:
    def __init__(self, engine: AsyncEngine) -> None:
        self._engine = engine

    async def build(self, schema_name: str, business_rules: str = "") -> str:
        ensure_queryable_schema_name(schema_name)
        async with self._engine.connect() as connection:
            exists = await connection.scalar(
                text(
                    "SELECT EXISTS (SELECT 1 FROM information_schema.schemata "
                    "WHERE schema_name = :schema_name)"
                ),
                {"schema_name": schema_name},
            )
            if not exists:
                raise QuerySchemaUnavailableError(f"Schema '{schema_name}' does not exist.")
            rows = (
                await connection.execute(
                    text(
                        """
                        SELECT table_name, column_name, data_type
                        FROM information_schema.columns
                        WHERE table_schema = :schema_name
                        ORDER BY table_name, ordinal_position
                        """
                    ),
                    {"schema_name": schema_name},
                )
            ).all()
            await connection.execute(text(f'GRANT USAGE ON SCHEMA "{schema_name}" TO talk2db_reader'))
            await connection.execute(
                text(f'GRANT SELECT ON ALL TABLES IN SCHEMA "{schema_name}" TO talk2db_reader')
            )
            await connection.commit()
        if not rows:
            raise QuerySchemaUnavailableError(f"Schema '{schema_name}' has no queryable tables.")

        tables: dict[str, list[str]] = {}
        for table_name, column_name, data_type in rows:
            tables.setdefault(table_name, []).append(f"- {column_name} {data_type}")

        chunks = [
            f"Schema: {schema_name}\nTable: {table}\nColumns:\n" + "\n".join(columns)
            for table, columns in tables.items()
        ]
        if business_rules.strip():
            chunks.append("Business rules:\n" + business_rules.strip())
        return "\n\n".join(chunks)


def ensure_queryable_schema_name(schema_name: str) -> None:
    if not SAFE_IDENTIFIER.fullmatch(schema_name):
        raise QuerySchemaUnavailableError("Schema name is not a safe SQL identifier.")
    if schema_name in INTERNAL_SCHEMAS:
        raise QuerySchemaUnavailableError(f"Schema '{schema_name}' cannot be registered.")
