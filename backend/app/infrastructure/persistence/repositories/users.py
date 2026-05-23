from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.user import User, UserRole
from app.domain.errors import UserAlreadyExistsError
from app.domain.ports.users import UsersRepository
from app.infrastructure.persistence.orm.user_records import UserRecord


class SqlAlchemyUsersRepository(UsersRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_username(self, username: str) -> User | None:
        record = await self._session.scalar(
            select(UserRecord).where(UserRecord.username == username)
        )
        return self._to_domain(record) if record is not None else None

    async def get_by_email(self, email: str) -> User | None:
        record = await self._session.scalar(
            select(UserRecord).where(UserRecord.email == email)
        )
        return self._to_domain(record) if record is not None else None

    async def save(self, user: User) -> User:
        record = await self._session.get(UserRecord, user.id)
        if record is None:
            record = UserRecord(id=user.id)
            self._session.add(record)

        record.username = user.username
        record.email = user.email
        record.password = user.password
        record.created_at = user.created_at
        record.role = user.role.value

        try:
            await self._session.commit()
        except IntegrityError as error:
            await self._session.rollback()
            raise UserAlreadyExistsError(user.username) from error

        await self._session.refresh(record)
        return self._to_domain(record)

    @staticmethod
    def _to_domain(record: UserRecord) -> User:
        return User(
            id=record.id,
            username=record.username,
            email=record.email,
            password=record.password,
            created_at=record.created_at,
            role=UserRole(record.role),
        )
