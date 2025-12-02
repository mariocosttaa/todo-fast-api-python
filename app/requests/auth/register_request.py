from pydantic import BaseModel, validator, Field
from sqlalchemy.orm import Session
from app.database.db_helper import get_db_session
from app.models.user import User

class RegisterRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=50, description="The name of the user")
    surname: str = Field(..., min_length=2, max_length=50, description="The surname of the user")
    email: str = Field(..., min_length=2, max_length=50, description="The email of the user")
    password: str = Field(..., min_length=8, max_length=72, description="The password of the user (max 72 bytes)")
    password_confirm: str = Field(..., min_length=8, max_length=72, description="The password confirmation of the user")

    @validator('email')
    def validate_email(cls, v) -> str:
        """Validate the email"""
        with get_db_session() as session:
            user = session.query(User).filter(User.email == v).first()
            if user:
                raise ValueError("Email already exists")
        return v

    @validator('password_confirm')
    def validate_password_confirm(cls, v, values) -> str:
        """Validate the password confirmation"""
        if 'password' in values and v != values['password']:
            raise ValueError("Passwords do not match")
        return v

    class Config:
        extra = "forbid"
        json_schema_extra = {  # ✅ Changed from schema_extra
            "example": {
                "name": "John",
                "surname": "Doe",   
                "email": "john.doe@example.com",
                "password": "password123",
                "password_confirm": "password123"
            }
        }