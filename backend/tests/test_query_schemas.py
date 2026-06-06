from datetime import UTC, datetime, timedelta

import jwt
from dependency_injector import providers
from fastapi.testclient import TestClient

from app.core.settings import get_settings
from app.domain.entities.query_schema import QuerySchema
from app.main import app

USER_ID = "00000000-0000-0000-0000-000000000101"


class FakeSchemasUseCase:
    async def get_schemas(self):
        now = datetime.now(UTC)
        return [
            QuerySchema(
                id="schema-1",
                name="ventas",
                description="Schema demo para ventas",
                business_rules="Solo clientes activos",
                context="internal context",
                created_at=now,
                refreshed_at=now,
            )
        ]

    async def get_schema(self, schema_id: str):
        return None


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


def test_list_query_schemas_returns_available_schemas():
    app.container.schemas_use_case.override(providers.Object(FakeSchemasUseCase()))

    try:
        response = TestClient(app).get(
            "/api/v1/query-schemas",
            headers={"Authorization": f"Bearer {_token()}"},
        )
    finally:
        app.container.schemas_use_case.reset_override()

    assert response.status_code == 200
    assert response.json()[0]["id"] == "schema-1"
    assert response.json()[0]["name"] == "ventas"
    assert response.json()[0]["description"] == "Schema demo para ventas"
    assert response.json()[0]["business_rules"] == "Solo clientes activos"


def test_list_query_schemas_requires_bearer_token():
    response = TestClient(app).get("/api/v1/query-schemas")

    assert response.status_code == 401
