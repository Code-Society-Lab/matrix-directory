from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from .category import CategoryRead


class ProjectCreate(BaseModel):
    """Schema for creating a new project."""

    name: str = Field(min_length=2, max_length=100)
    description: str
    short_description: str = Field(max_length=240)

    repository_url: str | None = None
    website_url: str | None = None
    matrix_server_url: str | None = None

    supports_e2ee: bool = False

    category_ids: list[UUID] = Field(min_length=1)


class ProjectUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=100)
    description: str | None = None
    short_description: str | None = Field(default=None, max_length=240)

    repository_url: str | None = None
    website_url: str | None = None
    matrix_server_url: str | None = None

    supports_e2ee: bool | None = None

    category_ids: list[UUID] | None = Field(default=None, min_length=1)

    @field_validator(
        "name",
        "description",
        "short_description",
        "supports_e2ee",
        "category_ids",
        mode="before",
    )
    @classmethod
    def reject_explicit_null(cls, value: Any) -> Any:
        """Reject null for required fields while allowing them to be omitted."""
        if value is None:
            raise ValueError("Field cannot be null")

        return value


class ProjectOwnerRead(BaseModel):
    """Public information about a project owner."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    display_name: str | None = None
    matrix_id: str | None = None
    avatar_url: str | None = None

    @model_validator(mode="before")
    @classmethod
    def from_user(cls, value: Any) -> Any:
        if isinstance(value, dict):
            return value

        profile = getattr(value, "profile", None)

        return {
            "id": value.id,
            "display_name": (profile.display_name if profile is not None else None),
            "matrix_id": (profile.matrix_id if profile is not None else None),
            "avatar_url": (profile.avatar_url if profile is not None else None),
        }


class ProjectRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID

    name: str
    description: str
    short_description: str

    repository_url: str | None
    website_url: str | None
    matrix_server_url: str | None

    supports_e2ee: bool

    user_id: UUID
    owner: ProjectOwnerRead

    categories: list[CategoryRead] = Field(default_factory=list)
