"""Testes para o router de clinicas"""
from fastapi.testclient import TestClient

def test_get_clinicas(authenticated_client):
    """Testa listagem de clinicas"""
    response = authenticated_client.get("/clinicas/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_get_clinica_by_id(authenticated_client):
    """Testa buscar clinica por ID"""
    response = authenticated_client.get("/clinicas/1")
    assert response.status_code in [200, 404]
