"""Testes para o router de estados"""
from fastapi.testclient import TestClient

def test_get_estados(authenticated_client):
    """Testa listagem de estados"""
    response = authenticated_client.get("/estados/")
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_get_estado_by_id(authenticated_client):
    """Testa buscar estado por ID"""
    response = authenticated_client.get("/estados/1")
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    assert response.status_code in [200, 404]  # 200 se existir, 404 se não
