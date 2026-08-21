from fastapi.testclient import TestClient

from api.main import app


client = TestClient(app)


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "running"


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_companies():
    response = client.get("/companies")
    assert response.status_code == 200
    assert "companies" in response.json()


def test_top_performers():
    response = client.get("/top-performers")
    assert response.status_code == 200
    assert "results" in response.json()