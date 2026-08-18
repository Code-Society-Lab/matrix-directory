from uuid import UUID

from sqlmodel import Field
from sqlmodel_toolkit import Model


class ProjectLabel(Model, table=True):
    """Association table between projects and descriptive labels."""

    __tablename__ = "project_labels"

    project_id: UUID = Field(
        foreign_key="projects.id",
        primary_key=True,
        index=True,
    )
    label_id: UUID = Field(
        foreign_key="labels.id",
        primary_key=True,
        index=True,
    )
