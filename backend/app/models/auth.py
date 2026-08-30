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


class MatrixOAuthCredential(Model, table=True):
    """Encrypted OAuth refresh token used for Matrix media requests."""

    __tablename__ = "matrix_oauth_credentials"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(
        foreign_key="users.id",
        unique=True,
        index=True,
        nullable=False,
    )
    refresh_token_encrypted: str = Field(max_length=4096)

    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
