from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, model_validator

from .profile import ProfileRead


class UserRead(BaseModel):
    """Schema for reading a user."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    profile: ProfileRead | None
    project_ids: list[UUID]

    @model_validator(mode="before")
    @classmethod
    def from_user(cls, value: Any) -> Any:
        if isinstance(value, dict):
            return value

        return {
            "id": value.id,
            "profile": value.profile,
            "project_ids": [project.id for project in value.projects],
        }
