from typing import Any
from uuid import UUID

from pydantic import BaseModel, model_validator

from ..services.avatar import resolve_avatar_url


class ProjectOwnerRead(BaseModel):
    """Public owner fields embedded in a project response."""

    id: UUID
    display_name: str | None = None
    matrix_id: str | None = None
    avatar_url: str | None = None

    @model_validator(mode="before")
    @classmethod
    def from_user(cls, value: Any) -> Any:
        if isinstance(value, dict):
            return value

        profile = getattr(value, "profile", None)
        return {
            "id": value.id,
            "display_name": profile.display_name if profile is not None else None,
            "matrix_id": profile.matrix_id if profile is not None else None,
            "avatar_url": (
                resolve_avatar_url(profile) if profile is not None else None
            ),
        }
