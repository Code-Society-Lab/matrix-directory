from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.database import get_session
from app.models.category import Category
from app.routers.category_router import router


def test_list_categories__expect_alphabetical_results(session: Session) -> None:
    session.add_all(
        [
            Category(name="Utility"),
            Category(name="Dev tools"),
        ]
    )
    session.commit()

    app = FastAPI()
    app.include_router(router, prefix="/api")
    app.dependency_overrides[get_session] = lambda: session

    response = TestClient(app).get("/api/categories/")

    assert response.status_code == 200
    assert [category["name"] for category in response.json()] == [
        "Dev tools",
        "Utility",
    ]
