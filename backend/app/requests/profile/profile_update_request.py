from app.models.user import User
from pydantic import BaseModel, Field, field_validator
from app.utilis.validation_messages import required, min_length, max_length

class ProfileUpdateRequest(BaseModel):
    name: str = Field(..., description="User Name")
    surname: str = Field(..., description="User Surname")
    email: str = Field(..., description="User Email")

    @field_validator("name")
    def validate_name(cls, v: str) -> str:
        if v is None or v.strip() == "":
            raise ValueError(required("name"))
        if len(v) < 1:
            raise ValueError(min_length("name", 1))
        if len(v) > 50:
            raise ValueError(max_length("name", 50))
        return v

    @field_validator("surname")
    def validate_surname(cls, v: str) -> str:
        if v is None or v.strip() == "":
            raise ValueError(required("surname"))
        if len(v) < 1:
            raise ValueError(min_length("surname", 1))
        if len(v) > 50:
            raise ValueError(max_length("surname", 50))
        return v

    @field_validator("email")
    def validate_email(cls, v: str) -> str:
        if v is None or v.strip() == "":
            raise ValueError(required("email"))
        if len(v) < 1:
            raise ValueError(min_length("email", 1))
        if len(v) > 100:
            raise ValueError(max_length("email", 100))
        return v

    class Config:
        extra = "forbid"
        json_schema_extra = {
            "example": {
                "name": "John",
                "surname": "Doe",   
                "email": "john.doe@example.com"
            }
        }