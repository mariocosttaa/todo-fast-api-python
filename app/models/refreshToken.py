from typing import Optional
from datetime import datetime
from uuid import UUID
from sqlmodel import Field
from app.database.base import Base

class RefreshToken(Base, table=True):
    __tablename__ = "refresh_tokens"

    id: Optional[UUID] = Field(default=None, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    token: str = Field(max_length=500, index=True)
    expires_at: Optional[datetime] = Field(default=None, index=True)
    created_at: Optional[datetime] = Field(default=None, index=True)
    updated_at: Optional[datetime] = Field(default=None, index=True)