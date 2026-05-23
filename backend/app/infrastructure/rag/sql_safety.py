import re

try:
    import sqlglot
    from sqlglot import exp
except ImportError:  # pragma: no cover
    sqlglot = None
    exp = None

from app.infrastructure.rag.schema_context import SAFE_IDENTIFIER

FORBIDDEN = ("DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "TRUNCATE", "CREATE", "REPLACE", "MERGE")


def validate_select_sql(sql: str, allowed_schema: str) -> tuple[str | None, str | None]:
    sql = sql.strip()
    if not sql:
        return None, "No SQL was generated."
    if ";" in sql.rstrip(";"):
        return None, "Multiple SQL statements are not allowed."
    normalized = sql.upper()
    for keyword in FORBIDDEN:
        if re.search(rf"\b{keyword}\b", normalized):
            return None, f"Forbidden SQL keyword detected: {keyword}."

    if sqlglot is not None:
        try:
            parsed = sqlglot.parse_one(sql, read="postgres")
        except Exception as exc:
            return None, f"Invalid SQL syntax: {exc}"
        if not isinstance(parsed, exp.Select):
            return None, "Only SELECT statements are allowed."
        for table in parsed.find_all(exp.Table):
            if table.db and table.db != allowed_schema:
                return None, f"Schema '{table.db}' is not allowed."
            if not table.db:
                table.set("db", exp.Identifier(this=allowed_schema))
        return parsed.sql(dialect="postgres"), None

    if not normalized.startswith("SELECT"):
        return None, "Only SELECT statements are allowed."
    if not SAFE_IDENTIFIER.fullmatch(allowed_schema):
        return None, "Allowed schema is invalid."
    if re.search(r"\b(?:FROM|JOIN)\s+[A-Za-z_][A-Za-z0-9_]*\.", sql, re.IGNORECASE):
        foreign_schemas = re.findall(r"\b(?:FROM|JOIN)\s+([A-Za-z_][A-Za-z0-9_]*)\.", sql, re.IGNORECASE)
        if any(schema != allowed_schema for schema in foreign_schemas):
            return None, "A referenced schema is not allowed."
    qualified = re.sub(
        r"\b(FROM|JOIN)\s+([A-Za-z_][A-Za-z0-9_]*)(?!\s*\.)",
        rf"\1 {allowed_schema}.\2",
        sql,
        flags=re.IGNORECASE,
    )
    return qualified, None
