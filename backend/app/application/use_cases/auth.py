from app.domain.ports.auth import AuthPort

from app.infrastructure.adapters.auth import AuthAdapter
from app.infrastructure.api.schemas.auth import LoginRequest, SignupRequest, AuthTokenResponse

class AuthUseCase(AuthPort):

    def __init__(self, auth_adapter: AuthAdapter):
        self._auth_adapter = auth_adapter

    async def login(self, credentials: LoginRequest) -> AuthTokenResponse:
        return await self._auth_adapter.login(credentials)
    
    async def signup(self, user: SignupRequest) -> AuthTokenResponse:
        return await self._auth_adapter.signup(user)
