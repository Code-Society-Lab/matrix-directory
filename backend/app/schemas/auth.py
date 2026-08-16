from uuid import UUID

from pydantic import BaseModel, ConfigDict

from .profile import ProfileRead


class CurrentUserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    profile: ProfileRead | None
