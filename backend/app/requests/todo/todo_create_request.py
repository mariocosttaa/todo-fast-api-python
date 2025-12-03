from typing import Optional, Literal
import uuid
from pydantic import BaseModel, Field   
from datetime import datetime       
from pydantic import field_validator
from datetime import datetime, timezone

class TodoCreateRequest(BaseModel):
    title: str = Field(..., min_length=3, max_length=255, description="Title of the todo")
    description: Optional[str] = Field(None, max_length=500, description="Description of the todo")
    priority: Literal["low", "medium", "high"] = Field("low", description="Priority of the todo")
    due_date: Optional[datetime] = Field(None, description="Due date of the todo")

    @field_validator("due_date")
    def validate_due_date(cls, v):
        if v is not None and v <= datetime.now(timezone.utc):
            raise ValueError("Due date must be in the future")
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
    