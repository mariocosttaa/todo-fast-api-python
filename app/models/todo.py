
from sqlalchemy import Column, Enum, String, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.sql import func
from app.database.base import Base

class Todo(Base):
    __tablename__ = "todos"

    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=None)
    order = Column(Integer, default=0)
    user_id = Column(PostgresUUID(as_uuid=True), ForeignKey("users.id"), index=True, nullable=False)
    title = Column(String(255), index=True, nullable=False)
    description = Column(String(500), nullable=True)
    is_completed = Column(Boolean, default=False, index=True)
    due_date = Column(DateTime(timezone=True), nullable=True, index=True)
    priority =Column(Enum("low", "medium", "high", name="todo_priority"), default="low", index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())