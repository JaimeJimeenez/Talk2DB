from datetime import UTC, datetime, timedelta
from types import SimpleNamespace

import jwt
from dependency_injector import providers
from fastapi.testclient import TestClient

from app.core.settings import get_settings
from app.domain.entities.query_schema import QuerySchema, QuerySchemaColumn, QuerySchemaTable
from app.domain.errors import QuerySchemaImportError
from app.infrastructure.adapters.schemas import _normalize_schema_name, _validate_sql
from app.main import app

USER_ID = "00000000-0000-0000-0000-000000000101"


class FakeSchemasUseCase:
    def __init__(self):
        self.import_payload = None

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
                table_count=1,
                column_count=2,
            )
        ]

    async def get_schema(self, schema_id: str):
        return None

    async def get_schema_detail(self, schema_id: str):
        now = datetime.now(UTC)
        if schema_id != "schema-1":
            return None
        return QuerySchema(
            id="schema-1",
            name="ventas",
            description="Schema demo para ventas",
            business_rules="Solo clientes activos",
            context="internal context",
            created_at=now,
            refreshed_at=now,
            table_count=1,
            column_count=2,
            tables=[
                QuerySchemaTable(
                    name="clientes",
                    columns=[
                        QuerySchemaColumn(name="id", data_type="text", nullable=False),
                        QuerySchemaColumn(name="nombre", data_type="text", nullable=False),
                    ],
                    constraints=[],
                )
            ],
        )

    async def import_schema(self, **kwargs):
        self.import_payload = kwargs
        now = datetime.now(UTC)
        return QuerySchema(
            id="schema-2",
            name=kwargs["name"],
            description=kwargs["description"],
            business_rules=kwargs["business_rules"],
            context="Schema: demo",
            created_at=now,
            refreshed_at=now,
            table_count=1,
            column_count=1,
            tables=[
                QuerySchemaTable(
                    name="items",
                    columns=[QuerySchemaColumn(name="id", data_type="text", nullable=False)],
                    constraints=[],
                )
            ],
        )


class FakeDatabase:
    def __init__(self, role: str):
        self.role = role

    def session(self):
        role = self.role

        class FakeSession:
            def __enter__(self):
                return self

            def __exit__(self, *args):
                return False

            def get(self, model, user_id):
                return SimpleNamespace(role=role)

        return FakeSession()


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
    assert response.json()[0]["table_count"] == 1


def test_get_query_schema_detail_returns_tables():
    app.container.schemas_use_case.override(providers.Object(FakeSchemasUseCase()))

    try:
        response = TestClient(app).get(
            "/api/v1/query-schemas/schema-1",
            headers={"Authorization": f"Bearer {_token()}"},
        )
    finally:
        app.container.schemas_use_case.reset_override()

    assert response.status_code == 200
    assert response.json()["name"] == "ventas"
    assert response.json()["tables"][0]["name"] == "clientes"
    assert response.json()["tables"][0]["columns"][1]["name"] == "nombre"


def test_import_query_schema_requires_admin_user():
    app.container.schemas_use_case.override(providers.Object(FakeSchemasUseCase()))
    app.container.database.override(providers.Object(FakeDatabase("user")))

    try:
        response = TestClient(app).post(
            "/api/v1/query-schemas/import",
            headers={"Authorization": f"Bearer {_token()}"},
            data={"name": "demo", "description": "Demo", "business_rules": ""},
            files={"file": ("demo.sql", b"CREATE TABLE demo.items (id TEXT);", "text/sql")},
        )
    finally:
        app.container.schemas_use_case.reset_override()
        app.container.database.reset_override()

    assert response.status_code == 403


def test_import_query_schema_accepts_admin_upload():
    use_case = FakeSchemasUseCase()
    app.container.schemas_use_case.override(providers.Object(use_case))
    app.container.database.override(providers.Object(FakeDatabase("admin")))

    try:
        response = TestClient(app).post(
            "/api/v1/query-schemas/import",
            headers={"Authorization": f"Bearer {_token()}"},
            data={"name": "demo", "description": "Demo", "business_rules": "Only active rows"},
            files={"file": ("demo.sql", b"CREATE TABLE demo.items (id TEXT);", "text/sql")},
        )
    finally:
        app.container.schemas_use_case.reset_override()
        app.container.database.reset_override()

    assert response.status_code == 201
    assert response.json()["name"] == "demo"
    assert use_case.import_payload["filename"] == "demo.sql"


def test_list_query_schemas_requires_bearer_token():
    response = TestClient(app).get("/api/v1/query-schemas")

    assert response.status_code == 401


def test_schema_sql_validation_rejects_invalid_schema_name():
    try:
        _normalize_schema_name("Ventas")
    except QuerySchemaImportError as error:
        assert "lowercase" in str(error)
    else:
        raise AssertionError("Expected invalid schema name to be rejected.")


def test_schema_sql_validation_rejects_dangerous_statement():
    try:
        _validate_sql("demo", "DROP TABLE ventas.clientes;")
    except QuerySchemaImportError as error:
        assert "not allowed" in str(error)
    else:
        raise AssertionError("Expected dangerous SQL to be rejected.")


def test_schema_sql_validation_rejects_references_outside_new_schema():
    try:
        _validate_sql(
            "demo",
            "CREATE TABLE demo.items (id TEXT REFERENCES ventas.clientes(id));",
        )
    except QuerySchemaImportError as error:
        assert "only reference objects inside the new schema" in str(error)
    else:
        raise AssertionError("Expected external schema reference to be rejected.")


def test_schema_sql_validation_accepts_create_table_and_insert():
    statements = _validate_sql(
        "demo",
        """
        CREATE SCHEMA demo;
        CREATE TABLE demo.items (id TEXT PRIMARY KEY, name TEXT NOT NULL);
        INSERT INTO demo.items (id, name) VALUES ('i001', 'Item');
        """,
    )

    assert len(statements) == 3
