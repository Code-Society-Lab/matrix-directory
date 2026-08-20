from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship
from sqlmodel_toolkit import Model

from app.utils.datetime import utc_now

from .label import Label
from .project_label import ProjectLabel
from .project_type import ProjectType

if TYPE_CHECKING:
    from .user import User


class Project(Model, table=True):
    """A project listed in the Matrix directory."""

    __tablename__ = "projects"

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    name: str = Field(
        max_length=100,
        index=True,
    )

    short_description: str = Field(
        max_length=160,
    )

    description: str = Field(
        max_length=10_000,
    )

    repository_url: str | None = Field(
        default=None,
        max_length=255,
    )
    website_url: str | None = Field(
        default=None,
        max_length=255,
    )
    matrix_server_url: str | None = Field(
        default=None,
        max_length=255,
    )

    user_id: UUID = Field(
        foreign_key="users.id",
        index=True,
    )

    supports_e2ee: bool = Field(default=False)

    project_type_id: UUID = Field(foreign_key="project_types.id", index=True)
    project_type: ProjectType = Relationship(back_populates="projects")

    labels: list[Label] = Relationship(
        back_populates="projects",
        link_model=ProjectLabel,
    )

    owner: "User" = Relationship(
        back_populates="projects",
    )

    created_at: datetime = Field(
        default_factory=utc_now,
    )
    updated_at: datetime = Field(
        default_factory=utc_now,
    )
