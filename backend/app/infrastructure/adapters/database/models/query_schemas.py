from datetime import datetime

from sqlalchemy import DateTime, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.settings import get_settings
from app.infrastructure.adapters.database.models.base import Base

settings = get_settings()


class QuerySchemaRecord(Base):
    __tablename__ = "query_schemas"
    __table_args__ = {"schema": settings.database_schema}

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True)
    name: Mapped[str] = mapped_column(String(63), nullable=False, unique=True)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    business_rules: Mapped[str] = mapped_column(Text, nullable=False, default="")
    context: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    refreshed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
