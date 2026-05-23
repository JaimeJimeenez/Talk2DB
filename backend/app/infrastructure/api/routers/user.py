from dependency_injector import providers
from fastapi import APIRouter, HTTPException, status, Request

from app.infrastructure.api.schemas.user import LoginRequest, SignupRequest, SignupResponse
from app.domain.entities.user import User
from app.domain.errors import InvalidCredentialsError, UserAlreadyExistsError
from app.infrastructure.api.routers.dependencies import SessionDep
from app.infrastructure.api.security import create_access_token

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


def _to_auth_response(user: User, request: Request) -> SignupResponse:
    token = create_access_token(user.username, request.app.container.settings())
    return SignupResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        token=token,
    )

@router.post("/signup", response_model=SignupResponse, status_code=status.HTTP_201_CREATED)
async def signup(
    payload: SignupRequest,
    request: Request,
    session: SessionDep,
) -> SignupResponse:
    with request.app.container.session.override(providers.Object(session)):
        users = request.app.container.users_use_case()
        try:
            user = await users.create_user(payload.username, payload.email, payload.password)
        except UserAlreadyExistsError as error:
            raise HTTPException(status_code=409, detail="User already exists") from error

    return _to_auth_response(user, request)


@router.post("/login", response_model=SignupResponse)
async def login(
    payload: LoginRequest,
    request: Request,
    session: SessionDep,
) -> SignupResponse:
    with request.app.container.session.override(providers.Object(session)):
        users = request.app.container.users_use_case()
        try:
            user = await users.login(payload.email, payload.password)
        except InvalidCredentialsError as error:
            raise HTTPException(status_code=401, detail="Invalid credentials") from error

    return _to_auth_response(user, request)
