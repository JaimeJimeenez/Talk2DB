from collections.abc import Awaitable, Callable
from functools import wraps
from typing import Any

import jwt
from dependency_injector import providers
from fastapi import HTTPException, Request, status

from app.core.settings import Settings
from app.domain.entities.user import User
from app.domain.ports.users import UsersRepository


class TokenAuthenticator:
    def __init__(self, users: UsersRepository, settings: Settings) -> None:
        self._users = users
        self._settings = settings

    async def authenticate(self, authorization: str | None) -> User:
        if authorization is None:
            self._raise_unauthorized("Missing bearer token")

        scheme, _, token = authorization.partition(" ")
        if scheme.lower() != "bearer" or not token:
            self._raise_unauthorized("Invalid bearer token")

        try:
            payload = jwt.decode(
                token,
                self._settings.jwt_secret_key,
                algorithms=[self._settings.jwt_algorithm],
            )
        except jwt.PyJWTError as error:
            raise self._unauthorized("Invalid bearer token") from error

        username = payload.get("sub")
        if not isinstance(username, str) or not username:
            self._raise_unauthorized("Invalid bearer token")

        user = await self._users.get_by_username(username)
        if user is None:
            self._raise_unauthorized("User not found")
        return user

    @staticmethod
    def _unauthorized(detail: str) -> HTTPException:
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )

    @classmethod
    def _raise_unauthorized(cls, detail: str) -> None:
        raise cls._unauthorized(detail)


def create_access_token(username: str, settings: Settings) -> str:
    return jwt.encode(
        {"sub": username},
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )


def requires_authentication(endpoint: Callable[..., Awaitable[Any]]) -> Callable[..., Awaitable[Any]]:
    @wraps(endpoint)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        request = _extract_request(args, kwargs)
        session = kwargs.get("session")
        if session is None:
            raise RuntimeError("Authenticated endpoints must receive a session dependency.")

        with request.app.container.session.override(providers.Object(session)):
            authenticator = request.app.container.token_authenticator()
            request.state.current_user = await authenticator.authenticate(
                request.headers.get("Authorization")
            )
            return await endpoint(*args, **kwargs)

    return wrapper


def _extract_request(args: tuple[Any, ...], kwargs: dict[str, Any]) -> Request:
    request = kwargs.get("request")
    if isinstance(request, Request):
        return request

    for arg in args:
        if isinstance(arg, Request):
            return arg

    raise RuntimeError("Authenticated endpoints must receive a request argument.")
