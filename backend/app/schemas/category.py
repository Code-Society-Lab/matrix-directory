from pydantic import BaseModel, Field
from uuid import UUID


class CategoryCreate(BaseModel):
    """Schema for creating a new category."""

    name: str = Field(min_length=2, max_length=100)

    project_ids: list[UUID]


class CategoryRead(BaseModel):
    id: UUID
    name: str
