from app.models.user import User
from pydantic import BaseModel, Field, validator

class ProfileUpdateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=50, description="User Name")
    surname: str = Field(..., min_length=1, max_length=50, description="User Surname")
    email: str = Field(..., min_length=1, max_length=100, description="User Email")

    class Config:
        extra = "forbid"
        json_schema_extra = {
            "example": {
                "name": "John",
                "surname": "Doe",   
                "email": "john.doe@example.com"
            }
        }