from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from .project import ProjectRead
from ..models.profile import Profile
from ..services.avatar import matrix_avatar_url, resolve_avatar_url
from ..utils.validators import normalize_optional_http_url


class ProfilePublicFields(BaseModel):
    """Profile fields that are safe to expose publicly."""

    model_config = ConfigDict(from_attributes=True)

    matrix_id: str
    matrix_id_verified: bool = False
    display_name: str | None = None
    bio: str | None = None
    avatar_url: str | None = None
    github_url: str | None = None
    website_url: str | None = None

    @model_validator(mode="before")
    @classmethod
    def resolve_avatar(cls, value: Any) -> Any:
        """Expose one avatar URL, whether it is custom or the Matrix proxy."""
        if isinstance(value, dict) or not isinstance(value, Profile):
            return value

        return {
            **{name: getattr(value, name) for name in Profile.model_fields},
            "avatar_url": resolve_avatar_url(value),
            "custom_avatar_url": value.avatar_url,
            "matrix_avatar_url": matrix_avatar_url(value),
        }


class ProfileUpdate(BaseModel):
    """Schema for updating a user profile."""

    model_config = ConfigDict(extra="forbid")

    display_name: str | None = Field(default=None, max_length=255)
    bio: str | None = Field(default=None, max_length=1024)
    avatar_url: str | None = Field(default=None, max_length=500)
    github_url: str | None = Field(default=None, max_length=500)
    website_url: str | None = Field(default=None, max_length=500)

    @field_validator(
        "avatar_url",
        "github_url",
        "website_url",
        mode="before",
    )
    @classmethod
    def validate_optional_urls(cls, value: Any) -> Any:
        """Keep stored profile links to absolute HTTP(S) URLs, as projects are."""
        return normalize_optional_http_url(value)


class ProfileRead(ProfilePublicFields):
    """Profile record returned to the authenticated user."""

    id: UUID

    custom_avatar_url: str | None = None
    matrix_avatar_url: str | None = None


class PublicProfileRead(ProfilePublicFields):
    """Public profile and its published projects."""

    user_id: UUID
    projects: list[ProjectRead]
