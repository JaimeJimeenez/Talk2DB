from abc import ABC, abstractmethod

from app.domain.entities.user import User


class UsersRepository(ABC):
    @abstractmethod
    async def get_by_username(self, username: str) -> User | None:
        raise NotImplementedError

    @abstractmethod
    async def get_by_email(self, email: str) -> User | None:
        raise NotImplementedError
    
    @abstractmethod
    async def save(self, user: User) -> User:
        raise NotImplementedError
