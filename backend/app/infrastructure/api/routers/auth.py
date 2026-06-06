from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, status

from app.application.use_cases.auth import AuthUseCase
from app.core.container import Container
from app.domain.errors import InvalidCredentialsError, UserAlreadyExistsError

from app.infrastructure.api.schemas.auth import AuthTokenResponse, LoginRequest, SignupRequest

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/signup", response_model=AuthTokenResponse, status_code=status.HTTP_201_CREATED)
@inject
async def signup(
    payload: SignupRequest,
    auth_use_case: AuthUseCase = Depends(Provide[Container.auth_use_case]),
) -> AuthTokenResponse:
    try:
        return await auth_use_case.signup(payload)
    except UserAlreadyExistsError as error:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(error)) from error


@router.post("/login", response_model=AuthTokenResponse, status_code=status.HTTP_200_OK)
@inject
async def login(
    payload: LoginRequest,
    auth_use_case: AuthUseCase = Depends(Provide[Container.auth_use_case]),
) -> AuthTokenResponse:
    try:
        return await auth_use_case.login(payload)
    except InvalidCredentialsError as error:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(error)) from error
