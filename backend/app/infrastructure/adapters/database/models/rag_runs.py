from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, JSON, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.settings import get_settings
from app.infrastructure.adapters.database.models.base import Base

settings = get_settings()


class RagRunRecord(Base):
    __tablename__ = "rag_runs"
    __table_args__ = {"schema": settings.database_schema}

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True)
    conversation_id: Mapped[str] = mapped_column(UUID(as_uuid=False), nullable=False, index=True)
    message_id: Mapped[str] = mapped_column(UUID(as_uuid=False), nullable=False, index=True)
    user_id: Mapped[str] = mapped_column(UUID(as_uuid=False), nullable=False, index=True)
    schema_id: Mapped[str] = mapped_column(UUID(as_uuid=False), nullable=False, index=True)
    schema_name: Mapped[str] = mapped_column(String(63), nullable=False, default="")
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    duration_ms: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    attempt_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    repair_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    sql_validated: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    sql_executed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    generated_sql: Mapped[str | None] = mapped_column(Text, nullable=True)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    row_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    truncated: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    used_context: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    context_message_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    model: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    retrieved_table_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    retrieved_tables: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
