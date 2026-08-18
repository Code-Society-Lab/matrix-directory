from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ProjectTypeRead(BaseModel):
    """Public representation of a project's primary type."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
