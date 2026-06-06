from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

from app.application.rag.database import ReadonlySQLExecutor
from app.application.rag.service import RagResult
from app.application.rag.sql import SQLValidationError, validate_sql


class RagAnswerer(Protocol):
    async def answer(self, question: str, schema_id: str) -> RagResult:
        ...


@dataclass(frozen=True)
class SqlEvaluationCase:
    id: str
    schema_id: str
    prompt: str
    expected_sql: str


@dataclass(frozen=True)
class SqlEvaluationResult:
    case_id: str
    prompt: str
    passed: bool
    generated_sql: str | None
    expected_sql: str
    structural_match: bool
    result_match: bool
    expected_rows: list[list[Any]]
    generated_rows: list[list[Any]]
    error: str | None = None


@dataclass(frozen=True)
class SqlEvaluationSummary:
    total: int
    passed: int
    failed: int
    results: list[SqlEvaluationResult]

    @property
    def success(self) -> bool:
        return self.failed == 0


def load_sql_evaluation_cases(path: str | Path) -> list[SqlEvaluationCase]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return [
        SqlEvaluationCase(
            id=item["id"],
            schema_id=item["schema_id"],
            prompt=item["prompt"],
            expected_sql=item["expected_sql"],
        )
        for item in data["cases"]
    ]


async def evaluate_sql_generation(
    *,
    cases: list[SqlEvaluationCase],
    rag_service: RagAnswerer,
    sql_executor: ReadonlySQLExecutor,
) -> SqlEvaluationSummary:
    results = [
        await evaluate_sql_case(
            case=case,
            rag_service=rag_service,
            sql_executor=sql_executor,
        )
        for case in cases
    ]
    passed = sum(result.passed for result in results)
    return SqlEvaluationSummary(
        total=len(results),
        passed=passed,
        failed=len(results) - passed,
        results=results,
    )


async def evaluate_sql_case(
    *,
    case: SqlEvaluationCase,
    rag_service: RagAnswerer,
    sql_executor: ReadonlySQLExecutor,
) -> SqlEvaluationResult:
    try:
        expected_sql = validate_sql(case.expected_sql)
        expected_columns, expected_rows = await sql_executor.execute(expected_sql)
    except Exception as exc:
        return SqlEvaluationResult(
            case_id=case.id,
            prompt=case.prompt,
            passed=False,
            generated_sql=None,
            expected_sql=case.expected_sql,
            structural_match=False,
            result_match=False,
            expected_rows=[],
            generated_rows=[],
            error=f"Expected SQL is invalid or failed to execute: {exc}",
        )

    try:
        rag_result = await rag_service.answer(case.prompt, case.schema_id)
        if rag_result.error:
            raise SQLValidationError(rag_result.error)
        if rag_result.sql is None:
            raise SQLValidationError("The RAG service did not return SQL.")
        generated_sql = validate_sql(rag_result.sql)
    except Exception as exc:
        return SqlEvaluationResult(
            case_id=case.id,
            prompt=case.prompt,
            passed=False,
            generated_sql=None,
            expected_sql=expected_sql,
            structural_match=False,
            result_match=False,
            expected_rows=_row_values(expected_columns, expected_rows),
            generated_rows=[],
            error=f"Generated SQL is invalid or failed to generate: {exc}",
        )

    generated_columns, generated_rows = await sql_executor.execute(generated_sql)
    structural_match = generated_sql == expected_sql
    expected_values = _row_values(expected_columns, expected_rows)
    generated_values = _row_values(generated_columns, generated_rows)
    result_match = _sorted_rows(expected_values) == _sorted_rows(generated_values)

    return SqlEvaluationResult(
        case_id=case.id,
        prompt=case.prompt,
        passed=result_match,
        generated_sql=generated_sql,
        expected_sql=expected_sql,
        structural_match=structural_match,
        result_match=result_match,
        expected_rows=expected_values,
        generated_rows=generated_values,
        error=None if result_match else "Generated SQL returned different results.",
    )


def sql_evaluation_summary_to_dict(summary: SqlEvaluationSummary) -> dict[str, Any]:
    return {
        "total": summary.total,
        "passed": summary.passed,
        "failed": summary.failed,
        "success": summary.success,
        "results": [
            {
                "case_id": result.case_id,
                "prompt": result.prompt,
                "passed": result.passed,
                "generated_sql": result.generated_sql,
                "expected_sql": result.expected_sql,
                "structural_match": result.structural_match,
                "result_match": result.result_match,
                "expected_rows": result.expected_rows,
                "generated_rows": result.generated_rows,
                "error": result.error,
            }
            for result in summary.results
        ],
    }


def _row_values(columns: list[str], rows: list[dict[str, Any]]) -> list[list[Any]]:
    return [[row.get(column) for column in columns] for row in rows]


def _sorted_rows(rows: list[list[Any]]) -> list[list[Any]]:
    return sorted(rows, key=lambda row: json.dumps(row, sort_keys=True, default=str))
