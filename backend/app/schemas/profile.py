from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from .project import ProjectRead


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


class ProfileUpdate(BaseModel):
    """Schema for updating a user profile."""

    model_config = ConfigDict(extra="forbid")

    display_name: str | None = Field(default=None, max_length=255)
    bio: str | None = Field(default=None, max_length=1024)
    avatar_url: str | None = Field(default=None, max_length=500)
    github_url: str | None = Field(default=None, max_length=500)
    website_url: str | None = Field(default=None, max_length=500)


class ProfileRead(ProfilePublicFields):
    """Profile record returned to the authenticated user."""

    id: UUID


class PublicProfileRead(ProfilePublicFields):
    """Public profile and its published projects."""

    user_id: UUID
    projects: list[ProjectRead]
