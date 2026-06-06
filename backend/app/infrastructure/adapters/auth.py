from datetime import datetime, timedelta, timezone

import jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.core.settings import get_settings
from app.domain.errors import InvalidCredentialsError, UserAlreadyExistsError
from app.domain.entities.user import UserRole
from app.infrastructure.adapters.database.models.users import UserRecord
from app.infrastructure.api.schemas.auth import AuthTokenResponse, LoginRequest, SignupRequest


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthAdapter:

    def __init__(self, session_factory):
        self._session_factory = session_factory
        self._settings = get_settings()

    async def login(self, credentials: LoginRequest) -> AuthTokenResponse:
        with self._session_factory() as session:
            user_record = session.execute(
                select(UserRecord).where(UserRecord.email == credentials.email.lower())
            ).scalar_one_or_none()

            if user_record is None or not pwd_context.verify(credentials.password, user_record.password):
                raise InvalidCredentialsError("Invalid email or password.")

            return AuthTokenResponse(access_token=self._create_access_token(user_record.id))
    
    async def signup(self, user: SignupRequest) -> AuthTokenResponse:
        with self._session_factory() as session:
            existing_user = session.execute(
                select(UserRecord).where(UserRecord.email == user.email.lower())
            ).scalar_one_or_none()
            if existing_user is not None:
                raise UserAlreadyExistsError("A user with this email already exists.")

            user_record = UserRecord(
                username=user.username.strip(),
                email=user.email.lower(),
                password=pwd_context.hash(user.password),
                role=UserRole.User.value,
            )
            session.add(user_record)
            try:
                session.flush()
            except IntegrityError as error:
                raise UserAlreadyExistsError("A user with this email already exists.") from error

            return AuthTokenResponse(access_token=self._create_access_token(user_record.id))

    def _create_access_token(self, user_id: str) -> str:
        now = datetime.now(timezone.utc)
        user_id = str(user_id)
        payload = {
            "sub": user_id,
            "user_id": user_id,
            "iat": now,
            "exp": now + timedelta(minutes=self._settings.jwt_expiration_minutes),
        }
        if self._settings.jwt_audience is not None:
            payload["aud"] = self._settings.jwt_audience
        if self._settings.jwt_issuer is not None:
            payload["iss"] = self._settings.jwt_issuer

        return jwt.encode(
            payload,
            self._settings.jwt_secret_key,
            algorithm=self._settings.jwt_algorithm,
        )
