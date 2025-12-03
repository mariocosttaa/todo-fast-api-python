from pydantic import BaseModel
from typing import Optional, Literal
import uuid
from pydantic import BaseModel, Field

class TodoIndexRequest(BaseModel):
    page: Optional[int] = 1
    page_size: Optional[int] = 20
    search: Optional[str] = None
    completed: Optional[bool] = None
    active: Optional[bool] = None
    due_date: Optional[str] = None
    priority: Literal["low", "medium", "high"] = Field("low", description="Priority of the todo")
    
    class Config:
        schema_extra = {
            "example": {
                "page": 1,
                "page_size": 20,
                "search": "test",
                "completed": False,
                "active": True,
                "due_date": "2022-01-01",
                "priority": "low"
            }
        }