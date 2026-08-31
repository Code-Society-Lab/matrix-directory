from datetime import datetime
from typing import TYPE_CHECKING, Optional
from uuid import UUID, uuid4

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, Relationship
from sqlmodel_toolkit import Model

from ..utils.datetime import utc_now

if TYPE_CHECKING:
    from .profile import Profile
    from .project import Project


class User(Model, table=True):
    """Authenticated user account."""

    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint(
            "oidc_issuer",
            "oidc_subject",
            name="uq_users_oidc_identity",
        ),
    )

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    oidc_issuer: str = Field(max_length=255)
    oidc_subject: str = Field(max_length=255)

    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)

    profile: Optional["Profile"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={
            "uselist": False,
            "cascade": "all, delete-orphan",
        },
    )

    projects: list["Project"] = Relationship(
        back_populates="owner",
    )
