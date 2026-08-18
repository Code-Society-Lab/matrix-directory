from collections.abc import Generator
from dataclasses import dataclass
from uuid import UUID
from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import ValidationError
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.database import get_session
from app.dependencies import get_current_user
from app.models.category import Category
from app.models.user import User
from app.routers.project_routers import router
from app.schemas.project import ProjectCreate, ProjectUpdate


@dataclass(frozen=True)
class ProjectClient:
    client: TestClient
    user_id: UUID
    category_id: UUID


@pytest.fixture
def project_client() -> Generator[ProjectClient, None, None]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)

    app = FastAPI()
    app.include_router(router, prefix="/api")
    user = User(oidc_issuer="issuer", oidc_subject="owner")
    category = Category(name="Bots")

    with Session(engine) as setup_session:
        setup_session.add_all([user, category])
        setup_session.commit()
        setup_session.refresh(user)
        setup_session.refresh(category)
        user_id = user.id
        category_id = category.id

    def override_session() -> Generator[Session, None, None]:
        with Session(engine) as session:
            yield session

    def override_current_user() -> User:
        return user

    app.dependency_overrides[get_session] = override_session
    app.dependency_overrides[get_current_user] = override_current_user

    try:
        with TestClient(app) as test_client:
            yield ProjectClient(test_client, user_id, category_id)
    finally:
        engine.dispose()


def test_create_with_no_categories__expect_validation_error(
    project_client: ProjectClient,
) -> None:
    response = project_client.client.post(
        "/api/projects/",
        json={
            "name": "Test Bot",
            "description": "A test bot",
            "short_description": "Test bot",
            "category_ids": [],
        },
    )

    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", "category_ids"]


def test_create__expect_project_associated_with_authenticated_user(
    project_client: ProjectClient,
) -> None:
    response = project_client.client.post(
        "/api/projects/",
        json={
            "name": "Test Bot",
            "description": "A useful bot.",
            "short_description": "Useful bot",
            "repository_url": "https://example.com/test-bot",
            "category_ids": [str(project_client.category_id)],
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["user_id"] == str(project_client.user_id)
    assert [category["id"] for category in body["categories"]] == [
        str(project_client.category_id)
    ]


def test_update_with_no_categories__expect_validation_error(
    project_client: ProjectClient,
) -> None:
    response = project_client.client.patch(
        f"/api/projects/{uuid4()}",
        json={"category_ids": []},
    )

    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", "category_ids"]


@pytest.mark.parametrize(
    "update",
    [
        {"name": "x"},
        {"name": "x" * 101},
        {"short_description": "x" * 241},
    ],
)
def test_update_with_invalid_text__expect_validation_error(
    update: dict[str, str],
) -> None:
    with pytest.raises(ValidationError):
        ProjectUpdate.model_validate(update)


@pytest.mark.parametrize(
    "field",
    [
        "name",
        "description",
        "short_description",
        "supports_e2ee",
        "category_ids",
    ],
)
def test_update_with_null_required_field__expect_validation_error(field: str) -> None:
    with pytest.raises(ValidationError, match="cannot be null") as error:
        ProjectUpdate.model_validate({field: None})

    assert error.value.errors()[0]["loc"] == (field,)


def test_update_with_omitted_fields__expect_only_supplied_fields_set() -> None:
    update = ProjectUpdate(name="Renamed Bot")

    assert update.model_dump(exclude_unset=True) == {"name": "Renamed Bot"}


def test_create__expect_required_text_trimmed() -> None:
    project = ProjectCreate(
        name="  Test Bot  ",
        description="  A useful bot.  ",
        short_description="  Useful bot  ",
        repository_url="https://example.com/test-bot",
        category_ids=[uuid4()],
    )

    assert project.name == "Test Bot"
    assert project.description == "A useful bot."
    assert project.short_description == "Useful bot"


@pytest.mark.parametrize(
    "field",
    ["name", "description", "short_description"],
)
def test_create_with_whitespace_only_text__expect_validation_error(
    field: str,
) -> None:
    data = {
        "name": "Test Bot",
        "description": "A useful bot.",
        "short_description": "Useful bot",
        "category_ids": [uuid4()],
    }
    data[field] = "   "

    with pytest.raises(ValidationError):
        ProjectCreate.model_validate(data)


@pytest.mark.parametrize(
    "url",
    ["matrix:roomid/example.org", "/relative", "javascript:alert(1)"],
)
def test_create_with_invalid_url__expect_validation_error(url: str) -> None:
    with pytest.raises(ValidationError, match="absolute HTTP or HTTPS URL"):
        ProjectCreate(
            name="Test Bot",
            description="A useful bot.",
            short_description="Useful bot",
            repository_url=url,
            category_ids=[uuid4()],
        )


def test_create_with_overlong_url__expect_validation_error() -> None:
    url = "https://example.com/" + "x" * 236

    with pytest.raises(ValidationError):
        ProjectCreate(
            name="Test Bot",
            description="A useful bot.",
            short_description="Useful bot",
            repository_url=url,
            category_ids=[uuid4()],
        )


def test_create_with_blank_optional_url__expect_null() -> None:
    project = ProjectCreate(
        name="Test Bot",
        description="A useful bot.",
        short_description="Useful bot",
        repository_url="https://example.com/test-bot",
        website_url="   ",
        category_ids=[uuid4()],
    )

    assert project.website_url is None


def test_create_with_duplicate_categories__expect_validation_error() -> None:
    category_id = uuid4()

    with pytest.raises(ValidationError, match="Categories must be unique"):
        ProjectCreate(
            name="Test Bot",
            description="A useful bot.",
            short_description="Useful bot",
            category_ids=[category_id, category_id],
        )
