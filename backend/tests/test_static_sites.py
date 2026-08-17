from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.main import app, mount_static_sites


def test_api_documentation_routes__expect_swagger_and_schema() -> None:
    client = TestClient(app)

    swagger_response = client.get("/api/docs")
    schema_response = client.get("/api/openapi.json")

    assert swagger_response.status_code == 200
    assert "swagger-ui" in swagger_response.text
    assert schema_response.status_code == 200
    assert schema_response.json()["info"]["title"] == "Matrix Directory API"


def test_documentation_static_files__expect_served_under_docs(
    tmp_path: Path,
) -> None:
    static_directory = tmp_path / "static"
    documentation_directory = static_directory / "docs"
    guide_directory = documentation_directory / "guide"
    guide_directory.mkdir(parents=True)
    (documentation_directory / "index.html").write_text(
        "<h1>Documentation home</h1>",
        encoding="utf-8",
    )
    (guide_directory / "index.html").write_text(
        "<h1>Documentation guide</h1>",
        encoding="utf-8",
    )

    application = FastAPI()
    mount_static_sites(application, static_directory)
    client = TestClient(application)

    home_response = client.get("/docs/")
    guide_response = client.get("/docs/guide/")

    assert home_response.status_code == 200
    assert "Documentation home" in home_response.text
    assert guide_response.status_code == 200
    assert "Documentation guide" in guide_response.text


def test_reserved_routes__expect_not_fall_through_to_frontend(
    tmp_path: Path,
) -> None:
    static_directory = tmp_path / "static"
    static_directory.mkdir()
    (static_directory / "index.html").write_text(
        "<h1>Frontend application</h1>",
        encoding="utf-8",
    )

    application = FastAPI()
    mount_static_sites(application, static_directory)
    client = TestClient(application)

    api_response = client.get("/api/not-a-real-route")
    docs_response = client.get("/docs/not-a-real-page")
    frontend_response = client.get("/bots/example")

    assert api_response.status_code == 404
    assert "Frontend application" not in api_response.text
    assert docs_response.status_code == 404
    assert "Frontend application" not in docs_response.text
    assert frontend_response.status_code == 200
    assert "Frontend application" in frontend_response.text
