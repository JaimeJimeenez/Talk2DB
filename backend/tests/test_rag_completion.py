from datetime import UTC, datetime, timedelta

import jwt
from dependency_injector import providers
from fastapi.testclient import TestClient

from app.application.rag.service import RagResult, RagTrace
from app.application.use_cases.conversations import ConversationsUseCase
from app.application.use_cases.rag import RagUseCase
from app.core.settings import get_settings
from app.domain.entities.conversation import Conversation
from app.domain.entities.message import Message, MessageRole
from app.domain.entities.query_schema import QuerySchema
from app.main import app


SCHEMA_ID = "00000000-0000-0000-0000-000000000001"
USER_ID = "00000000-0000-0000-0000-000000000101"


class FakeSchemasPort:
    async def get_schema(self, schema_id: str):
        return QuerySchema(
            id=schema_id,
            name="ventas",
            description="Schema demo para ventas",
            business_rules="",
            context="",
            created_at=datetime.now(UTC),
            refreshed_at=datetime.now(UTC),
        )

    async def get_schemas(self):
        return [await self.get_schema(SCHEMA_ID)]


class FakeConversationsPort:
    def __init__(self) -> None:
        self.saved = None
        self.items = {}

    async def save(self, conversation):
        self.saved = conversation
        self.items[conversation.id] = conversation
        return conversation

    async def get_conversation(self, conversation_id: str, user_id: str):
        conversation = self.items.get(conversation_id)
        if conversation is None or conversation.user_id != user_id:
            return None
        return conversation

    async def list_conversations(self, user_id: str):
        return [
            conversation
            for conversation in self.items.values()
            if conversation.user_id == user_id
        ]


class FakeRagService:
    def __init__(self) -> None:
        self.calls = []

    async def answer(self, question: str, schema_id: str, conversation_context: str | None = None):
        self.calls.append(
            {
                "question": question,
                "schema_id": schema_id,
                "conversation_context": conversation_context,
            }
        )
        return RagResult(
            answer="He encontrado 4 resultados.",
            sql="SELECT id, nombre FROM ventas.clientes WHERE activo = true LIMIT 100",
            columns=["id", "nombre"],
            rows=[{"id": "c001", "nombre": "Acme Retail"}],
            row_count=1,
            trace=RagTrace(
                status="success",
                started_at=datetime.now(UTC),
                completed_at=datetime.now(UTC),
                duration_ms=120,
                attempt_count=2,
                repair_count=1,
                sql_validated=True,
                sql_executed=True,
                row_count=1,
                truncated=False,
                used_context=bool(conversation_context),
                context_message_count=2 if conversation_context else 0,
                model="test-model",
                schema_name="ventas",
                retrieved_tables=["ventas.clientes"],
            ),
        )

    async def title_for(self, prompt: str):
        return "Clientes activos"


class FailingRagService(FakeRagService):
    async def answer(self, question: str, schema_id: str, conversation_context: str | None = None):
        raise RuntimeError("SQL execution failed")


class FakeMetricsUseCase:
    def __init__(self) -> None:
        self.runs = []

    async def save_run(self, run):
        self.runs.append(run)
        return run


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


def test_completion_uses_token_user_id_and_saves_messages():
    conversations_port = FakeConversationsPort()
    conversations_use_case = ConversationsUseCase(
        conversations_port=conversations_port,
        schemas_port=FakeSchemasPort(),
    )
    rag_use_case = RagUseCase(FakeRagService(), conversations_use_case)
    app.container.rag_use_case.override(providers.Object(rag_use_case))

    try:
        client = TestClient(app)
        response = client.post(
            "/api/v1/rag/completion",
            headers={"Authorization": f"Bearer {_token()}"},
            json={
                "schema_id": SCHEMA_ID,
                "prompt": "Muestra los clientes activos",
            },
        )
    finally:
        app.container.rag_use_case.reset_override()

    assert response.status_code == 200
    body = response.json()
    assert body["answer"] == "He encontrado 4 resultados."
    assert body["content"] == "He encontrado 4 resultados."
    assert body["role"] == "assistant"
    assert body["id"]
    assert body["timestamp"]
    assert body["conversation_title"] == "Muestra los clientes activos"
    assert body["conversation_id"]
    assert body["title"] == "Muestra los clientes activos"
    assert body["sql"] == "SELECT id, nombre FROM ventas.clientes WHERE activo = true LIMIT 100"
    assert body["artifact"]["rowCount"] == 1
    assert conversations_port.saved.user_id == USER_ID
    assert len(conversations_port.saved.messages) == 2
    assert conversations_port.saved.messages[0].content == "Muestra los clientes activos"
    assert conversations_port.saved.messages[1].sql is not None


def test_completion_records_rag_metrics_when_trace_is_available():
    conversations_port = FakeConversationsPort()
    metrics_use_case = FakeMetricsUseCase()
    conversations_use_case = ConversationsUseCase(
        conversations_port=conversations_port,
        schemas_port=FakeSchemasPort(),
    )
    rag_use_case = RagUseCase(FakeRagService(), conversations_use_case, metrics_use_case)
    app.container.rag_use_case.override(providers.Object(rag_use_case))

    try:
        client = TestClient(app)
        response = client.post(
            "/api/v1/rag/completion",
            headers={"Authorization": f"Bearer {_token()}"},
            json={
                "schema_id": SCHEMA_ID,
                "prompt": "Muestra los clientes activos",
            },
        )
    finally:
        app.container.rag_use_case.reset_override()

    assert response.status_code == 200
    assert len(metrics_use_case.runs) == 1
    run = metrics_use_case.runs[0]
    assert run.status == "success"
    assert run.user_id == USER_ID
    assert run.schema_id == SCHEMA_ID
    assert run.schema_name == "ventas"
    assert run.message_id == response.json()["id"]
    assert run.duration_ms == 120
    assert run.repair_count == 1
    assert run.row_count == 1
    assert run.retrieved_tables == ["ventas.clientes"]


def test_create_conversation_then_completion_uses_bearer_token_end_to_end():
    conversations_port = FakeConversationsPort()
    conversations_use_case = ConversationsUseCase(
        conversations_port=conversations_port,
        schemas_port=FakeSchemasPort(),
    )
    rag_use_case = RagUseCase(FakeRagService(), conversations_use_case)
    app.container.conversations_use_case.override(providers.Object(conversations_use_case))
    app.container.rag_use_case.override(providers.Object(rag_use_case))

    try:
        client = TestClient(app)
        headers = {"Authorization": f"Bearer {_token()}"}
        create_response = client.post(
            "/api/v1/conversations",
            headers=headers,
            json={"schema_id": SCHEMA_ID},
        )
        conversation_id = create_response.json()["id"]
        completion_response = client.post(
            "/api/v1/rag/completion",
            headers=headers,
            json={
                "conversation_id": conversation_id,
                "schema_id": SCHEMA_ID,
                "prompt": "Muestra los clientes activos",
            },
        )
    finally:
        app.container.conversations_use_case.reset_override()
        app.container.rag_use_case.reset_override()

    assert create_response.status_code == 201
    assert completion_response.status_code == 200
    assert completion_response.json()["conversation_id"] == conversation_id
    assert completion_response.json()["id"]
    assert completion_response.json()["content"] == "He encontrado 4 resultados."
    assert completion_response.json()["title"] == "Clientes activos"
    assert completion_response.json()["conversation_title"] == "Clientes activos"
    assert conversations_port.saved.user_id == USER_ID
    assert len(conversations_port.saved.messages) == 2
    assert conversations_port.saved.messages[0].role == "user"
    assert conversations_port.saved.messages[1].role == "assistant"
    assert conversations_port.saved.messages[0].timestamp < conversations_port.saved.messages[1].timestamp


def test_completion_passes_previous_messages_as_conversation_context():
    conversations_port = FakeConversationsPort()
    conversations_use_case = ConversationsUseCase(
        conversations_port=conversations_port,
        schemas_port=FakeSchemasPort(),
    )
    existing_conversation = Conversation(
        id="conversation-ctx",
        title="Ventas por mes",
        created_at=datetime.now(UTC),
        schema_id=SCHEMA_ID,
        user_id=USER_ID,
        messages=[
            Message(
                id="user-1",
                role=MessageRole.USER,
                content="Ventas por mes",
                timestamp=datetime.now(UTC),
            ),
            Message(
                id="assistant-1",
                role=MessageRole.ASSISTANT,
                content="He calculado ingresos por mes.",
                timestamp=datetime.now(UTC),
                sql="SELECT DATE_TRUNC('MONTH', fecha) AS mes FROM ventas.pedidos LIMIT 100",
            ),
        ],
    )
    conversations_port.items[existing_conversation.id] = existing_conversation
    rag_service = FakeRagService()
    rag_use_case = RagUseCase(rag_service, conversations_use_case)

    app.container.rag_use_case.override(providers.Object(rag_use_case))

    try:
        client = TestClient(app)
        response = client.post(
            "/api/v1/rag/completion",
            headers={"Authorization": f"Bearer {_token()}"},
            json={
                "conversation_id": existing_conversation.id,
                "schema_id": SCHEMA_ID,
                "prompt": "Y por producto?",
            },
        )
    finally:
        app.container.rag_use_case.reset_override()

    assert response.status_code == 200
    assert rag_service.calls[-1]["conversation_context"] is not None
    assert "user: Ventas por mes" in rag_service.calls[-1]["conversation_context"]
    assert "assistant: He calculado ingresos por mes." in rag_service.calls[-1]["conversation_context"]
    assert "assistant_sql: SELECT DATE_TRUNC" in rag_service.calls[-1]["conversation_context"]


def test_completion_requires_bearer_token():
    client = TestClient(app)

    response = client.post(
        "/api/v1/rag/completion",
        json={
            "schema_id": SCHEMA_ID,
            "prompt": "Muestra los clientes activos",
        },
    )

    assert response.status_code == 401


def test_completion_returns_assistant_error_message_when_rag_fails():
    conversations_port = FakeConversationsPort()
    conversations_use_case = ConversationsUseCase(
        conversations_port=conversations_port,
        schemas_port=FakeSchemasPort(),
    )
    rag_use_case = RagUseCase(FailingRagService(), conversations_use_case)
    app.container.rag_use_case.override(providers.Object(rag_use_case))

    try:
        client = TestClient(app)
        response = client.post(
            "/api/v1/rag/completion",
            headers={"Authorization": f"Bearer {_token()}"},
            json={
                "schema_id": SCHEMA_ID,
                "prompt": "Muestra los clientes activos",
            },
        )
    finally:
        app.container.rag_use_case.reset_override()

    assert response.status_code == 200
    body = response.json()
    assert body["role"] == "assistant"
    assert body["content"] == "No he podido completar la consulta con el SQL generado."
    assert body["error"] == "SQL execution failed"
    assert body["artifact"] is None
