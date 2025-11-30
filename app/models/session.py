from typing import Optional
from datetime import datetime
from uuid import UUID
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.sql import func
from app.database.base import Base

class Session(Base):
    __tablename__ = "sessions"

    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=None)
    user_id = Column(PostgresUUID(as_uuid=True), ForeignKey("users.id"), index=True, nullable=False)
    token = Column(String(255), index=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_used_at = Column(DateTime(timezone=True), nullable=True, index=True)
