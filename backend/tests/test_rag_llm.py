from app.application.rag.llm import clean_sql_output
from app.application.rag.llm import SqlGenerator


class CapturingLlm:
    def __init__(self, response_content: str = "SELECT 1") -> None:
        self.messages = []
        self.response_content = response_content

    async def ainvoke(self, messages):
        self.messages = messages
        return type("Response", (), {"content": self.response_content})()


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


def test_rewrite_follow_up_question_uses_previous_exchange():
    import asyncio

    llm = CapturingLlm("Devuelve la ciudad del envío con mayor coste de envío.")
    generator = SqlGenerator(llm)

    rewritten = asyncio.run(
        generator.rewrite_follow_up_question(
            "Si pero quiero saber la ciudad",
            conversation_context=(
                "user: Cual es el que tiene más coste de envío?\n"
                "assistant_sql: SELECT e.id, e.coste_envio "
                "FROM logistica_demo.envios AS e "
                "ORDER BY e.coste_envio DESC LIMIT 1"
            ),
        )
    )

    prompt = llm.messages[1].content
    assert rewritten == "Devuelve la ciudad del envío con mayor coste de envío."
    assert "Previous conversation messages, oldest first" in prompt
    assert "Current user question" in prompt
    assert "Si pero quiero saber la ciudad" in prompt
    assert "coste_envio DESC" in prompt
    assert "immediately previous user/assistant exchange" in llm.messages[0].content
