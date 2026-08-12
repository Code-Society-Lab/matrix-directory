from pydantic import BaseModel, Field
from uuid import UUID


class UserCreate(BaseModel):
    """Schema for creating a new user."""

    matrix_id: str
    project_ids: list[UUID]


class UserRead(BaseModel):
    """Schema for reading a user."""

    id: UUID
    matrix_id: str
    project_ids: list[UUID]
