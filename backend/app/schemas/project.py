from pydantic import BaseModel, Field
from uuid import UUID
from .category import CategoryRead


class ProjectCreate(BaseModel):
    """Schema for creating a new project."""

    name: str = Field(min_length=2, max_length=100)
    description: str
    short_description: str = Field(max_length=240)

    repository_url: str | None = None
    website_url: str | None = None
    matrix_server_url: str | None = None

    supports_e2ee: bool = False

    category_ids: list[UUID]


class ProjectUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    short_description: str | None = None

    repository_url: str | None = None
    website_url: str | None = None
    matrix_server_url: str | None = None

    supports_e2ee: bool | None = None

    category_ids: list[UUID] | None = None


class ProjectRead(BaseModel):
    id: UUID

    name: str
    description: str
    short_description: str

    repository_url: str | None
    website_url: str | None
    matrix_server_url: str | None

    supports_e2ee: bool

    user_id: UUID

    categories: list[CategoryRead] = []
