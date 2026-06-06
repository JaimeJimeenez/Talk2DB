from datetime import UTC, datetime

from app.application.rag.service import RagService
from app.domain.entities.query_schema import QuerySchema


class FakeSchemasPort:
    async def get_schema(self, schema_id: str):
        return QuerySchema(
            id=schema_id,
            name="logistica_demo",
            description="Schema demo de logística",
            business_rules="",
            context="",
            created_at=datetime.now(UTC),
            refreshed_at=datetime.now(UTC),
        )


class FakeSchemaLoader:
    async def load_database_schema(self, schema_name: str | None = None):
        return {
            "logistica_demo": {
                "envios": {
                    "description": None,
                    "columns": [
                        {"name": "id", "type": "text", "nullable": False},
                        {"name": "cliente_id", "type": "text", "nullable": False},
                        {"name": "estado", "type": "text", "nullable": False},
                        {"name": "coste_envio", "type": "numeric", "nullable": False},
                    ],
                    "constraints": [
                        {
                            "type": "FOREIGN KEY",
                            "column": "cliente_id",
                            "foreign_table_schema": "logistica_demo",
                            "foreign_table_name": "clientes",
                            "foreign_column_name": "id",
                        }
                    ],
                },
                "clientes": {
                    "description": None,
                    "columns": [
                        {"name": "id", "type": "text", "nullable": False},
                        {"name": "ciudad", "type": "text", "nullable": False},
                    ],
                    "constraints": [],
                },
            }
        }


class FakeSchemaContext:
    def __init__(self) -> None:
        self.retrieve_questions = []

    async def retrieve_relevant_schema(self, schema, question: str, *, guidance: str = ""):
        self.retrieve_questions.append(question)
        return schema

    def format_for_prompt(self, schema) -> str:
        return "Table logistica_demo.envios\nTable logistica_demo.clientes"


class FakeSqlGenerator:
    def __init__(self) -> None:
        self.rewrite_calls = []
        self.generate_calls = []

    async def rewrite_follow_up_question(self, question: str, conversation_context: str | None = None) -> str:
        self.rewrite_calls.append(
            {
                "question": question,
                "conversation_context": conversation_context,
            }
        )
        return "Devuelve la ciudad del envio no cancelado con mayor coste_envio."

    async def generate_sql(
        self,
        question: str,
        schema_text: str,
        conversation_context: str | None = None,
    ) -> str:
        self.generate_calls.append(
            {
                "question": question,
                "schema_text": schema_text,
                "conversation_context": conversation_context,
            }
        )
        return (
            "SELECT c.ciudad "
            "FROM logistica_demo.envios AS e "
            "JOIN logistica_demo.clientes AS c ON c.id = e.cliente_id "
            "WHERE e.estado <> 'cancelado' "
            "ORDER BY e.coste_envio DESC "
            "LIMIT 1"
        )

    async def repair_sql(self, **kwargs) -> str:
        raise AssertionError("repair_sql should not be called")


class FakeSqlExecutor:
    def __init__(self) -> None:
        self.sql = None

    async def execute(self, sql: str):
        self.sql = sql
        return ["ciudad"], [{"ciudad": "Valencia"}]


def test_default_answer_summarizes_numeric_result_by_label():
    answer = RagService._default_answer(
        ["mes", "ingresos"],
        [
            {"mes": "2026-01-01T00:00:00+00:00", "ingresos": 2910.0},
            {"mes": "2026-02-01T00:00:00+00:00", "ingresos": 1600.0},
            {"mes": "2026-03-01T00:00:00+00:00", "ingresos": 1400.0},
            {"mes": "2026-04-01T00:00:00+00:00", "ingresos": 2890.0},
        ],
    )

    assert answer.startswith("He calculado ingresos para 4 categorías.")
    assert "2026-01: 2,910" in answer
    assert answer.endswith("...")


def test_default_answer_summarizes_single_row_values():
    answer = RagService._default_answer(
        ["producto", "ingresos"],
        [{"producto": "Pro Analytics", "ingresos": 2800.0}],
    )

    assert answer == "He calculado ingresos para 1 categoría. Pro Analytics: 2,800."


def test_answer_uses_rewritten_follow_up_for_schema_retrieval_and_sql_generation():
    import asyncio

    schema_context = FakeSchemaContext()
    sql_generator = FakeSqlGenerator()
    sql_executor = FakeSqlExecutor()
    service = RagService(
        schemas=FakeSchemasPort(),
        schema_loader=FakeSchemaLoader(),
        schema_context=schema_context,
        sql_generator=sql_generator,
        sql_executor=sql_executor,
        model_name="test-model",
    )
    conversation_context = (
        "user: Haz una comparación entre el número de los envíos por ciudades.\n"
        "assistant_sql: SELECT c.ciudad, COUNT(e.id) AS numero_envios "
        "FROM logistica_demo.clientes AS c "
        "JOIN logistica_demo.envios AS e ON c.id = e.cliente_id "
        "GROUP BY c.ciudad\n"
        "user: Cual es el que tiene más coste de envío?\n"
        "assistant_sql: SELECT e.id, e.coste_envio "
        "FROM logistica_demo.envios AS e "
        "WHERE e.estado <> 'cancelado' "
        "ORDER BY e.coste_envio DESC LIMIT 1"
    )

    result = asyncio.run(
        service.answer(
            "Si pero quiero saber la ciudad",
            "schema-logistica",
            conversation_context=conversation_context,
        )
    )

    assert schema_context.retrieve_questions == [
        "Devuelve la ciudad del envio no cancelado con mayor coste_envio."
    ]
    assert sql_generator.generate_calls[-1]["question"] == (
        "Devuelve la ciudad del envio no cancelado con mayor coste_envio."
    )
    assert sql_generator.generate_calls[-1]["conversation_context"] == conversation_context
    assert "coste_envio" in result.sql
    assert "COUNT(e.id)" not in result.sql
    assert result.rows == [{"ciudad": "Valencia"}]
    assert result.trace is not None
    assert result.trace.used_context is True
