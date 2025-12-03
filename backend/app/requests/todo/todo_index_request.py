from pydantic import BaseModel, Field, field_validator
from typing import Optional, Literal
import uuid
from app.utilis.validation_messages import greater_than, at_most, max_length

class TodoIndexRequest(BaseModel):
    page: Optional[int] = 1
    page_size: Optional[int] = 20
    search: Optional[str] = None
    completed: Optional[bool] = None
    due_date: Optional[str] = None
    # make priority optional so it only filters when explicitly provided
    priority: Optional[Literal["low", "medium", "high"]] = Field(
        None, description="Priority of the todo"
    )

    @field_validator("page")
    def validate_page(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and v <= 0:
            raise ValueError(greater_than("page", 0))
        return v

    @field_validator("page_size")
    def validate_page_size(cls, v: Optional[int]) -> Optional[int]:
        if v is not None:
            if v <= 0:
                raise ValueError(greater_than("page_size", 0))
            if v > 100:
                raise ValueError(at_most("page_size", 100))
        return v

    @field_validator("search")
    def validate_search(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and len(v) > 255:
            raise ValueError(max_length("search", 255))
        return v

    class Config:
        schema_extra = {
            "example": {
                "page": 1,
                "page_size": 20,
                "search": "test",
                "completed": False,
                "due_date": "2022-01-01",
                "priority": "low"
            }
        }