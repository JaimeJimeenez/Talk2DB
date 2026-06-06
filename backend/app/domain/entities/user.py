from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class UserRole(StrEnum):
    User = "user"
    Admin = "admin"


@dataclass(slots=True)
class User:
    id: str
    username: str
    email: str
    password: str
    created_at: datetime
    role: UserRole
