from fastapi.testclient import TestClient
from tests.conftest import TEST_SCHEMA_ID, build_token


def test_create_list_get_and_send_message(client: TestClient, auth_headers: dict[str, str]) -> None:
    created = client.post("/api/v1/conversations", json={"schema_id": TEST_SCHEMA_ID}, headers=auth_headers)
    assert created.status_code == 201
    conversation_id = created.json()["id"]

    listed = client.get("/api/v1/conversations", headers=auth_headers)
    assert listed.status_code == 200
    assert [item["id"] for item in listed.json()] == [conversation_id]

    sent = client.post(
        f"/api/v1/conversations/{conversation_id}/messages",
        json={"content": "show me active users"},
        headers=auth_headers,
    )
    assert sent.status_code == 200
    assert sent.json()["role"] == "assistant"
    assert sent.json()["sql"] == f"SELECT * FROM {TEST_SCHEMA_ID}.example LIMIT 100"

    fetched = client.get(f"/api/v1/conversations/{conversation_id}", headers=auth_headers)
    assert fetched.status_code == 200
    assert len(fetched.json()["messages"]) == 2


def test_get_unknown_conversation_returns_404(client: TestClient, auth_headers: dict[str, str]) -> None:
    response = client.get("/api/v1/conversations/unknown", headers=auth_headers)

    assert response.status_code == 404


def test_conversations_require_bearer_token(client: TestClient) -> None:
    response = client.get("/api/v1/conversations")

    assert response.status_code == 401


def test_conversations_reject_invalid_bearer_token(client: TestClient) -> None:
    response = client.get("/api/v1/conversations", headers={"Authorization": "Bearer invalid"})

    assert response.status_code == 401


def test_conversations_reject_unknown_user_token(client: TestClient) -> None:
    response = client.get(
        "/api/v1/conversations",
        headers={"Authorization": f"Bearer {build_token('missing_user')}"},
    )

    assert response.status_code == 401


def test_user_cannot_access_other_users_conversations(
    client: TestClient,
    auth_headers: dict[str, str],
    other_auth_headers: dict[str, str],
) -> None:
    created = client.post(
        "/api/v1/conversations",
        json={"schema_id": TEST_SCHEMA_ID},
        headers=other_auth_headers,
    )
    assert created.status_code == 201
    conversation_id = created.json()["id"]

    listed = client.get("/api/v1/conversations", headers=auth_headers)
    fetched = client.get(f"/api/v1/conversations/{conversation_id}", headers=auth_headers)

    assert listed.status_code == 200
    assert listed.json() == []
    assert fetched.status_code == 404
