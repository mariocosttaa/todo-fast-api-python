from pydantic import BaseModel, field_validator, Field  
from app.database.db_helper import get_db_session
from app.models.user import User
from pydantic import ValidationInfo
from app.utilis.validation_messages import required, min_length, max_length

class RegisterRequest(BaseModel):
    name: str = Field(..., name="name", description="The name of the user")
    surname: str = Field(..., name="surname", description="The surname of the user")
    email: str = Field(..., name="email", description="The email of the user")
    password: str = Field(..., name="password", description="The password of the user (max 72 bytes)")
    password_confirm: str = Field(..., name="password_confirm", description="The password confirmation of the user")

    @field_validator('name')
    def validate_name(cls, v: str) -> str:
        if v is None or v.strip() == "":
            raise ValueError(required("name"))
        if len(v) < 2:
            raise ValueError(min_length("name", 2))
        if len(v) > 50:
            raise ValueError(max_length("name", 50))
        return v

    @field_validator('surname')
    def validate_surname(cls, v: str) -> str:
        if v is None or v.strip() == "":
            raise ValueError(required("surname"))
        if len(v) < 2:
            raise ValueError(min_length("surname", 2))
        if len(v) > 50:
            raise ValueError(max_length("surname", 50))
        return v

    @field_validator('email')
    def validate_email(cls, v: str) -> str:
        """Validate the email"""
        if v is None or v.strip() == "":
            raise ValueError(required("email"))
        if len(v) < 2:
            raise ValueError(min_length("email", 2))
        if len(v) > 50:
            raise ValueError(max_length("email", 50))
        with get_db_session() as session:
            user = session.query(User).filter(User.email == v).first()
            if user:
                raise ValueError("email already exists")
        return v

    @field_validator('password')
    def validate_password(cls, v: str) -> str:
        if v is None or v.strip() == "":
            raise ValueError(required("password"))
        if len(v) < 8:
            raise ValueError(min_length("password", 8))
        if len(v) > 72:
            raise ValueError(max_length("password", 72))
        return v

    @field_validator('password_confirm')
    def validate_password_confirm(cls, v: str, info: ValidationInfo) -> str:
        """Validate the password confirmation"""
        if v is None or v.strip() == "":
            raise ValueError(required("password_confirm", label="Password confirmation"))
        if len(v) < 8:
            raise ValueError(min_length("password_confirm", 8, label="Password confirmation"))
        if len(v) > 72:
            raise ValueError(max_length("password_confirm", 72, label="Password confirmation"))
        if 'password' in info.data and v != info.data['password']:
            raise ValueError("passwords do not match")
        return v


    class Config:
        extra = "forbid"
        json_schema_extra = {  
            "example": {
                "name": "John",
                "surname": "Doe",   
                "email": "john.doe@example.com",
                "password": "password123",
                "password_confirm": "password123"
            }
        }