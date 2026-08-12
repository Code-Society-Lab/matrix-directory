from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship
from sqlmodel_toolkit import Model
from uuid import UUID, uuid4

if TYPE_CHECKING:
    from .category import Category
    from .user import User


def utc_now() -> datetime:
    """Return the current UTC time without timezone information."""
    return datetime.now(UTC).replace(tzinfo=None)


class ProjectCategory(Model, table=True):
    """Association table between projects and categories."""

    __tablename__ = "project_categories"

    project_id: UUID = Field(foreign_key="projects.id", primary_key=True, index=True)
    category_id: UUID = Field(foreign_key="categories.id", primary_key=True, index=True)


class Project(Model, table=True):
    """A project that can be listed in the directory."""

    __tablename__ = "projects"

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    name: str = Field(max_length=100, index=True)
    description: str
    short_description: str = Field(max_length=240)

    repository_url: str | None = None
    website_url: str | None = None
    matrix_server_url: str | None = None

    user_id: UUID = Field(foreign_key="users.id", index=True)

    supports_e2ee: bool = False

    owner: "User" = Relationship(back_populates="projects")

    categories: list["Category"] = Relationship(
        back_populates="projects",
        link_model=ProjectCategory,
    )

    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
