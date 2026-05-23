import logging
from datetime import datetime, UTC
from uuid import uuid4

from app.domain.entities.user import User, UserRole
from app.domain.errors import InvalidCredentialsError, UserAlreadyExistsError
from app.domain.ports.users import UsersRepository
from app.infrastructure.security.passwords import hash_password, verify_password

logger = logging.getLogger(__name__)

class Users:
    def __init__(self, repository: UsersRepository) -> None:
        self._repository = repository

    async def create_user(self, username: str, email: str, password: str) -> User:
        logging.info("Creating user with username '%s' and email '%s'", username, email)
        if await self._repository.get_by_username(username) is not None:
            logging.warning("User with username '%s' already exists", username)
            raise UserAlreadyExistsError(username)
        if await self._repository.get_by_email(email) is not None:
            logging.warning("User with email '%s' already exists", email)
            raise UserAlreadyExistsError(email)

        user = User(
            id=str(uuid4()),
            username=username,
            email=email,
            password=hash_password(password),
            created_at=datetime.now(UTC),
            role=UserRole.User,
        )
        return await self._repository.save(user)

    async def login(self, email: str, password: str) -> User:
        user = await self._repository.get_by_email(email)
        if user is None or not verify_password(password, user.password):
            raise InvalidCredentialsError(email)
        return user
