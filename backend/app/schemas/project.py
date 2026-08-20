from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)

from .label import LabelRead
from .project_owner import ProjectOwnerRead
from .project_type import ProjectTypeRead
from ..utils.validators import normalize_optional_http_url


class ProjectFilters(BaseModel):
    """Optional filters shared by project listing and counting endpoints."""

    q: str | None = Field(default=None, max_length=200)
    project_type: str | None = Field(default=None, max_length=100)
    label: str | None = Field(default=None, max_length=100)


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

    project_type_id: UUID
    label_ids: list[UUID] = Field(default_factory=list)

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

    @field_validator("label_ids")
    @classmethod
    def reject_duplicate_labels(
        cls,
        value: list[UUID],
    ) -> list[UUID]:
        if len(value) != len(set(value)):
            raise ValueError("Labels must be unique")

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

    project_type_id: UUID | None = None
    label_ids: list[UUID] | None = None

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

    @field_validator("label_ids")
    @classmethod
    def reject_duplicate_labels(
        cls,
        value: list[UUID] | None,
    ) -> list[UUID] | None:
        if value is not None and len(value) != len(set(value)):
            raise ValueError("Labels must be unique")

        return value

    @field_validator(
        "name",
        "short_description",
        "description",
        "supports_e2ee",
        "project_type_id",
        "label_ids",
        mode="before",
    )
    @classmethod
    def reject_explicit_null(cls, value: Any) -> Any:
        """Reject null for required fields while allowing omission."""
        if value is None:
            raise ValueError("Field cannot be null")

        return value


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

    project_type: ProjectTypeRead
    labels: list[LabelRead] = Field(default_factory=list)

    user_id: UUID
    owner: ProjectOwnerRead

    created_at: datetime
    updated_at: datetime
