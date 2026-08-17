from collections.abc import Generator
from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import ValidationError
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.database import get_session
from app.dependencies import get_current_user
from app.models.user import User
from app.routers.project_routers import router
from app.schemas.project import ProjectUpdate


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)

    app = FastAPI()
    app.include_router(router, prefix="/api")
    user = User(oidc_issuer="issuer", oidc_subject="owner")

    def override_session() -> Generator[Session, None, None]:
        with Session(engine) as session:
            yield session

    def override_current_user() -> User:
        return user

    app.dependency_overrides[get_session] = override_session
    app.dependency_overrides[get_current_user] = override_current_user

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        engine.dispose()


def test_create_with_no_categories__expect_validation_error(
    client: TestClient,
) -> None:
    response = client.post(
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


def test_update_with_no_categories__expect_validation_error(
    client: TestClient,
) -> None:
    response = client.patch(
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
