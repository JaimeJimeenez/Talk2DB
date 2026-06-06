from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine


class DatabaseSchemaLoader:
    def __init__(self, engine: AsyncEngine) -> None:
        self._engine = engine

    async def load_database_schema(self, schema_name: str | None = None) -> dict[str, Any]:
        columns_query = text(
            """
            SELECT
                n.nspname AS table_schema,
                c.relname AS table_name,
                a.attname AS column_name,
                format_type(a.atttypid, a.atttypmod) AS data_type,
                CASE WHEN a.attnotnull THEN 'NO' ELSE 'YES' END AS is_nullable,
                a.attnum AS ordinal_position,
                obj_description(c.oid, 'pg_class') AS table_comment,
                col_description(c.oid, a.attnum) AS column_comment
            FROM pg_catalog.pg_attribute a
            JOIN pg_catalog.pg_class c ON c.oid = a.attrelid
            JOIN pg_catalog.pg_namespace n ON n.oid = c.relnamespace
            WHERE a.attnum > 0
                AND NOT a.attisdropped
                AND c.relkind IN ('r', 'p', 'v', 'm', 'f')
                AND n.nspname NOT IN ('pg_catalog', 'information_schema')
                AND (CAST(:schema_name AS text) IS NULL OR n.nspname = CAST(:schema_name AS text))
            ORDER BY n.nspname, c.relname, a.attnum
            """
        )
        constraints_query = text(
            """
            SELECT
                ns.nspname AS table_schema,
                cl.relname AS table_name,
                CASE constraint_record.contype
                    WHEN 'p' THEN 'PRIMARY KEY'
                    WHEN 'f' THEN 'FOREIGN KEY'
                    WHEN 'u' THEN 'UNIQUE'
                END AS constraint_type,
                att.attname AS column_name,
                foreign_ns.nspname AS foreign_table_schema,
                foreign_cl.relname AS foreign_table_name,
                foreign_att.attname AS foreign_column_name
            FROM pg_catalog.pg_constraint constraint_record
            JOIN pg_catalog.pg_class cl
                ON cl.oid = constraint_record.conrelid
            JOIN pg_catalog.pg_namespace ns
                ON ns.oid = cl.relnamespace
            JOIN LATERAL unnest(constraint_record.conkey) WITH ORDINALITY AS constraint_key(attnum, ord)
                ON TRUE
            JOIN pg_catalog.pg_attribute att
                ON att.attrelid = cl.oid
                AND att.attnum = constraint_key.attnum
            LEFT JOIN pg_catalog.pg_class foreign_cl
                ON foreign_cl.oid = constraint_record.confrelid
            LEFT JOIN pg_catalog.pg_namespace foreign_ns
                ON foreign_ns.oid = foreign_cl.relnamespace
            LEFT JOIN LATERAL unnest(constraint_record.confkey) WITH ORDINALITY AS foreign_key(attnum, ord)
                ON foreign_key.ord = constraint_key.ord
            LEFT JOIN pg_catalog.pg_attribute foreign_att
                ON foreign_att.attrelid = foreign_cl.oid
                AND foreign_att.attnum = foreign_key.attnum
            WHERE ns.nspname NOT IN ('pg_catalog', 'information_schema')
                AND constraint_record.contype IN ('p', 'f', 'u')
                AND (CAST(:schema_name AS text) IS NULL OR ns.nspname = CAST(:schema_name AS text))
            ORDER BY ns.nspname, cl.relname, constraint_type
            """
        )
        async with self._engine.connect() as connection:
            column_rows = (await connection.execute(columns_query, {"schema_name": schema_name})).mappings().all()
            constraint_rows = (await connection.execute(constraints_query, {"schema_name": schema_name})).mappings().all()
        schema: dict[str, Any] = {}
        for row in column_rows:
            schema_name_value = row["table_schema"]
            table_name = row["table_name"]
            schema.setdefault(schema_name_value, {})
            schema[schema_name_value].setdefault(
                table_name,
                {"columns": [], "constraints": [], "description": row["table_comment"]},
            )
            schema[schema_name_value][table_name]["columns"].append(
                {
                    "name": row["column_name"],
                    "type": row["data_type"],
                    "nullable": row["is_nullable"] == "YES",
                    "position": row["ordinal_position"],
                    "description": row["column_comment"],
                }
            )
        for row in constraint_rows:
            schema_name_value = row["table_schema"]
            table_name = row["table_name"]
            if schema_name_value not in schema or table_name not in schema[schema_name_value]:
                continue
            schema[schema_name_value][table_name]["constraints"].append(
                {
                    "type": row["constraint_type"],
                    "column": row["column_name"],
                    "foreign_table_schema": row["foreign_table_schema"],
                    "foreign_table_name": row["foreign_table_name"],
                    "foreign_column_name": row["foreign_column_name"],
                }
            )
        return schema


class ReadonlySQLExecutor:
    def __init__(self, engine: AsyncEngine) -> None:
        self._engine = engine

    async def execute(self, sql: str) -> tuple[list[str], list[dict[str, Any]]]:
        async with self._engine.connect() as connection:
            async with connection.begin():
                await connection.execute(text("SET TRANSACTION READ ONLY"))
                result = await connection.execute(text(sql))
                columns = list(result.keys())
                rows = [
                    {key: _serialize_value(value) for key, value in row._mapping.items()}
                    for row in result.fetchall()
                ]
        return columns, rows


def _serialize_value(value: Any) -> Any:
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    return value
