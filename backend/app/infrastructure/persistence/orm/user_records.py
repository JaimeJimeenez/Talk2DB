from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.persistence.orm.base import Base


class UserRecord(Base):
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint("role IN ('user', 'admin')", name="ck_users_role"),
    )

    id: Mapped[str] = mapped_column(Uuid(as_uuid=False), primary_key=True)
    username: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    role: Mapped[str] = mapped_column(String(16), nullable=False)
