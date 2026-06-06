from app.application.rag.llm import clean_sql_output
from app.application.rag.llm import SqlGenerator


class CapturingLlm:
    def __init__(self) -> None:
        self.messages = []

    async def ainvoke(self, messages):
        self.messages = messages
        return type("Response", (), {"content": "SELECT 1"})()


def test_clean_sql_output_normalizes_mysql_identifier_quotes():
    sql = "SELECT `id`, `nombre` FROM ventas.clientes WHERE `activo` = TRUE;"

    assert clean_sql_output(sql) == 'SELECT "id", "nombre" FROM ventas.clientes WHERE "activo" = TRUE'


def test_generate_sql_includes_conversation_context():
    import asyncio

    llm = CapturingLlm()
    generator = SqlGenerator(llm)

    asyncio.run(
        generator.generate_sql(
            "Y por producto?",
            "Table ventas.pedidos",
            conversation_context="user: Ventas por mes\nassistant_sql: SELECT 1",
        )
    )

    prompt = llm.messages[1].content
    assert "Previous conversation messages, oldest first" in prompt
    assert "user: Ventas por mes" in prompt
    assert "assistant_sql: SELECT 1" in prompt
