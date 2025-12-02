from app.database.db_helper import get_db_session
from app.utilis.auth import verify_password
from pydantic import BaseModel, Field, validator
from app.models.user import User

class LoginRequest(BaseModel):
    email: str = Field(..., min_length=2, max_length=50, description="The email of the user")
    password: str = Field(..., min_length=8, max_length=72, description="The password of the user (max 72 bytes)")

    @validator('email')
    def validate_email(cls, v) -> str:
        """ Validate email """
        with get_db_session() as session:
            if v is None or v == "":
                raise ValueError("Email is required")
            user = session.query(User).filter(User.email == v).first()
            if not user:
                raise ValueError("Email or Password are Incorrect")
        return v

    @validator('password')
    def validate_password(cls, v, values) -> str:
        """ Validate password """
        with get_db_session() as session:
            if 'email' not in values:
                raise ValueError("Email is required")
            user = session.query(User).filter(User.email == values['email']).first()
            if not user:
                raise ValueError("Email or Password are Incorrect")
            if not verify_password(v, user.hashed_password):  # Use 'v' instead of values['password']
                raise ValueError("Email or Password are Incorrect")
        return v
        
    class Config:
        extra = "forbid"
        json_schema_extra = {  # ✅ Changed from schema_extra
            "example": {
                "email": "john.doe@example.com",
                "password": "password123"
            }
        }