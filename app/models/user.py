
from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.sql import func
from app.database.base import Base

class User(Base):
    __tablename__ = "users" 

    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=None)
    name = Column(String(50), nullable=False)
    surname = Column(String(50), nullable=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())