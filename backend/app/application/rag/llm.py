from __future__ import annotations

import json
from typing import Protocol
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from langchain_core.messages import HumanMessage, SystemMessage


class ChatModel(Protocol):
    async def ainvoke(self, messages: list[object]) -> object:
        ...


class EmbeddingGateway:
    def __init__(self, *, model: str, base_url: str) -> None:
        self.model = model
        self._base_url = base_url.rstrip("/")

    async def embed_text(self, text: str) -> list[float]:
        url = f"{self._base_url}/api/embeddings"
        payload = json.dumps({"model": self.model, "prompt": text}).encode("utf-8")
        request = Request(url, data=payload, headers={"Content-Type": "application/json"}, method="POST")
        try:
            with urlopen(request, timeout=60) as response:
                body = json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"Ollama embedding request failed: {detail}") from exc
        except (TimeoutError, URLError) as exc:
            raise RuntimeError(f"Could not reach Ollama embeddings API: {exc}") from exc
        embedding = body.get("embedding")
        if not isinstance(embedding, list):
            raise RuntimeError("Ollama embedding response did not include an embedding.")
        return [float(value) for value in embedding]

    async def embed_documents(self, documents: list[str]) -> list[list[float]]:
        return [await self.embed_text(document) for document in documents]


class ChatResponse:
    def __init__(self, content: str) -> None:
        self.content = content


class OllamaChatModel:
    def __init__(self, *, model: str, base_url: str) -> None:
        self.model = model
        self._base_url = base_url.rstrip("/")

    async def ainvoke(self, messages: list[object]) -> ChatResponse:
        url = f"{self._base_url}/api/chat"
        payload = json.dumps(
            {
                "model": self.model,
                "messages": [self._message_payload(message) for message in messages],
                "stream": False,
            }
        ).encode("utf-8")
        request = Request(url, data=payload, headers={"Content-Type": "application/json"}, method="POST")
        try:
            with urlopen(request, timeout=120) as response:
                body = json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"Ollama chat request failed: {detail}") from exc
        except (TimeoutError, URLError) as exc:
            raise RuntimeError(f"Could not reach Ollama chat API: {exc}") from exc
        content = body.get("message", {}).get("content")
        if not isinstance(content, str):
            raise RuntimeError("Ollama chat response did not include message content.")
        return ChatResponse(content)

    @staticmethod
    def _message_payload(message: object) -> dict[str, str]:
        content = str(getattr(message, "content", message))
        role_name = message.__class__.__name__.lower()
        role = "system" if "system" in role_name else "user"
        return {"role": role, "content": content}


class SqlGenerator:
    SYSTEM_PROMPT = """
You are a senior PostgreSQL expert.

Your task is to generate a safe SQL SELECT query from a natural language question.

Rules:
- Generate PostgreSQL SQL.
- Use only the tables and columns provided in the database schema.
- Use schema-qualified table names.
- Every table reference must be schema-qualified, including JOIN tables.
- Generate the simplest query that answers the question.
- Use exact column names from the schema context. Do not shorten, rename, or substitute column names with synonyms.
- Never use a column unless it appears under that exact table in the schema context.
- Never infer that a column exists on a related table.
- Do not add filters that the user did not request unless an explicit business rule requires them.
- If a business rule says to exclude one status/category/value, include all other values unless the user asks otherwise.
- Do not apply "active" filters unless the user asks for active records or a business rule explicitly requires active records for that metric.
- Do not mix values between columns. A value listed for one column cannot be used as a value for another column.
- Do not join tables unless the question needs columns or filters from more than one table.
- Prefer not to use table aliases for simple single-table queries.
- If you use a table alias, reference columns only through that alias.
- Do not invent aliases that were not declared in the FROM or JOIN clauses.
- For PostgreSQL date grouping by month, use DATE_TRUNC('month', column), never STRFTIME.
- Apply the provided business rules and examples when they match the user's metric.
- If curated examples include a question similar to the user question, follow that SQL pattern.
- Interpret snake_case identifiers by their words.
- Use table and column descriptions when present.
- Generate only one SQL query.
- Generate only SELECT queries.
- Do not generate INSERT, UPDATE, DELETE, DROP, ALTER, TRUNCATE, CREATE or any write operation.
- Do not explain the query.
- Do not wrap the query in markdown.
- If the question cannot be answered with the provided schema, return exactly: I_DO_NOT_KNOW
""".strip()

    def __init__(self, llm: ChatModel) -> None:
        self._llm = llm

    async def rewrite_follow_up_question(
        self,
        question: str,
        conversation_context: str | None = None,
    ) -> str:
        if not conversation_context or not conversation_context.strip():
            return question

        response = await self._llm.ainvoke(
            [
                SystemMessage(
                    content=(
                        "Rewrite follow-up analytics questions into standalone questions. "
                        "Use the previous conversation only to resolve references, pronouns, "
                        "omitted filters, requested columns, comparisons and sort criteria. "
                        "Prefer the immediately previous user/assistant exchange when resolving references. "
                        "Preserve relevant filters, joins, metrics and ORDER BY intent from previous SQL. "
                        "Return only the rewritten question, with no markdown and no explanation."
                    )
                ),
                HumanMessage(
                    content=(
                        "Previous conversation messages, oldest first:\n\n"
                        f"{conversation_context.strip()}\n\n"
                        "Current user question:\n\n"
                        f"{question}\n\n"
                        "Standalone question:"
                    )
                ),
            ]
        )
        rewritten = str(getattr(response, "content", response)).strip().strip('"').strip("'")
        return rewritten or question

    async def generate_sql(
        self,
        question: str,
        schema_text: str,
        conversation_context: str | None = None,
    ) -> str:
        response = await self._llm.ainvoke(
            [
                SystemMessage(content=self.SYSTEM_PROMPT),
                HumanMessage(
                    content=(
                        "Relevant database schema subset:\n\n"
                        f"{schema_text}\n\n"
                        f"{_conversation_context_section(conversation_context)}"
                        "User question:\n\n"
                        f"{question}\n\n"
                        "Return only the SQL query."
                    )
                ),
            ]
        )
        return clean_sql_output(str(getattr(response, "content", response)))

    async def repair_sql(
        self,
        *,
        question: str,
        schema_text: str,
        failed_sql: str,
        error: str,
        conversation_context: str | None = None,
    ) -> str:
        response = await self._llm.ainvoke(
            [
                SystemMessage(content=self.SYSTEM_PROMPT),
                HumanMessage(
                    content=(
                        "Relevant database schema subset:\n\n"
                        f"{schema_text}\n\n"
                        f"{_conversation_context_section(conversation_context)}"
                        "The previous SQL query failed. Repair it using only the schema above.\n\n"
                        "Original user question:\n\n"
                        f"{question}\n\n"
                        "Failed SQL:\n\n"
                        f"{failed_sql}\n\n"
                        "Database or validation error:\n\n"
                        f"{error}\n\n"
                        "Return only one corrected PostgreSQL SELECT query. "
                        "Do not explain the query."
                    )
                ),
            ]
        )
        return clean_sql_output(str(getattr(response, "content", response)))

    async def generate_title(self, prompt: str) -> str:
        response = await self._llm.ainvoke(
            [
                SystemMessage(
                    content=(
                        "Generate a short conversation title in the same language as the user. "
                        "Return only the title, with no quotes, no markdown and at most 56 characters."
                    )
                ),
                HumanMessage(content=prompt),
            ]
        )
        title = str(getattr(response, "content", response)).strip().strip('"').strip("'")
        return title[:56].strip() or fallback_title(prompt)


def clean_sql_output(sql: str) -> str:
    cleaned = sql.strip()
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        if lines and lines[0].strip().lower() in {"```", "```sql", "```postgres", "```postgresql"}:
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        cleaned = "\n".join(lines).strip()
    cleaned = cleaned.strip().replace("`", '"')
    select_index = cleaned.lower().find("select")
    if select_index > 0:
        cleaned = cleaned[select_index:]
    statement_end = cleaned.find(";")
    if statement_end >= 0:
        cleaned = cleaned[:statement_end]
    return cleaned.strip().rstrip(";").strip()


def _conversation_context_section(conversation_context: str | None) -> str:
    if not conversation_context:
        return ""
    return (
        "Previous conversation messages, oldest first:\n\n"
        f"{conversation_context.strip()}\n\n"
        "Use this context only to resolve follow-up references, omitted filters, pronouns, or comparisons. "
        "The current user question remains the source of truth.\n\n"
    )


def fallback_title(prompt: str) -> str:
    normalized = " ".join(prompt.strip().split()).strip(" ¿?¡!.,;:")
    if not normalized:
        return "New Conversation"
    return normalized[:53].rstrip(" .,;:") + ("..." if len(normalized) > 56 else "")
