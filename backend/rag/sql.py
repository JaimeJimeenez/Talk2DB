import re
import logging

import psycopg
from psycopg import Error as PsycopgError

import sqlglot
from sqlglot.errors import ParseError

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from models.graph import DbGraphState
from constants.rag import AGENT_PROMPT
from constants.sql import DATABASE_URL, LLM_MODEL, LLM_API_KEY, LLM_BASE_URL

logger = logging.getLogger('uvicorn')

class SqlGenerationError(ValueError):
    pass

model = ChatOpenAI(
    model=LLM_MODEL,
    base_url=LLM_BASE_URL,
    api_key=LLM_API_KEY,
    temperature=0,
    max_tokens=128,
)

def _extract_sql(text: str) -> str:
    fenced_sql = re.search(r"```(?:sql)?\s*(.*?)```", text, re.IGNORECASE | re.DOTALL)
    if fenced_sql:
        text = fenced_sql.group(1)

    select_statement = re.search(r"\bselect\b.*?(?:;|$)", text, re.IGNORECASE | re.DOTALL)
    if select_statement:
        text = select_statement.group(0)
    else:
        raise SqlGenerationError("El modelo no devolvio una consulta SELECT.")

    return text.strip().rstrip(";") + ";"

def generate_sql(state: DbGraphState) -> DbGraphState:
    logger.info('Generating sql for the petition')
    prompt: str = AGENT_PROMPT.format(
        schema=state["schema"],
        question=state["question"],
    )

    response = model.invoke([
        SystemMessage(content="You generate PostgreSQL SELECT queries only."),
        HumanMessage(content=prompt),
    ])
    logger.info(f'Response of the model: {response.content}')
    return { "sql": _extract_sql(response.content) }

def validate_sql(state: DbGraphState) -> DbGraphState:
    logger.info('Now we need to validate the sql in case the model type something wrong...')
    sql = state["sql"]

    try:
        parsed = sqlglot.parse_one(sql, read="postgres")
    except ParseError as exc:
        raise SqlGenerationError("El SQL generado no se pudo parsear.") from exc

    if parsed.key.upper() != "SELECT":
        raise SqlGenerationError("Solo se permiten consultas de lectura SELECT.")
    
    forbidden = [ "INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "TRUNCATE" ]
    if any(word in sql.upper() for word in forbidden):
        raise SqlGenerationError("La consulta solicitada contiene operaciones no permitidas.")
    
    logger.info('All good!')
    return {}

def execute_sql(state: DbGraphState) -> DbGraphState:
    logger.info('Executing sql...')
    with psycopg.connect(DATABASE_URL) as conn:
        with conn.cursor(row_factory=psycopg.rows.dict_row) as cur:
            try:
                cur.execute(state["sql"])
            except PsycopgError as exc:
                raise SqlGenerationError(f"El SQL generado no se pudo ejecutar: {exc}") from exc
            rows = cur.fetchall()

    logger.info(f'Sql results: {rows}')
    return {"rows": rows, "command": state["sql"] }

def write_answer(state: DbGraphState) -> DbGraphState:
    rows = state["rows"]
    if not rows:
        return {"answer": "La consulta se ejecuto correctamente, pero no devolvio resultados."}

    formatted_rows = []
    for row in rows[:10]:
        formatted_rows.append(
            ", ".join(f"{key}: {value}" for key, value in row.items())
        )

    answer = "Resultados:\n" + "\n".join(f"- {row}" for row in formatted_rows)
    if len(rows) > 10:
        answer += f"\n... y {len(rows) - 10} resultados mas."

    return { "answer": answer, "command": state["sql"] }
