from typing import Optional
from datetime import datetime
from uuid import UUID
from sqlmodel import Field
from app.database.base import Base

class User(Base, table=True):
    __tablename__ = "users" 

    id: Optional[UUID] = Field(default=None, primary_key=True)
    name: str = Field(max_length=50)
    surname: Optional[str] = Field(default=None, max_length=50)
    email: str = Field(unique=True, index=True)
    hashed_password: str = Field(max_length=255)
    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)
