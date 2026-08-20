from datetime import datetime
from uuid import UUID, uuid4

from sqlmodel import Field
from sqlmodel_toolkit import Model

from ..utils.datetime import utc_now


class AuthSession(Model, table=True):
    """An application session created after Matrix identity verification."""

    __tablename__ = "auth_sessions"

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    token_hash: str = Field(unique=True, index=True, max_length=64)
    user_id: UUID = Field(foreign_key="users.id", index=True)

    expires_at: datetime
    created_at: datetime = Field(default_factory=utc_now)
