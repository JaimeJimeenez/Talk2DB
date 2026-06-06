from contextlib import AbstractContextManager
from datetime import UTC, datetime
import re
from typing import Callable
from uuid import uuid4

import sqlglot
from sqlalchemy import select, text
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.domain.entities.query_schema import (
    QuerySchema,
    QuerySchemaColumn,
    QuerySchemaConstraint,
    QuerySchemaTable,
)
from app.domain.errors import QuerySchemaImportError
from app.infrastructure.adapters.database.models.query_schemas import QuerySchemaRecord


MAX_SQL_FILE_BYTES = 1_000_000
SAFE_SCHEMA_NAME = re.compile(r"^[a-z][a-z0-9_]{0,62}$")
DANGEROUS_SQL = re.compile(
    r"\b("
    r"DROP|TRUNCATE|DELETE|UPDATE|MERGE|GRANT|REVOKE|CREATE\s+ROLE|ALTER\s+ROLE|"
    r"CREATE\s+USER|ALTER\s+USER|CREATE\s+EXTENSION|CREATE\s+FUNCTION|CREATE\s+PROCEDURE|"
    r"CREATE\s+TRIGGER|CALL|DO|COPY|VACUUM|ANALYZE|SECURITY\s+DEFINER"
    r")\b",
    re.IGNORECASE,
)


class SchemasAdapter:

    def __init__(
        self,
        session_factory: Callable[..., AbstractContextManager[Session]],
    ) -> None:
        self._session_factory = session_factory

    async def get_schemas(self):
        with self._session_factory() as session:
            records = session.execute(select(QuerySchemaRecord).order_by(QuerySchemaRecord.name)).scalars().all()
            return [self._to_entity(record, self._load_schema_summary(session, record.name)) for record in records]
    
    async def get_schema(self, schema_id: str):
        with self._session_factory() as session:
            record = session.get(QuerySchemaRecord, schema_id)
            if record is None:
                return None
            return self._to_entity(record, self._load_schema_summary(session, record.name))

    async def get_schema_detail(self, schema_id: str):
        with self._session_factory() as session:
            record = session.get(QuerySchemaRecord, schema_id)
            if record is None:
                return None
            structure = self._load_schema_structure(session, record.name)
            return self._to_entity(record, structure, include_tables=True)

    async def import_schema(
        self,
        *,
        name: str,
        description: str,
        business_rules: str,
        filename: str,
        content: bytes,
    ) -> QuerySchema:
        schema_name = _normalize_schema_name(name)
        sql_text = _decode_sql_file(filename, content)
        statements = _validate_sql(schema_name, sql_text)

        with self._session_factory() as session:
            if self._schema_record_exists(session, schema_name):
                raise QuerySchemaImportError(f"Schema '{schema_name}' already exists in the platform.")
            if self._database_schema_exists(session, schema_name):
                raise QuerySchemaImportError(f"Schema '{schema_name}' already exists in the database.")

            now = datetime.now(UTC)
            try:
                if not _has_create_schema_statement(schema_name, statements):
                    session.execute(text(f'CREATE SCHEMA "{schema_name}"'))

                for statement in statements:
                    session.execute(text(statement))

                session.execute(text(f'GRANT USAGE ON SCHEMA "{schema_name}" TO talk2db_reader'))
                session.execute(text(f'GRANT SELECT ON ALL TABLES IN SCHEMA "{schema_name}" TO talk2db_reader'))

                structure = self._load_schema_structure(session, schema_name)
                if not structure["tables"]:
                    raise QuerySchemaImportError("The SQL file must create at least one table.")

                record = QuerySchemaRecord(
                    id=str(uuid4()),
                    name=schema_name,
                    description=description.strip(),
                    business_rules=business_rules.strip(),
                    context=_build_schema_context(schema_name, structure["tables"]),
                    created_at=now,
                    refreshed_at=now,
                )
                session.add(record)
                session.flush()
            except QuerySchemaImportError:
                raise
            except IntegrityError as error:
                raise QuerySchemaImportError(f"Schema '{schema_name}' already exists in the platform.") from error
            except SQLAlchemyError as error:
                raise QuerySchemaImportError(f"The SQL file could not be applied: {error}") from error

            return self._to_entity(record, structure, include_tables=True)

    def _to_entity(
        self,
        record: QuerySchemaRecord,
        structure: dict | None = None,
        *,
        include_tables: bool = False,
    ) -> QuerySchema:
        structure = structure or {"table_count": 0, "column_count": 0, "tables": []}
        return QuerySchema(
            id=record.id,
            name=record.name,
            description=record.description,
            business_rules=record.business_rules,
            context=record.context,
            created_at=record.created_at,
            refreshed_at=record.refreshed_at,
            table_count=structure["table_count"],
            column_count=structure["column_count"],
            tables=structure["tables"] if include_tables else None,
        )

    def _schema_record_exists(self, session: Session, schema_name: str) -> bool:
        return session.execute(
            select(QuerySchemaRecord.id).where(QuerySchemaRecord.name == schema_name)
        ).scalar_one_or_none() is not None

    @staticmethod
    def _database_schema_exists(session: Session, schema_name: str) -> bool:
        return session.execute(
            text("SELECT 1 FROM information_schema.schemata WHERE schema_name = :schema_name"),
            {"schema_name": schema_name},
        ).scalar_one_or_none() is not None

    def _load_schema_summary(self, session: Session, schema_name: str) -> dict:
        structure = self._load_schema_structure(session, schema_name, include_constraints=False)
        return {
            "table_count": structure["table_count"],
            "column_count": structure["column_count"],
            "tables": [],
        }

    @staticmethod
    def _load_schema_structure(
        session: Session,
        schema_name: str,
        *,
        include_constraints: bool = True,
    ) -> dict:
        column_rows = session.execute(
            text(
                """
                SELECT
                    c.table_name,
                    c.column_name,
                    c.data_type,
                    c.is_nullable,
                    c.column_default,
                    c.ordinal_position
                FROM information_schema.columns c
                JOIN information_schema.tables t
                    ON t.table_schema = c.table_schema
                    AND t.table_name = c.table_name
                WHERE c.table_schema = :schema_name
                    AND t.table_type = 'BASE TABLE'
                ORDER BY c.table_name, c.ordinal_position
                """
            ),
            {"schema_name": schema_name},
        ).mappings().all()

        tables_by_name: dict[str, QuerySchemaTable] = {}
        for row in column_rows:
            table = tables_by_name.setdefault(
                row["table_name"],
                QuerySchemaTable(name=row["table_name"], columns=[], constraints=[]),
            )
            table.columns.append(
                QuerySchemaColumn(
                    name=row["column_name"],
                    data_type=row["data_type"],
                    nullable=row["is_nullable"] == "YES",
                    default=row["column_default"],
                )
            )

        if include_constraints:
            constraint_rows = session.execute(
                text(
                    """
                    SELECT
                        tc.table_name,
                        kcu.column_name,
                        ccu.table_schema AS foreign_table_schema,
                        ccu.table_name AS foreign_table_name,
                        ccu.column_name AS foreign_column_name
                    FROM information_schema.table_constraints tc
                    JOIN information_schema.key_column_usage kcu
                        ON tc.constraint_name = kcu.constraint_name
                        AND tc.table_schema = kcu.table_schema
                    JOIN information_schema.constraint_column_usage ccu
                        ON ccu.constraint_name = tc.constraint_name
                        AND ccu.table_schema = tc.table_schema
                    WHERE tc.constraint_type = 'FOREIGN KEY'
                        AND tc.table_schema = :schema_name
                    ORDER BY tc.table_name, kcu.column_name
                    """
                ),
                {"schema_name": schema_name},
            ).mappings().all()

            for row in constraint_rows:
                table = tables_by_name.get(row["table_name"])
                if table is None:
                    continue
                table.constraints.append(
                    QuerySchemaConstraint(
                        column=row["column_name"],
                        foreign_table_schema=row["foreign_table_schema"],
                        foreign_table_name=row["foreign_table_name"],
                        foreign_column_name=row["foreign_column_name"],
                    )
                )

        tables = list(tables_by_name.values())
        return {
            "table_count": len(tables),
            "column_count": sum(len(table.columns) for table in tables),
            "tables": tables,
        }


def _normalize_schema_name(name: str) -> str:
    schema_name = name.strip()
    if not SAFE_SCHEMA_NAME.fullmatch(schema_name):
        raise QuerySchemaImportError(
            "Schema name must start with a lowercase letter and contain only lowercase letters, numbers and underscores."
        )
    return schema_name


def _decode_sql_file(filename: str, content: bytes) -> str:
    if not filename.lower().endswith(".sql"):
        raise QuerySchemaImportError("Only .sql files are accepted.")
    if not content:
        raise QuerySchemaImportError("The SQL file is empty.")
    if len(content) > MAX_SQL_FILE_BYTES:
        raise QuerySchemaImportError("The SQL file exceeds the 1 MB limit.")
    try:
        sql_text = content.decode("utf-8")
    except UnicodeDecodeError as error:
        raise QuerySchemaImportError("The SQL file must be UTF-8 encoded.") from error
    if not sql_text.strip():
        raise QuerySchemaImportError("The SQL file is empty.")
    return sql_text


def _validate_sql(schema_name: str, sql_text: str) -> list[str]:
    stripped_sql = _strip_comments_and_literals(sql_text)
    if DANGEROUS_SQL.search(stripped_sql):
        raise QuerySchemaImportError("The SQL file contains statements that are not allowed.")

    try:
        sqlglot.parse(sql_text, read="postgres")
    except Exception as error:
        raise QuerySchemaImportError(f"The SQL file is not valid PostgreSQL: {error}") from error

    statements = _split_sql_statements(sql_text)
    if not statements:
        raise QuerySchemaImportError("The SQL file is empty.")

    for statement in statements:
        _validate_statement(schema_name, statement)
    return statements


def _validate_statement(schema_name: str, statement: str) -> None:
    normalized = " ".join(_strip_comments_and_literals(statement).split())
    upper = normalized.upper()
    allowed = (
        upper.startswith("CREATE SCHEMA")
        or upper.startswith("CREATE TABLE")
        or upper.startswith("CREATE INDEX")
        or upper.startswith("CREATE UNIQUE INDEX")
        or upper.startswith("ALTER TABLE")
        or upper.startswith("INSERT INTO")
    )
    if not allowed:
        raise QuerySchemaImportError("Only CREATE SCHEMA/TABLE/INDEX, ALTER TABLE and INSERT statements are accepted.")

    if upper.startswith("CREATE SCHEMA"):
        if not re.match(rf'^CREATE\s+SCHEMA\s+(IF\s+NOT\s+EXISTS\s+)?"?{schema_name}"?$', normalized, re.IGNORECASE):
            raise QuerySchemaImportError("CREATE SCHEMA must target the schema name provided in the form.")
        return

    if upper.startswith("CREATE TABLE"):
        _require_schema_qualified(normalized, rf"CREATE\s+TABLE\s+(IF\s+NOT\s+EXISTS\s+)?", schema_name)
    elif upper.startswith("CREATE INDEX") or upper.startswith("CREATE UNIQUE INDEX"):
        if not re.search(rf"\bON\s+\"?{schema_name}\"?\.", normalized, re.IGNORECASE):
            raise QuerySchemaImportError("CREATE INDEX must target a table inside the new schema.")
    elif upper.startswith("ALTER TABLE"):
        _require_schema_qualified(normalized, r"ALTER\s+TABLE\s+(IF\s+EXISTS\s+)?", schema_name)
    elif upper.startswith("INSERT INTO"):
        _require_schema_qualified(normalized, r"INSERT\s+INTO\s+", schema_name)

    for referenced_schema in _referenced_schemas(normalized):
        if referenced_schema != schema_name:
            raise QuerySchemaImportError("SQL statements may only reference objects inside the new schema.")


def _require_schema_qualified(statement: str, prefix_pattern: str, schema_name: str) -> None:
    pattern = rf"^{prefix_pattern}\"?{schema_name}\"?\."
    if not re.search(pattern, statement, re.IGNORECASE):
        raise QuerySchemaImportError("SQL statements must use the schema name provided in the form.")


def _referenced_schemas(statement: str) -> set[str]:
    return {
        match.group("schema").strip('"')
        for match in re.finditer(
            r'(?P<schema>"?[a-z][a-z0-9_]{0,62}"?)\s*\.\s*"?[a-z][a-z0-9_]{0,62}"?',
            statement,
            re.IGNORECASE,
        )
    }


def _has_create_schema_statement(schema_name: str, statements: list[str]) -> bool:
    return any(
        re.match(
            rf'^\s*CREATE\s+SCHEMA\s+(IF\s+NOT\s+EXISTS\s+)?"?{schema_name}"?\s*$',
            _strip_comments_and_literals(statement),
            re.IGNORECASE,
        )
        for statement in statements
    )


def _split_sql_statements(sql_text: str) -> list[str]:
    statements: list[str] = []
    current: list[str] = []
    quote: str | None = None
    index = 0
    while index < len(sql_text):
        char = sql_text[index]
        next_char = sql_text[index + 1] if index + 1 < len(sql_text) else ""
        current.append(char)

        if quote is None and char == "-" and next_char == "-":
            index += 1
            current.append(next_char)
            while index + 1 < len(sql_text) and sql_text[index + 1] != "\n":
                index += 1
                current.append(sql_text[index])
        elif quote is None and char == "/" and next_char == "*":
            index += 1
            current.append(next_char)
            while index + 1 < len(sql_text):
                index += 1
                current.append(sql_text[index])
                if sql_text[index - 1] == "*" and sql_text[index] == "/":
                    break
        elif char in ("'", '"'):
            if quote is None:
                quote = char
            elif quote == char:
                if next_char == char:
                    index += 1
                    current.append(next_char)
                else:
                    quote = None
        elif char == ";" and quote is None:
            statement = "".join(current).strip().rstrip(";").strip()
            if statement:
                statements.append(statement)
            current = []

        index += 1

    trailing = "".join(current).strip()
    if trailing:
        statements.append(trailing)
    return statements


def _strip_comments_and_literals(sql_text: str) -> str:
    sql_text = re.sub(r"--.*?$", " ", sql_text, flags=re.MULTILINE)
    sql_text = re.sub(r"/\*.*?\*/", " ", sql_text, flags=re.DOTALL)
    sql_text = re.sub(r"'(?:''|[^'])*'", "''", sql_text)
    return sql_text


def _build_schema_context(schema_name: str, tables: list[QuerySchemaTable]) -> str:
    lines = [f"Schema: {schema_name}"]
    for table in tables:
        lines.append(f"\nTable: {schema_name}.{table.name}")
        lines.append("Columns:")
        for column in table.columns:
            nullable = "nullable" if column.nullable else "not null"
            lines.append(f"- {column.name} {column.data_type} {nullable}")
        if table.constraints:
            lines.append("Foreign keys:")
            for constraint in table.constraints:
                lines.append(
                    "- "
                    f"{constraint.column} references "
                    f"{constraint.foreign_table_schema}.{constraint.foreign_table_name}"
                    f"({constraint.foreign_column_name})"
                )
    return "\n".join(lines)
