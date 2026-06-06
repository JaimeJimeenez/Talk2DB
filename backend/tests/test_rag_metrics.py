from datetime import UTC, datetime, timedelta

import jwt
from dependency_injector import providers
from fastapi.testclient import TestClient

from app.core.settings import get_settings
from app.domain.entities.rag_metrics import (
    RagMetricBucket,
    RagMetricPoint,
    RagMetricsSummary,
    RagRun,
    RagSchemaMetric,
)
from app.main import app

USER_ID = "00000000-0000-0000-0000-000000000101"


class FakeRagMetricsUseCase:
    async def get_summary(self, **kwargs):
        return RagMetricsSummary(
            total_runs=3,
            successful_runs=2,
            failed_runs=1,
            success_rate=0.6667,
            average_duration_ms=250.5,
            average_repair_count=0.33,
            average_row_count=12,
            runs_by_day=[
                RagMetricPoint(label="2026-06-03", total=3, successful=2, failed=1),
            ],
            latency_by_day=[
                RagMetricPoint(label="2026-06-03", total=3, average_duration_ms=250.5),
            ],
            runs_by_schema=[
                RagSchemaMetric(schema_id="schema-1", schema_name="ventas", count=3),
            ],
            errors_by_type=[
                RagMetricBucket(label="Invalid SQL syntax", count=1),
            ],
            row_count_buckets=[
                RagMetricBucket(label="0", count=1),
                RagMetricBucket(label="1-10", count=2),
            ],
        )

    async def list_runs(self, **kwargs):
        now = datetime.now(UTC)
        return [
            RagRun(
                id="run-1",
                conversation_id="conversation-1",
                message_id="message-1",
                user_id=USER_ID,
                schema_id="schema-1",
                schema_name="ventas",
                prompt="Ventas por mes",
                status="error",
                created_at=now,
                started_at=now,
                completed_at=now,
                duration_ms=350,
                attempt_count=5,
                repair_count=4,
                sql_validated=False,
                sql_executed=False,
                generated_sql="SELECT * FROM ventas.pedidos",
                error="Invalid SQL syntax",
                row_count=0,
                truncated=False,
                used_context=True,
                context_message_count=2,
                model="test-model",
                retrieved_table_count=1,
                retrieved_tables=["ventas.pedidos"],
            )
        ]


def _token() -> str:
    settings = get_settings()
    now = datetime.now(UTC)
    return jwt.encode(
        {
            "sub": USER_ID,
            "user_id": USER_ID,
            "iat": now,
            "exp": now + timedelta(minutes=5),
        },
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )


def test_rag_metrics_summary_returns_global_metrics():
    app.container.rag_metrics_use_case.override(providers.Object(FakeRagMetricsUseCase()))

    try:
        response = TestClient(app).get(
            "/api/v1/rag/metrics/summary",
            headers={"Authorization": f"Bearer {_token()}"},
        )
    finally:
        app.container.rag_metrics_use_case.reset_override()

    assert response.status_code == 200
    body = response.json()
    assert body["total_runs"] == 3
    assert body["success_rate"] == 0.6667
    assert body["runs_by_schema"][0]["schema_name"] == "ventas"
    assert body["errors_by_type"][0]["label"] == "Invalid SQL syntax"


def test_rag_metrics_runs_returns_recent_failures():
    app.container.rag_metrics_use_case.override(providers.Object(FakeRagMetricsUseCase()))

    try:
        response = TestClient(app).get(
            "/api/v1/rag/metrics/runs?status=error&limit=10",
            headers={"Authorization": f"Bearer {_token()}"},
        )
    finally:
        app.container.rag_metrics_use_case.reset_override()

    assert response.status_code == 200
    body = response.json()
    assert body[0]["status"] == "error"
    assert body[0]["prompt"] == "Ventas por mes"
    assert body[0]["generated_sql"] == "SELECT * FROM ventas.pedidos"


def test_rag_metrics_requires_bearer_token():
    response = TestClient(app).get("/api/v1/rag/metrics/summary")

    assert response.status_code == 401
