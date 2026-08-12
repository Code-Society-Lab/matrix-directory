from fastapi.testclient import TestClient

from app.main import app


def test_health_call_with_success__expect_status_returned() -> None:
    response = TestClient(app).get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
