from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from time import perf_counter
from typing import Any

from app.application.rag.database import DatabaseSchemaLoader, ReadonlySQLExecutor
from app.application.rag.llm import SqlGenerator
from app.application.rag.schema_context import SchemaContextService
from app.application.rag.sql import repair_sql_identifiers, validate_sql
from app.domain.entities.query_schema import QuerySchema
from app.domain.ports.schemas import SchemasPort


class RagError(Exception):
    def __init__(
        self,
        message: str,
        generated_sql: str | None = None,
        trace: "RagTrace | None" = None,
    ) -> None:
        super().__init__(message)
        self.generated_sql = generated_sql
        self.trace = trace


@dataclass(frozen=True)
class RagResult:
    answer: str
    sql: str | None
    columns: list[str]
    rows: list[dict[str, Any]]
    row_count: int
    error: str | None = None
    trace: "RagTrace | None" = None


@dataclass(frozen=True)
class RagTrace:
    status: str
    started_at: datetime
    completed_at: datetime
    duration_ms: int
    attempt_count: int
    repair_count: int
    sql_validated: bool
    sql_executed: bool
    row_count: int
    truncated: bool
    used_context: bool
    context_message_count: int
    model: str
    schema_name: str
    retrieved_tables: list[str]
    error: str | None = None


class RagService:
    def __init__(
        self,
        *,
        schemas: SchemasPort,
        schema_loader: DatabaseSchemaLoader,
        schema_context: SchemaContextService,
        sql_generator: SqlGenerator,
        sql_executor: ReadonlySQLExecutor,
        model_name: str = "",
    ) -> None:
        self._schemas = schemas
        self._schema_loader = schema_loader
        self._schema_context = schema_context
        self._sql_generator = sql_generator
        self._sql_executor = sql_executor
        self._model_name = model_name

    async def answer(
        self,
        question: str,
        schema_id: str,
        conversation_context: str | None = None,
    ) -> RagResult:
        started_at = datetime.now(UTC)
        start_time = perf_counter()
        attempt_count = 0
        sql_validated = False
        sql_executed = False
        retrieved_tables: list[str] = []
        generated_sql: str | None = None
        query_schema = await self._get_query_schema(schema_id)
        full_schema = await self._schema_loader.load_database_schema(query_schema.name)
        guidance = "\n\n".join(
            value.strip()
            for value in (query_schema.business_rules, query_schema.context)
            if value.strip()
        )
        resolved_question = await self._sql_generator.rewrite_follow_up_question(
            question,
            conversation_context=conversation_context,
        )
        relevant_schema = await self._schema_context.retrieve_relevant_schema(
            full_schema,
            resolved_question,
            guidance=guidance,
        )
        retrieved_tables = _table_ids(relevant_schema)
        schema_text = self._schema_context.format_for_prompt(relevant_schema)
        if query_schema.business_rules.strip():
            schema_text = f"{schema_text}\n\nBusiness rules:\n{query_schema.business_rules.strip()}"
        if query_schema.context.strip():
            schema_text = (
                f"{schema_text}\n\n"
                "Curated schema guidance, business rules and examples:\n"
                f"{query_schema.context.strip()}"
            )

        last_error: Exception | None = None
        for attempt in range(5):
            attempt_count = attempt + 1
            if attempt == 0:
                generated_sql = await self._sql_generator.generate_sql(
                    resolved_question,
                    schema_text,
                    conversation_context=conversation_context,
                )
            else:
                generated_sql = await self._sql_generator.repair_sql(
                    question=resolved_question,
                    schema_text=schema_text,
                    failed_sql=generated_sql or "",
                    error=str(last_error),
                    conversation_context=conversation_context,
                )
            generated_sql = repair_sql_identifiers(generated_sql, relevant_schema)

            try:
                validated_sql = validate_sql(generated_sql)
                sql_validated = True
                columns, rows = await self._sql_executor.execute(validated_sql)
                sql_executed = True
                break
            except Exception as exc:
                last_error = exc
        else:
            completed_at = datetime.now(UTC)
            raise RagError(
                str(last_error),
                generated_sql=generated_sql,
                trace=self._trace(
                    status="error",
                    started_at=started_at,
                    completed_at=completed_at,
                    start_time=start_time,
                    attempt_count=attempt_count,
                    sql_validated=sql_validated,
                    sql_executed=sql_executed,
                    row_count=0,
                    conversation_context=conversation_context,
                    schema_name=query_schema.name,
                    retrieved_tables=retrieved_tables,
                    error=str(last_error),
                ),
            )

        completed_at = datetime.now(UTC)
        return RagResult(
            answer=self._default_answer(columns, rows),
            sql=validated_sql,
            columns=columns,
            rows=rows,
            row_count=len(rows),
            trace=self._trace(
                status="success",
                started_at=started_at,
                completed_at=completed_at,
                start_time=start_time,
                attempt_count=attempt_count,
                sql_validated=sql_validated,
                sql_executed=sql_executed,
                row_count=len(rows),
                conversation_context=conversation_context,
                schema_name=query_schema.name,
                retrieved_tables=retrieved_tables,
            ),
        )

    async def title_for(self, prompt: str) -> str:
        return await self._sql_generator.generate_title(prompt)

    async def _get_query_schema(self, schema_id: str) -> QuerySchema:
        if hasattr(self._schemas, "get_schema"):
            query_schema = await self._schemas.get_schema(schema_id)
        else:
            query_schema = await self._schemas.get(schema_id)  # type: ignore[attr-defined]
        if query_schema is None:
            raise RagError(f"Schema '{schema_id}' was not found.")
        return query_schema

    def _trace(
        self,
        *,
        status: str,
        started_at: datetime,
        completed_at: datetime,
        start_time: float,
        attempt_count: int,
        sql_validated: bool,
        sql_executed: bool,
        row_count: int,
        conversation_context: str | None,
        schema_name: str,
        retrieved_tables: list[str],
        error: str | None = None,
    ) -> RagTrace:
        return RagTrace(
            status=status,
            started_at=started_at,
            completed_at=completed_at,
            duration_ms=max(0, int((perf_counter() - start_time) * 1000)),
            attempt_count=attempt_count,
            repair_count=max(0, attempt_count - 1),
            sql_validated=sql_validated,
            sql_executed=sql_executed,
            row_count=row_count,
            truncated=False,
            used_context=bool(conversation_context and conversation_context.strip()),
            context_message_count=_context_message_count(conversation_context),
            model=self._model_name,
            schema_name=schema_name,
            retrieved_tables=retrieved_tables,
            error=error,
        )

    @staticmethod
    def _default_answer(columns: list[str], rows: list[dict[str, Any]]) -> str:
        if not rows:
            return "No he encontrado resultados para esa consulta."
        if not columns:
            return f"He obtenido {len(rows)} filas, pero la consulta no devolvió columnas con nombre."

        preview_rows = rows[:3]
        label_column = _first_column_matching(columns, rows, lambda value: isinstance(value, str))
        numeric_column = _first_column_matching(columns, rows, lambda value: isinstance(value, (int, float)))

        if label_column and numeric_column and label_column != numeric_column:
            metric_name = _humanize_identifier(numeric_column)
            category_text = "1 categoría" if len(rows) == 1 else f"{len(rows)} categorías"
            details = "; ".join(
                f"{_format_value(row.get(label_column))}: {_format_value(row.get(numeric_column))}"
                for row in preview_rows
            )
            suffix = "..." if len(rows) > len(preview_rows) else "."
            return f"He calculado {metric_name} para {category_text}. {details}{suffix}"

        if len(rows) == 1:
            row = rows[0]
            details = ", ".join(
                f"{_humanize_identifier(column)}: {_format_value(row.get(column))}"
                for column in columns[:4]
            )
            return f"He encontrado 1 resultado: {details}."

        displayed_columns = columns[:3]
        details = "; ".join(
            ", ".join(
                f"{_humanize_identifier(column)}: {_format_value(row.get(column))}"
                for column in displayed_columns
            )
            for row in preview_rows
        )
        suffix = "..." if len(rows) > len(preview_rows) else "."
        return f"He obtenido {len(rows)} filas. Primeros resultados: {details}{suffix}"


def _first_column_matching(columns: list[str], rows: list[dict[str, Any]], predicate) -> str | None:
    for column in columns:
        if any(predicate(row.get(column)) for row in rows):
            return column
    return None


def _table_ids(schema: dict[str, Any]) -> list[str]:
    return [
        f"{schema_name}.{table_name}"
        for schema_name, tables in schema.items()
        for table_name in tables.keys()
    ]


def _context_message_count(conversation_context: str | None) -> int:
    if not conversation_context:
        return 0
    return sum(
        1
        for line in conversation_context.splitlines()
        if line.startswith("user: ") or line.startswith("assistant: ")
    )


def _humanize_identifier(identifier: str) -> str:
    return identifier.replace("_", " ").strip().lower()


def _format_value(value: Any) -> str:
    if isinstance(value, float):
        return f"{value:,.2f}".rstrip("0").rstrip(".")
    if isinstance(value, str) and len(value) >= 10:
        if value[4:5] == "-" and value[7:8] == "-" and "T00:00:00" in value:
            if value[8:10] == "01":
                return value[:7]
            return value[:10]
    if value is None:
        return "sin valor"
    return str(value)
