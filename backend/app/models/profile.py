from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship
from sqlmodel_toolkit import Model

from ..utils.datetime import utc_now

if TYPE_CHECKING:
    from .user import User


class Profile(Model, table=True):
    """Public profile associated with a user account."""

    __tablename__ = "profiles"

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    user_id: UUID = Field(
        foreign_key="users.id",
        unique=True,
        index=True,
        nullable=False,
    )

    matrix_id: str = Field(
        unique=True,
        index=True,
    )
    matrix_id_verified: bool = Field(default=False)
    matrix_avatar_mxc: str | None = Field(default=None, max_length=500)

    display_name: str | None = Field(default=None, max_length=100)
    bio: str | None = Field(default=None, max_length=1024)
    avatar_url: str | None = Field(default=None, max_length=500)

    github_url: str | None = Field(default=None, max_length=150)
    website_url: str | None = Field(default=None, max_length=150)

    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)

    user: "User" = Relationship(back_populates="profile")
