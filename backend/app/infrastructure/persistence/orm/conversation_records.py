from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.persistence.orm.base import Base

class ConversationRecord(Base):
    __tablename__ = "conversations"

    id: Mapped[str] = mapped_column(Uuid(as_uuid=False), primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    schema_id: Mapped[str] = mapped_column(Uuid(as_uuid=False), ForeignKey("query_schemas.id"), nullable=False, index=True)
    user_id: Mapped[str] = mapped_column(Uuid(as_uuid=False), ForeignKey("users.id"), nullable=False, index=True)

    messages: Mapped[list["MessageRecord"]] = relationship(
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="MessageRecord.timestamp, MessageRecord.id",
        lazy="selectin",
    )


class MessageRecord(Base):
    __tablename__ = "messages"

    id: Mapped[str] = mapped_column(Uuid(as_uuid=False), primary_key=True)
    conversation_id: Mapped[str] = mapped_column(
        Uuid(as_uuid=False),
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role: Mapped[str] = mapped_column(String(16), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    sql: Mapped[str | None] = mapped_column(Text, nullable=True)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)

    conversation: Mapped[ConversationRecord] = relationship(back_populates="messages")
