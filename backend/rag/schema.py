import logging

from typing import List, Dict
from datetime import date
from decimal import Decimal

import psycopg
from psycopg import sql
from psycopg.rows import dict_row

from models.graph import DbGraphState
from constants.sql import DATABASE_URL, INFORMATION_SCHEMA_QUERY, FOREIGN_QUERY
from constants.rag import QUERY_SCHEMA

logger = logging.getLogger('uvicorn')

def _read_sample_rows(connection: psycopg.Connection, table_names: List[str]) -> Dict[str, List[Dict]]:
    samples: dict[str, list[dict]] = {}

    with connection.cursor(row_factory=dict_row) as cursor:
        for table_name in table_names:
            query = sql.SQL("SELECT * FROM {} LIMIT 3").format(
                sql.Identifier(table_name)
            )
            cursor.execute(query)
            samples[table_name] = [dict(row) for row in cursor.fetchall()]

    return samples

def _format_sample_value(value: object) -> str:
    if isinstance(value, str):
        return repr(value)
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, Decimal):
        return str(value)
    return repr(value)

def _format_schema(
    columns: List[Dict],
    primary_keys: List[Dict],
    foreign_keys: List[Dict],
    samples: Dict[str, List[Dict]],
) -> str:
    primary_key_columns = {
        (row["table_name"], row["column_name"])
        for row in primary_keys
    }

    foreign_key_map = {
        (row["table_name"], row["column_name"]): (
            row["foreign_table_name"],
            row["foreign_column_name"],
        )
        for row in foreign_keys
    }

    tables: dict[str, list[str]] = {}
    for row in columns:
        table_name = row["table_name"]
        column_name = row["column_name"]
        data_type = row["data_type"]
        nullable = "nullable" if row["is_nullable"] == "YES" else "not null"
        notes = [data_type, nullable]

        if (table_name, column_name) in primary_key_columns:
            notes.append("primary key")

        if (table_name, column_name) in foreign_key_map:
            foreign_table, foreign_column = foreign_key_map[(table_name, column_name)]
            notes.append(f"foreign key -> {foreign_table}.{foreign_column}")

        tables.setdefault(table_name, []).append(
            f"  - {column_name}: {', '.join(notes)}"
        )

    sections: list[str] = []
    for table_name, column_lines in tables.items():
        sections.append(f"table {table_name}")
        sections.extend(column_lines)

        table_samples = samples.get(table_name, [])
        if table_samples:
            sections.append("  sample rows:")
            for sample in table_samples:
                sample_values = ", ".join(
                    f"{key}={_format_sample_value(value)}"
                    for key, value in sample.items()
                )
                sections.append(f"    - {sample_values}")

        sections.append("")

    if foreign_keys:
        sections.append("relationships")
        for row in foreign_keys:
            sections.append(
                "  - "
                f"{row['table_name']}.{row['column_name']} -> "
                f"{row['foreign_table_name']}.{row['foreign_column_name']}"
            )

    return "\n".join(sections).strip()

def read_schema(state: DbGraphState) -> DbGraphState:
    logger.info('Reading schema...')

    with psycopg.connect(DATABASE_URL) as connection:
        with connection.cursor(row_factory=dict_row) as cursor:
            cursor.execute(QUERY_SCHEMA)
            columns = [dict(row) for row in cursor.fetchall()]

            cursor.execute(INFORMATION_SCHEMA_QUERY)
            primary_keys = [dict(row) for row in cursor.fetchall()]

            cursor.execute(FOREIGN_QUERY)
            foreign_keys = [dict(row) for row in cursor.fetchall()]

        table_names = list(dict.fromkeys(row["table_name"] for row in columns))
        samples = _read_sample_rows(connection, table_names)
        schema = _format_schema(columns, primary_keys, foreign_keys, samples)

        logger.info("Schema:\n%s", schema)
        return { "schema": schema }
