from datetime import UTC, datetime

from sqlmodel import Field, Relationship
from sqlmodel_toolkit import Model
from .project import Project, ProjectCategory
from uuid import UUID, uuid4


def utc_now() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


class Category(Model, table=True):
    """A category that a project can belong to."""

    __tablename__ = "categories"

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    name: str = Field(unique=True, index=True)

    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)

    projects: list[Project] = Relationship(
        back_populates="categories",
        link_model=ProjectCategory,
    )
