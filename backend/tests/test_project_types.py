from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.database import get_session
from app.models.project_type import ProjectType
from app.routers.project_type_router import router


def test_list_project_types__expect_alphabetical_results(session: Session) -> None:
    session.add_all(
        [
            ProjectType(name="SDK"),
            ProjectType(name="Bot"),
        ]
    )
    session.commit()

    app = FastAPI()
    app.include_router(router, prefix="/api")
    app.dependency_overrides[get_session] = lambda: session
    client = TestClient(app)

    response = client.get("/api/project-types/")

    assert response.status_code == 200
    assert [item["name"] for item in response.json()] == ["Bot", "SDK"]
