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
from app.models.label import Label
from app.models.project_type import ProjectType
from app.models.user import User
from app.routers.project_routers import router
from app.schemas.project import ProjectCreate, ProjectUpdate


@dataclass(frozen=True)
class ProjectClient:
    client: TestClient
    user_id: UUID
    project_type_id: UUID
    label_id: UUID


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
    project_type = ProjectType(name="Bot")
    label = Label(name="Utility")

    with Session(engine) as setup_session:
        setup_session.add_all([user, project_type, label])
        setup_session.commit()
        setup_session.refresh(user)
        setup_session.refresh(project_type)
        setup_session.refresh(label)
        user_id = user.id
        project_type_id = project_type.id
        label_id = label.id

    def override_session() -> Generator[Session, None, None]:
        with Session(engine) as session:
            yield session

    def override_current_user() -> User:
        return user

    app.dependency_overrides[get_session] = override_session
    app.dependency_overrides[get_current_user] = override_current_user

    try:
        with TestClient(app) as test_client:
            yield ProjectClient(test_client, user_id, project_type_id, label_id)
    finally:
        engine.dispose()


def test_create_without_project_type__expect_validation_error(
    project_client: ProjectClient,
) -> None:
    response = project_client.client.post(
        "/api/projects/",
        json={
            "name": "Test Bot",
            "description": "A test bot",
            "short_description": "Test bot",
            "label_ids": [],
        },
    )

    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", "project_type_id"]


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
            "project_type_id": str(project_client.project_type_id),
            "label_ids": [str(project_client.label_id)],
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["user_id"] == str(project_client.user_id)
    assert body["project_type"]["id"] == str(project_client.project_type_id)
    assert [label["id"] for label in body["labels"]] == [str(project_client.label_id)]


def test_random_projects__expect_requested_limit_and_total_count(
    project_client: ProjectClient,
) -> None:
    for index in range(3):
        response = project_client.client.post(
            "/api/projects/",
            json={
                "name": f"Test Project {index}",
                "description": "A useful project.",
                "short_description": "Useful project",
                "repository_url": f"https://example.com/project-{index}",
                "project_type_id": str(project_client.project_type_id),
                "label_ids": [],
            },
        )
        assert response.status_code == 201

    random_response = project_client.client.get("/api/projects/random/?limit=2")
    count_response = project_client.client.get("/api/projects/count/")

    assert random_response.status_code == 200
    assert len(random_response.json()) == 2
    assert count_response.status_code == 200
    assert count_response.json() == 3


@pytest.mark.parametrize("limit", [0, 25])
def test_random_projects_with_invalid_limit__expect_validation_error(
    project_client: ProjectClient,
    limit: int,
) -> None:
    response = project_client.client.get(f"/api/projects/random/?limit={limit}")

    assert response.status_code == 422


def test_list_projects__expect_server_side_search_and_filters(
    project_client: ProjectClient,
) -> None:
    for name, labels in [
        ("Alpha Bridge", [str(project_client.label_id)]),
        ("Beta Bot", []),
    ]:
        response = project_client.client.post(
            "/api/projects/",
            json={
                "name": name,
                "description": f"Description for {name}",
                "short_description": name,
                "repository_url": f"https://example.com/{name.lower().replace(' ', '-')}",
                "project_type_id": str(project_client.project_type_id),
                "label_ids": labels,
            },
        )
        assert response.status_code == 201

    response = project_client.client.get(
        "/api/projects/",
        params={
            "q": "alpha",
            "project_type": "Bot",
            "label": "Utility",
            "limit": 24,
        },
    )

    assert response.status_code == 200
    assert [project["name"] for project in response.json()] == ["Alpha Bridge"]


@pytest.mark.parametrize(
    ("project_type_id", "label_ids", "message"),
    [
        (uuid4(), [], "Project type not found"),
        (None, [uuid4()], "Labels not found"),
    ],
)
def test_create_with_unknown_classification__expect_bad_request(
    project_client: ProjectClient,
    project_type_id: UUID | None,
    label_ids: list[UUID],
    message: str,
) -> None:
    response = project_client.client.post(
        "/api/projects/",
        json={
            "name": "Test Bot",
            "description": "A useful bot.",
            "short_description": "Useful bot",
            "repository_url": "https://example.com/test-bot",
            "project_type_id": str(project_type_id or project_client.project_type_id),
            "label_ids": [str(label_id) for label_id in label_ids],
        },
    )

    assert response.status_code == 400
    assert message in response.json()["detail"]


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
        "project_type_id",
        "label_ids",
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
        project_type_id=uuid4(),
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
        "project_type_id": uuid4(),
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
            project_type_id=uuid4(),
        )


def test_create_with_overlong_url__expect_validation_error() -> None:
    url = "https://example.com/" + "x" * 236

    with pytest.raises(ValidationError):
        ProjectCreate(
            name="Test Bot",
            description="A useful bot.",
            short_description="Useful bot",
            repository_url=url,
            project_type_id=uuid4(),
        )


def test_create_with_blank_optional_url__expect_null() -> None:
    project = ProjectCreate(
        name="Test Bot",
        description="A useful bot.",
        short_description="Useful bot",
        repository_url="https://example.com/test-bot",
        website_url="   ",
        project_type_id=uuid4(),
    )

    assert project.website_url is None


def test_create_with_duplicate_labels__expect_validation_error() -> None:
    label_id = uuid4()

    with pytest.raises(ValidationError, match="Labels must be unique"):
        ProjectCreate(
            name="Test Bot",
            description="A useful bot.",
            short_description="Useful bot",
            project_type_id=uuid4(),
            label_ids=[label_id, label_id],
        )
