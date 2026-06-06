import asyncio

from app.application.rag.evaluation import (
    SqlEvaluationCase,
    SqlEvaluationSummary,
    evaluate_sql_case,
    load_sql_evaluation_cases,
    sql_evaluation_summary_to_dict,
)
from app.application.rag.service import RagResult


class FakeRagService:
    def __init__(self, sql: str) -> None:
        self._sql = sql

    async def answer(self, question: str, schema_id: str) -> RagResult:
        return RagResult(
            answer="He encontrado 1 resultado.",
            sql=self._sql,
            columns=[],
            rows=[],
            row_count=1,
        )


class FakeExecutor:
    async def execute(self, sql: str):
        if "activo = TRUE" in sql:
            return ["id"], [{"id": "c001"}]
        return ["id"], [{"id": "c999"}]


def test_sql_evaluation_passes_when_generated_sql_returns_expected_rows():
    case = SqlEvaluationCase(
        id="clientes_activos",
        schema_id="schema-id",
        prompt="Clientes activos",
        expected_sql="SELECT id FROM ventas.clientes WHERE activo = TRUE",
    )

    result = asyncio.run(
        evaluate_sql_case(
            case=case,
            rag_service=FakeRagService("SELECT id FROM ventas.clientes WHERE activo = TRUE"),
            sql_executor=FakeExecutor(),
        )
    )

    assert result.passed is True
    assert result.result_match is True
    assert result.structural_match is True
    assert result.error is None


def test_sql_evaluation_fails_when_generated_sql_returns_different_rows():
    case = SqlEvaluationCase(
        id="clientes_activos",
        schema_id="schema-id",
        prompt="Clientes activos",
        expected_sql="SELECT id FROM ventas.clientes WHERE activo = TRUE",
    )

    result = asyncio.run(
        evaluate_sql_case(
            case=case,
            rag_service=FakeRagService("SELECT id FROM ventas.clientes WHERE activo = FALSE"),
            sql_executor=FakeExecutor(),
        )
    )

    assert result.passed is False
    assert result.result_match is False
    assert result.error == "Generated SQL returned different results."


def test_load_sql_evaluation_cases(tmp_path):
    path = tmp_path / "cases.json"
    path.write_text(
        """
        {
          "cases": [
            {
              "id": "case-1",
              "schema_id": "schema-id",
              "prompt": "Pregunta",
              "expected_sql": "SELECT 1"
            }
          ]
        }
        """,
        encoding="utf-8",
    )

    cases = load_sql_evaluation_cases(path)

    assert cases == [
        SqlEvaluationCase(
            id="case-1",
            schema_id="schema-id",
            prompt="Pregunta",
            expected_sql="SELECT 1",
        )
    ]


def test_sql_evaluation_summary_to_dict():
    summary = sql_evaluation_summary_to_dict(
        SqlEvaluationSummary(
            total=0,
            passed=0,
            failed=0,
            results=[],
        )
    )

    assert summary == {
        "total": 0,
        "passed": 0,
        "failed": 0,
        "success": True,
        "results": [],
    }
