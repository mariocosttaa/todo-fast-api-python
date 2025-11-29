from typing import Optional
from datetime import datetime
from uuid import UUID
from sqlmodel import Field
from app.database.base import Base

class Todo(Base, table=True):
    __tablename__ = "todos"

    id: Optional[UUID] = Field(default=None, primary_key=True)
    order: int = Field(default=0)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    title: str = Field(max_length=255, index=True)
    description: Optional[str] = Field(default=None, max_length=500)
    is_completed: bool = Field(default=False, index=True)
    due_date: Optional[datetime] = Field(default=None, index=True)
    priority: int = Field(default=1, index=True)
    created_at: Optional[datetime] = Field(default=None, index=True)
    updated_at: Optional[datetime] = Field(default=None, index=True)
