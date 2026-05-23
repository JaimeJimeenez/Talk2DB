import jwt
from fastapi.testclient import TestClient

from app.core.settings import get_settings
from tests.conftest import TEST_EMAIL, TEST_PASSWORD, TEST_USERNAME


def test_signup_creates_user_and_returns_token(client: TestClient) -> None:
    response = client.post(
        "/api/v1/auth/signup",
        json={
            "username": "new_user",
            "email": "new@example.com",
            "password": "secret",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["id"]
    assert body["username"] == "new_user"
    assert body["email"] == "new@example.com"

    settings = get_settings()
    payload = jwt.decode(
        body["token"],
        settings.jwt_secret_key,
        algorithms=[settings.jwt_algorithm],
    )
    assert payload["sub"] == "new_user"


def test_login_returns_token_for_valid_credentials(client: TestClient) -> None:
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["username"] == TEST_USERNAME
    assert body["email"] == TEST_EMAIL

    settings = get_settings()
    payload = jwt.decode(
        body["token"],
        settings.jwt_secret_key,
        algorithms=[settings.jwt_algorithm],
    )
    assert payload["sub"] == TEST_USERNAME


def test_login_rejects_unknown_email(client: TestClient) -> None:
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "missing@example.com",
            "password": TEST_PASSWORD,
        },
    )

    assert response.status_code == 401


def test_login_rejects_wrong_password(client: TestClient) -> None:
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": TEST_EMAIL,
            "password": "wrong-password",
        },
    )

    assert response.status_code == 401


def test_signup_rejects_existing_username(client: TestClient) -> None:
    response = client.post(
        "/api/v1/auth/signup",
        json={
            "username": TEST_USERNAME,
            "email": "another@example.com",
            "password": "secret",
        },
    )

    assert response.status_code == 409


def test_signup_rejects_existing_email(client: TestClient) -> None:
    response = client.post(
        "/api/v1/auth/signup",
        json={
            "username": "another_user",
            "email": TEST_EMAIL,
            "password": "secret",
        },
    )

    assert response.status_code == 409


def test_signup_rejects_invalid_payload(client: TestClient) -> None:
    response = client.post(
        "/api/v1/auth/signup",
        json={
            "username": "",
            "email": "not-an-email",
            "password": "",
        },
    )

    assert response.status_code == 422
