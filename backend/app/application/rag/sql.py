from __future__ import annotations

from typing import Any

import sqlglot
from sqlglot import exp

from app.application.rag.schema_context import identifier_terms


class SQLValidationError(Exception):
    pass


FORBIDDEN_EXPRESSIONS = (
    exp.Insert,
    exp.Update,
    exp.Delete,
    exp.Drop,
    exp.Alter,
    exp.Create,
    exp.TruncateTable,
    exp.Command,
)


def validate_sql(sql: str) -> str:
    normalized = sql.strip().rstrip(";").strip()
    if not normalized:
        raise SQLValidationError("Generated SQL is empty.")
    if normalized == "I_DO_NOT_KNOW":
        raise SQLValidationError("The model could not generate a query for the provided schema.")
    try:
        parsed_expressions = sqlglot.parse(normalized, read="postgres")
    except sqlglot.errors.SqlglotError as exc:
        raise SQLValidationError(f"Invalid SQL syntax: {exc}") from exc
    if len(parsed_expressions) != 1:
        raise SQLValidationError("Only one SQL statement is allowed.")
    expression = parsed_expressions[0]
    if not isinstance(expression, exp.Select):
        raise SQLValidationError("Only SELECT statements are allowed.")
    for node in expression.walk():
        if isinstance(node, FORBIDDEN_EXPRESSIONS):
            raise SQLValidationError(f"Forbidden SQL expression detected: {type(node).__name__}")
    if expression.args.get("limit") is None:
        expression = expression.limit(100)
    return expression.sql(dialect="postgres")


def repair_sql_identifiers(sql: str, schema: dict[str, Any]) -> str:
    try:
        expression = sqlglot.parse_one(sql, read="postgres")
    except sqlglot.errors.ParseError:
        return sql
    table_aliases = _collect_table_aliases(expression)
    changed = False
    for column in expression.find_all(exp.Column):
        table_alias = column.table
        column_name = column.name
        table_id = table_aliases.get(table_alias) if table_alias else None
        replacement = _find_column_replacement(schema, column_name, table_id)
        if replacement and replacement != column_name:
            column.set("this", exp.to_identifier(replacement))
            changed = True
    return expression.sql(dialect="postgres") if changed else sql


def _collect_table_aliases(expression: exp.Expression) -> dict[str, str]:
    table_aliases: dict[str, str] = {}
    for table in expression.find_all(exp.Table):
        table_name = table.name
        db_expression = table.args.get("db")
        if not table_name or not db_expression:
            continue
        table_id = f"{db_expression.name}.{table_name}"
        table_aliases[table.alias_or_name] = table_id
        table_aliases[table_name] = table_id
    return table_aliases


def _find_column_replacement(schema: dict[str, Any], column_name: str, table_id: str | None) -> str | None:
    candidates = _candidate_columns(schema, table_id)
    if any(candidate == column_name for candidate in candidates):
        return column_name
    requested_terms = identifier_terms(column_name)
    matches = [candidate for candidate in candidates if requested_terms.issubset(identifier_terms(candidate))]
    if len(matches) == 1:
        return matches[0]
    return None


def _candidate_columns(schema: dict[str, Any], table_id: str | None) -> list[str]:
    columns: list[str] = []
    for schema_name, tables in schema.items():
        for table_name, table_info in tables.items():
            current_table_id = f"{schema_name}.{table_name}"
            if table_id and current_table_id != table_id:
                continue
            columns.extend(column["name"] for column in table_info.get("columns", []))
    return columns
