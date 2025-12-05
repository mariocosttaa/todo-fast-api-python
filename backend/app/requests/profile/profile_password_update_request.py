from app.utilis.auth import verify_password
from app.utilis.auth import get_password_hash
from app.models.user import User
from app.utilis.auth import get_current_user
from pydantic import BaseModel, Field, field_validator, ValidationInfo  
from app.utilis.validation_messages import required, min_length, max_length

class ProfilePasswordUpdateRequest(BaseModel):
    old_password: str = Field(..., description="Old Password")
    password:  str = Field(..., description="New Password")
    password_confirm: str = Field(..., description="Confirm New Password")

    @field_validator('old_password')
    def validate_old_password(cls, v: str) -> str:
        if v is None or v.strip() == "":
            raise ValueError(required('old_password'))
        if len(v) < 8:
            raise ValueError(min_length('old_password', 8))
        if len(v) > 72:
            raise ValueError(max_length('old_password', 72))
        return v

    @field_validator('password')
    def validate_password(cls, v: str) -> str:
        if v is None or v.strip() == "":
            raise ValueError(required('password'))
        if len(v) < 8:
            raise ValueError(min_length('password', 8))
        if len(v) > 72:
            raise ValueError(max_length('password', 72))
        return v

    @field_validator('password_confirm')
    def password_match(cls, v, info: ValidationInfo) -> bool:
        if 'password' in info.data and v != info.data['password']:
            raise ValueError('passwords do not match')
        if v is None or v.strip() == "":
            raise ValueError(required('password_confirm', label='Password confirmation'))
        if len(v) < 8:
            raise ValueError(min_length('password_confirm', 8, label='Password confirmation'))
        if len(v) > 72:
            raise ValueError(max_length('password_confirm', 72, label='Password confirmation'))
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
