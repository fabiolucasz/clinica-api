from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


def test_root():
    """Testa endpoint raiz"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert data["message"] == "Welcome to the Clinica API"
