from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.database import get_session
from app.models.label import Label
from app.routers.label_router import router


def test_list_labels__expect_alphabetical_results(session: Session) -> None:
    session.add_all(
        [
            Label(name="Utility"),
            Label(name="Dev tools"),
        ]
    )
    session.commit()

    app = FastAPI()
    app.include_router(router, prefix="/api")
    app.dependency_overrides[get_session] = lambda: session
    client = TestClient(app)

    response = client.get("/api/labels/")

    assert response.status_code == 200
    assert [item["name"] for item in response.json()] == ["Dev tools", "Utility"]
