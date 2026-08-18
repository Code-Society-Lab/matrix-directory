from uuid import UUID

from pydantic import BaseModel, ConfigDict


class LabelRead(BaseModel):
    """Public representation of a descriptive project label."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
