from app.database.db_helper import get_db_session
from app.utilis.auth import verify_password
from pydantic import BaseModel, Field, field_validator, ValidationInfo
from app.models.user import User
from app.utilis.validation_messages import required, min_length, max_length

class LoginRequest(BaseModel):
    email: str = Field(..., description="The email of the user")
    password: str = Field(..., description="The password of the user (max 72 bytes)")

    @field_validator('email')
    def validate_email(cls, v) -> str:
        """ Validate email """
        if v is None or v.strip() == "":
            raise ValueError(required("email"))
        if len(v) < 2:
            raise ValueError(min_length("email", 2))
        if len(v) > 50:
            raise ValueError(max_length("email", 50))
        with get_db_session() as session:
            user = session.query(User).filter(User.email == v).first()
            if not user:
                raise ValueError("email or password are incorrect")
        return v

    @field_validator('password')
    def validate_password(cls, v, info: ValidationInfo) -> str:
        """ Validate password """
        if v is None or v.strip() == "":
            raise ValueError(required("password"))
        if len(v) < 8:
            raise ValueError(min_length("password", 8))
        if len(v) > 72:
            raise ValueError(max_length("password", 72))
        with get_db_session() as session:
            if 'email' not in info.data:
                raise ValueError(required("email"))
            user = session.query(User).filter(User.email == info.data['email']).first()
            if not user:
                raise ValueError("email or password are incorrect")
            if not verify_password(v, user.hashed_password):  # Use 'v' instead of values['password']
                raise ValueError("email or password are incorrect")
        return v
        
    class Config:
        extra = "forbid"
        json_schema_extra = { 
            "example": {
                "email": "john.doe@example.com",
                "password": "password123"
            }
        }