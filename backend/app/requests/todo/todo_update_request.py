from datetime import datetime
from typing import Optional, Literal
import uuid
from pydantic import BaseModel, Field, ValidationInfo
from pydantic import field_validator
from datetime import timezone

class TodoUpdateRequest(BaseModel):
    title: str = Field(..., min_length=3, max_length=255, description="Title of the todo")
    description: Optional[str] = Field(None, max_length=500, description="Description of the todo")
    priority: Literal["low", "medium", "high"] = Field("low", description="Priority of the todo")
    due_date: Optional[datetime] = Field(None, description="Due date of the todo")

    class Config:
        schema_extra = {
            "example": {
                "title": "Todo title",
                "description": "Todo description",
                "priority": "low",
                "due_date": datetime.now(timezone.utc).isoformat()
            }
        }
    