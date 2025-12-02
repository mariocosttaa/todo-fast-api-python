from app.utilis.auth import verify_password
from app.utilis.auth import get_password_hash
from app.models.user import User
from app.utilis.auth import get_current_user
from pydantic import BaseModel, Field, validator

class ProfilePasswordUpdateRequest(BaseModel):
    old_password: str = Field(..., min_length=8, max_length=72, description="Old Password")
    password:  str = Field(..., min_length=8, max_length=72, description="New Password")
    password_confirm: str = Field(..., min_length=8, max_length=72, description="Confirm New Password")

    @validator('password_confirm')
    def password_match(cls, v, values) -> bool:
        if 'password' in values and v != values['password']:
            raise ValueError('passwords do not match')
        return True
    
    class Config:
        extra = "forbid"
        json_schema_extra = {
            "example": {
                "old_password": "12345678",
                "password": "12345678910",
                "password_confirm": "12345678910",   
            }
        }
