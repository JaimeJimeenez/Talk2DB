from datetime import datetime

from sqlalchemy import DateTime, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.persistence.orm.base import Base


class QuerySchemaRecord(Base):
    __tablename__ = "query_schemas"

    id: Mapped[str] = mapped_column(Uuid(as_uuid=False), primary_key=True)
    name: Mapped[str] = mapped_column(String(63), nullable=False, unique=True)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    business_rules: Mapped[str] = mapped_column(Text, nullable=False, default="")
    context: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    refreshed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
