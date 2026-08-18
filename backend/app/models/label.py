from datetime import UTC, datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship
from sqlmodel_toolkit import Model

from .project_label import ProjectLabel

if TYPE_CHECKING:
    from .project import Project


def utc_now() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


class Label(Model, table=True):
    """A descriptive label that may be assigned to many projects."""

    __tablename__ = "labels"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(max_length=100, unique=True, index=True)

    projects: list["Project"] = Relationship(
        back_populates="labels",
        link_model=ProjectLabel,
    )

    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
