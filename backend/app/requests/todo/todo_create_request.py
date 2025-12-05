from typing import Optional, Literal
import uuid
from pydantic import BaseModel, Field   
from datetime import datetime       
from pydantic import field_validator
from datetime import datetime, timezone
from app.utilis.validation_messages import required, min_length, max_length, future_date

class TodoCreateRequest(BaseModel):
    title: str = Field(..., description="Title of the todo")
    description: Optional[str] = Field(None, description="Description of the todo")
    priority: Literal["low", "medium", "high"] = Field("low", description="Priority of the todo")
    due_date: Optional[datetime] = Field(None, description="Due date of the todo")

    @field_validator("title")
    def validate_title(cls, v: str) -> str:
        if v is None or v.strip() == "":
            raise ValueError(required("title"))
        if len(v) < 3:
            raise ValueError(min_length("title", 3))
        if len(v) > 255:
            raise ValueError(max_length("title", 255))
        return v

    @field_validator("description")
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and len(v) > 500:
            raise ValueError(max_length("description", 500))
        return v

    @field_validator("due_date")
    def validate_due_date(cls, v):
        if v is not None and v <= datetime.now(timezone.utc):
            raise ValueError(future_date("due date"))
        return v

    class Config:
        schema_extra = { 
            "example": {
                "title": "Todo title",
                "description": "Todo description",
                "priority": "low",
                "due_date": datetime.now(timezone.utc).isoformat()
            }
        } 
    