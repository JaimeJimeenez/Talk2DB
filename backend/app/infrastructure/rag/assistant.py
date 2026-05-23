from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from app.domain.ports.assistant import AssistantGateway, AssistantReply
from app.domain.ports.query_schemas import QuerySchemasRepository
from app.infrastructure.rag.openai_client import OpenAITextClient
from app.infrastructure.rag.sql_safety import validate_select_sql

SQL_INSTRUCTIONS = """
You translate natural language questions into one PostgreSQL SELECT query.
Return SQL only. Use only the allowed schema and the supplied context.
Never use DDL or write statements. Add LIMIT 100 unless the result is aggregate-only.
If the question cannot be answered, return exactly: -- CANNOT_ANSWER
""".strip()

ANSWER_INSTRUCTIONS = """
Answer the user's question from the SQL result.
Be brief, do not invent facts, and answer in the same language as the question.
""".strip()


class RagAssistantGateway(AssistantGateway):
    def __init__(
        self,
        schemas: QuerySchemasRepository,
        engine: AsyncEngine,
        llm: OpenAITextClient,
    ) -> None:
        self._schemas = schemas
        self._engine = engine
        self._llm = llm

    async def reply_to(self, content: str, schema_id: str) -> AssistantReply:
        schema = await self._schemas.get(schema_id)
        if schema is None:
            return AssistantReply("No he podido resolver la consulta: el schema no está registrado.", error="schema_not_found")

        raw_sql = self._llm.complete(
            SQL_INSTRUCTIONS,
            f"Allowed schema: {schema.name}\n\nContext:\n{schema.context}\n\nQuestion:\n{content}\n\nSQL:",
        ).strip().strip("`")
        if raw_sql.upper().startswith("-- CANNOT_ANSWER"):
            return AssistantReply(
                "No he podido resolver la consulta con el schema disponible.",
                error="cannot_answer",
            )
        sql, error = validate_select_sql(raw_sql, schema.name)
        if error or sql is None:
            return AssistantReply(f"No he podido resolver la consulta: {error}", error=error)

        try:
            async with self._engine.connect() as connection:
                rows = [dict(row._mapping) for row in (await connection.execute(text(sql))).all()]
        except Exception as exc:
            return AssistantReply(f"No he podido resolver la consulta: {exc}", sql=sql, error="execution_failed")

        answer = self._llm.complete(
            ANSWER_INSTRUCTIONS,
            f"Question:\n{content}\n\nExecuted SQL:\n{sql}\n\nRows:\n{rows}",
        )
        return AssistantReply(content=answer, sql=sql)
