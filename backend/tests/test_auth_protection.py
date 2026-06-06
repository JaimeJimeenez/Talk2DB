from fastapi.testclient import TestClient

from app.main import app


def test_protected_endpoints_require_bearer_token():
    client = TestClient(app)

    protected_requests = [
        ("get", "/api/v1/query-schemas", None),
        ("get", "/api/v1/conversations", None),
        ("post", "/api/v1/conversations", {"schema_id": "schema-1"}),
        ("get", "/api/v1/conversations/conversation-1", None),
        (
            "post",
            "/api/v1/rag/completion",
            {
                "conversation_id": "conversation-1",
                "schema_id": "schema-1",
                "prompt": "show users",
            },
        ),
    ]

    for method, url, json_body in protected_requests:
        if json_body is None:
            response = getattr(client, method)(url)
        else:
            response = getattr(client, method)(url, json=json_body)

        assert response.status_code == 401, url


def test_auth_endpoints_do_not_require_bearer_token():
    client = TestClient(app)

    login_response = client.post("/api/v1/auth/login", json={})
    signup_response = client.post("/api/v1/auth/signup", json={})

    assert login_response.status_code != 401
    assert signup_response.status_code != 401
