from datetime import datetime
from typing import Any
from urllib.parse import urlsplit
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)

from .category import CategoryRead


def normalize_optional_http_url(value: Any) -> Any:
    """Normalize blank URLs and reject non-HTTP(S) or relative URLs."""
    if value is None:
        return None

    if not isinstance(value, str):
        return value

    value = value.strip()
    if not value:
        return None

    parsed = urlsplit(value)

    if parsed.scheme not in {"http", "https"} or parsed.hostname is None:
        raise ValueError("Must be an absolute HTTP or HTTPS URL")

    return value


class ProjectCreate(BaseModel):
    """Schema for creating a new project."""

    name: str = Field(
        min_length=2,
        max_length=100,
    )
    short_description: str = Field(
        min_length=1,
        max_length=160,
    )
    description: str = Field(
        min_length=1,
        max_length=10_000,
    )

    repository_url: str | None = Field(default=None, max_length=255)
    website_url: str | None = Field(default=None, max_length=255)
    matrix_server_url: str | None = Field(default=None, max_length=255)

    supports_e2ee: bool = False

    category_ids: list[UUID] = Field(min_length=1)

    @field_validator(
        "name",
        "short_description",
        "description",
        mode="before",
    )
    @classmethod
    def strip_required_text(cls, value: Any) -> Any:
        if isinstance(value, str):
            return value.strip()

        return value

    @field_validator(
        "repository_url",
        "website_url",
        "matrix_server_url",
        mode="before",
    )
    @classmethod
    def validate_optional_urls(cls, value: Any) -> Any:
        return normalize_optional_http_url(value)

    @field_validator("category_ids")
    @classmethod
    def reject_duplicate_categories(
        cls,
        value: list[UUID],
    ) -> list[UUID]:
        if len(value) != len(set(value)):
            raise ValueError("Categories must be unique")

        return value

    @model_validator(mode="after")
    def require_project_link(self) -> "ProjectCreate":
        """Require somewhere users can learn more about the project."""
        if self.repository_url is None and self.website_url is None:
            raise ValueError("Provide at least a repository URL or website URL")

        return self


class ProjectUpdate(BaseModel):
    """Schema for partially updating a project."""

    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
    )
    short_description: str | None = Field(
        default=None,
        min_length=1,
        max_length=160,
    )
    description: str | None = Field(
        default=None,
        min_length=1,
        max_length=10_000,
    )

    repository_url: str | None = Field(default=None, max_length=255)
    website_url: str | None = Field(default=None, max_length=255)
    matrix_server_url: str | None = Field(default=None, max_length=255)

    supports_e2ee: bool | None = None

    category_ids: list[UUID] | None = Field(
        default=None,
        min_length=1,
    )

    @field_validator(
        "name",
        "short_description",
        "description",
        mode="before",
    )
    @classmethod
    def strip_updated_text(cls, value: Any) -> Any:
        if isinstance(value, str):
            return value.strip()

        return value

    @field_validator(
        "repository_url",
        "website_url",
        "matrix_server_url",
        mode="before",
    )
    @classmethod
    def validate_optional_urls(cls, value: Any) -> Any:
        return normalize_optional_http_url(value)

    @field_validator("category_ids")
    @classmethod
    def reject_duplicate_categories(
        cls,
        value: list[UUID] | None,
    ) -> list[UUID] | None:
        if value is not None and len(value) != len(set(value)):
            raise ValueError("Categories must be unique")

        return value

    @field_validator(
        "name",
        "short_description",
        "description",
        "supports_e2ee",
        "category_ids",
        mode="before",
    )
    @classmethod
    def reject_explicit_null(cls, value: Any) -> Any:
        """Reject null for required fields while allowing omission."""
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
    """Public representation of a directory project."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID

    name: str
    short_description: str
    description: str

    repository_url: str | None
    website_url: str | None
    matrix_server_url: str | None

    supports_e2ee: bool

    user_id: UUID
    owner: ProjectOwnerRead

    categories: list[CategoryRead] = Field(default_factory=list)

    created_at: datetime
    updated_at: datetime
