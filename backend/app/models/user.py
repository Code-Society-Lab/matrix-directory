from typing import TYPE_CHECKING
from datetime import UTC, datetime

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, Relationship
from sqlmodel_toolkit import Model
from uuid import UUID, uuid4

if TYPE_CHECKING:
    from .project import Project


def utc_now() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


class User(Model, table=True):
    """A user that can own projects."""

    __tablename__ = "users"
    __table_args__ = (UniqueConstraint("oidc_issuer", "oidc_subject"),)

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    matrix_id: str | None = Field(default=None, unique=True, index=True)
    oidc_issuer: str | None = Field(default=None, max_length=255)
    oidc_subject: str | None = Field(default=None, max_length=255)

    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)

    projects: list["Project"] = Relationship(back_populates="owner")
