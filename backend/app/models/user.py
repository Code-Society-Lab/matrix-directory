from typing import TYPE_CHECKING
from datetime import UTC, datetime

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

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    matrix_id: str = Field(unique=True, index=True)

    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)

    projects: list["Project"] = Relationship(back_populates="owner")
