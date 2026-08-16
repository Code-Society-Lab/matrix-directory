from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ProfileUpdate(BaseModel):
    """Schema for updating a user profile."""

    matrix_id: str | None = Field(default=None, max_length=255)
    display_name: str | None = Field(default=None, max_length=255)
    bio: str | None = Field(default=None, max_length=1024)
    avatar_url: str | None = Field(default=None, max_length=500)
    github_url: str | None = Field(default=None, max_length=500)
    website_url: str | None = Field(default=None, max_length=500)


class ProfileRead(BaseModel):
    """Schema for reading a user profile."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    matrix_id: str | None
    matrix_id_verified: bool
    display_name: str | None
    bio: str | None
    avatar_url: str | None
    github_url: str | None
    website_url: str | None
